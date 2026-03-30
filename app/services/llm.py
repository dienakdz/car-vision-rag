from __future__ import annotations

import json
import re
import unicodedata
from urllib import error, request
from urllib.parse import quote

from app.core.config import (
    LLM_API_BASE,
    LLM_API_KEY,
    LLM_CONTEXT_CHARS,
    LLM_CONTEXT_DOCS,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_TIMEOUT_SEC,
)


def _build_prediction_context(prediction: dict | None) -> str:
    if not prediction:
        return "Khong co thong tin phan tich anh gan nhat."

    label = prediction.get("predicted_label")
    confidence = prediction.get("confidence")

    if not label:
        return "Anh gan nhat chua co nhan body type ro rang."

    if confidence is None:
        return f"Body type gan nhat: {label}."

    return f"Body type gan nhat: {label} (confidence: {round(float(confidence) * 100, 2)}%)."


def _build_source_context(docs: list[dict]) -> str:
    blocks = []
    for idx, doc in enumerate(docs[:LLM_CONTEXT_DOCS], start=1):
        text = _normalize_whitespace(doc.get("text") or "")
        if not text:
            continue

        text = text[:LLM_CONTEXT_CHARS]
        source_file = doc.get("source_file") or "unknown"
        page = doc.get("page")
        kb_type = doc.get("kb_type") or "unknown"
        body_type = doc.get("body_type") or "unknown"

        blocks.append(
            f"[{idx}] source_file={source_file}; page={page}; kb_type={kb_type}; body_type={body_type}\n{text}"
        )

    if not blocks:
        return "Khong co doan tai lieu truy hoi phu hop."

    return "\n\n".join(blocks)


def _classify_answer_style(message: str) -> str:
    msg = message.lower()

    short_markers = (
        "ngan gon",
        "tom tat",
        "1 cau",
        "2 cau",
        "brief",
    )
    compare_markers = (
        "so sanh",
        "vs",
        "khac nhau",
        "khac gi",
        "uu nhuoc",
    )
    advise_markers = (
        "co nen",
        "tu van",
        "goi y",
        "chon",
        "hop khong",
    )

    if any(m in msg for m in short_markers):
        return "compact"
    if any(m in msg for m in compare_markers):
        return "comparison"
    if any(m in msg for m in advise_markers):
        return "advisory"
    return "standard"


def _build_style_instruction(style: str, intent: str) -> str:
    base = [
        "Tra loi tieng Viet tu nhien, ro y, khong chung chung.",
        "Cau dau phai tra loi truc tiep vao cau hoi.",
        "Moi y quan trong nen gan citation [1], [2] neu lay tu context.",
        "Chi dung citation [n] o cuoi cau; khong tao dong bat dau bang 'Tham khao [n]:'.",
        "Neu thieu du lieu, noi ro thieu gi va dat 1 cau hoi tiep theo.",
        "Khong sao chep nguyen van doan context; phai dien giai lai bang ngon ngu tu nhien.",
    ]

    if intent == "vehicle":
        base.append("Neu co body type tu anh gan nhat, lien ket ngan gon voi cau hoi cua user.")

    if style == "compact":
        base.append("Do dai: 2-3 cau, ngan gon.")
    elif style == "comparison":
        base.append("Do dai: 6-9 cau.")
        base.append("Format bat buoc: Khac biet chinh -> Uu diem/Nhuoc diem -> Goi y theo nhu cau.")
    elif style == "advisory":
        base.append("Do dai: 6-8 cau.")
        base.append("Can co 2-3 goi y hanh dong cu the cho user.")
    else:
        base.append("Do dai: 5-8 cau.")
        base.append("Khong tra loi qua ngan (tranh 1-2 cau) neu user khong yeu cau ngan.")

    return "\n".join(f"- {x}" for x in base)


def _build_prompts(message: str, prediction: dict | None, docs: list[dict], intent: str) -> tuple[str, str, str]:
    style = _classify_answer_style(message)

    system_prompt = (
        "Ban la tro ly tu van o to cho showroom.\n"
        "Chi duoc dung du lieu trong context duoc cung cap, khong tu suy doan thong tin ngoai context.\n"
        "Uu tien tra loi huu ich, cu the, co logic va de hanh dong.\n"
        f"Quy tac tra loi:\n{_build_style_instruction(style, intent)}"
    )

    user_prompt = (
        f"Intent hien tai: {intent}\n"
        f"Thong tin anh gan nhat: {_build_prediction_context(prediction)}\n\n"
        f"Cau hoi nguoi dung: {message}\n\n"
        "Context tai lieu truy hoi:\n"
        f"{_build_source_context(docs)}\n\n"
        "Hay tra loi theo dung quy tac o tren."
    )

    return system_prompt, user_prompt, style


def _send_json(url: str, payload: dict) -> tuple[dict | None, dict | None]:
    headers = {"Content-Type": "application/json"}

    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=LLM_TIMEOUT_SEC) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body), None
    except error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        return None, {
            "mode": "fallback",
            "reason": f"gemini_http_error_{exc.code}",
            "error": err_body[:500],
            "model": LLM_MODEL,
            "api_base": LLM_API_BASE,
            "style": "gemini",
        }
    except Exception as exc:
        return None, {
            "mode": "fallback",
            "reason": "gemini_request_failed",
            "error": str(exc),
            "model": LLM_MODEL,
            "api_base": LLM_API_BASE,
            "style": "gemini",
        }


def _extract_gemini_text(data: dict) -> tuple[str, str | None]:
    candidates = data.get("candidates") or []
    if not candidates:
        return "", "gemini_empty_candidates"

    first = candidates[0]
    parts = ((first.get("content") or {}).get("parts") or [])

    texts = []
    for part in parts:
        if isinstance(part, dict):
            text = (part.get("text") or "").strip()
            if text:
                texts.append(text)

    content = "\n".join(texts).strip()
    if content:
        return content, None

    finish_reason = (first.get("finishReason") or "empty_content").lower()
    return "", f"gemini_empty_content_{finish_reason}"


def _sentence_count(text: str) -> int:
    parts = re.split(r"[.!?]+", text)
    return len([p for p in parts if p.strip()])


def _normalize_whitespace(text: str) -> str:
    return " ".join((text or "").strip().split())


def _ascii_fold(text: str) -> str:
    return unicodedata.normalize("NFD", text or "").encode("ascii", "ignore").decode("ascii")


def _tokenize_words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", _ascii_fold(text).lower())


def _contains_context_copy(answer: str, docs: list[dict], ngram_words: int = 11) -> bool:
    answer_tokens = _tokenize_words(answer)
    if len(answer_tokens) < ngram_words:
        return False

    answer_ngrams = {
        " ".join(answer_tokens[i : i + ngram_words])
        for i in range(len(answer_tokens) - ngram_words + 1)
    }

    for doc in docs[:LLM_CONTEXT_DOCS]:
        text = (doc.get("text") or "")[: LLM_CONTEXT_CHARS * 2]
        doc_tokens = _tokenize_words(text)
        if len(doc_tokens) < ngram_words:
            continue

        for i in range(len(doc_tokens) - ngram_words + 1):
            gram = " ".join(doc_tokens[i : i + ngram_words])
            if gram in answer_ngrams:
                return True

    return False


def _strip_reference_dump(content: str) -> str:
    kept_lines: list[str] = []
    for line in (content or "").splitlines():
        folded = _ascii_fold(line).strip().lower()
        if re.match(r"^tham\s*khao\s*\[\d+\]\s*:", folded):
            continue
        kept_lines.append(line)

    merged = "\n".join(kept_lines).strip()
    merged = re.sub(r"\n{3,}", "\n\n", merged)
    return merged


def _should_expand_answer(content: str, style: str) -> bool:
    if style == "compact":
        return False
    if len(content) < 170:
        return True
    return _sentence_count(content) < 4


def _followup_by_intent(intent: str) -> str:
    if intent == "vehicle":
        return "Ban uu tien su em ai, khong gian, hay chi phi su dung de minh goi y sat hon?"
    if intent == "company":
        return "Ban can minh chi tiet them ve quy trinh mua xe, ho tro tra gop, hay test drive?"
    return "Ban muon minh mo rong theo huong so sanh, tu van nhu cau, hay quy trinh mua xe?"


def _build_source_refs(docs: list[dict], max_refs: int = 3) -> str:
    refs = []
    for idx, doc in enumerate(docs[:max_refs], start=1):
        source = doc.get("source_file") or "unknown"
        page = doc.get("page")
        if page is None:
            refs.append(f"[{idx}] {source}")
        else:
            refs.append(f"[{idx}] {source} (trang {page})")
    if not refs:
        return ""
    return "Nguon tham khao: " + "; ".join(refs) + "."


def _enrich_if_still_short(
    content: str,
    style: str,
    prediction: dict | None,
    docs: list[dict],
    intent: str,
) -> str:
    if style == "compact":
        return content
    if _sentence_count(content) >= 4 and len(content) >= 170:
        return content

    extras: list[str] = []
    label = (prediction or {}).get("predicted_label")
    confidence = (prediction or {}).get("confidence")
    if label and confidence is not None:
        extras.append(
            f"Ngoai ra, he thong dang nghieng ve body type '{label}' voi do tin cay {round(float(confidence) * 100, 2)}%."
        )

    source_refs = _build_source_refs(docs)
    if source_refs:
        extras.append(source_refs)

    extras.append(_followup_by_intent(intent))

    if not extras:
        return content
    return f"{content}\n\n" + "\n".join(extras)


def _build_expand_payload(
    original_answer: str,
    message: str,
    prediction: dict | None,
    docs: list[dict],
    intent: str,
    style: str,
) -> dict:
    system_prompt = (
        "Ban la tro ly tu van o to. Nhiem vu: viet lai cau tra loi cho day du hon, "
        "nhung van dung du lieu context, khong them thong tin ngoai context, "
        "va khong sao chep nguyen van doan tai lieu."
    )
    user_prompt = (
        f"Cau hoi user: {message}\n"
        f"Intent: {intent}\n"
        f"Body type tu anh: {_build_prediction_context(prediction)}\n"
        f"Kieu tra loi: {style}\n\n"
        f"Cau tra loi qua ngan hien tai:\n{original_answer}\n\n"
        f"Context:\n{_build_source_context(docs)}\n\n"
        "Viet lai thanh 5-8 cau (neu style=comparison thi 6-9 cau), "
        "mo dau bang cau tra loi truc tiep, co them y phan tich va goi y tiep theo."
    )
    return {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": min(0.7, max(LLM_TEMPERATURE, 0.25)),
            "maxOutputTokens": min(LLM_MAX_TOKENS + 220, 1024),
        },
    }


def _build_paraphrase_payload(
    answer: str,
    message: str,
    prediction: dict | None,
    docs: list[dict],
    intent: str,
    style: str,
) -> dict:
    system_prompt = (
        "Ban la tro ly tu van o to. Viet lai cau tra loi theo van phong tu nhien va de hieu. "
        "Tuyet doi khong sao chep nguyen van context, khong sao chep cum > 8 tu lien tiep tu tai lieu, "
        "va khong tao dong dang 'Tham khao [n]: ...'."
    )
    user_prompt = (
        f"Cau hoi user: {message}\n"
        f"Intent: {intent}\n"
        f"Kieu tra loi: {style}\n"
        f"Body type tu anh: {_build_prediction_context(prediction)}\n\n"
        f"Cau tra loi can viet lai:\n{answer}\n\n"
        f"Context goc:\n{_build_source_context(docs)}\n\n"
        "Hay viet lai 4-8 cau, tu nhien, ngan gon, co citation [1], [2] o cuoi cau khi can."
    )
    return {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": min(0.55, max(LLM_TEMPERATURE, 0.2)),
            "maxOutputTokens": min(LLM_MAX_TOKENS + 180, 960),
        },
    }


def generate_answer_with_rag(
    message: str,
    prediction: dict | None,
    docs: list[dict],
    intent: str,
) -> tuple[str | None, dict]:
    if not LLM_API_KEY:
        return None, {
            "mode": "fallback",
            "reason": "gemini_key_missing",
            "style": "gemini",
        }

    if not LLM_MODEL:
        return None, {
            "mode": "fallback",
            "reason": "gemini_model_missing",
            "style": "gemini",
        }

    system_prompt, user_prompt, answer_style = _build_prompts(
        message=message,
        prediction=prediction,
        docs=docs,
        intent=intent,
    )

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        ],
        "generationConfig": {
            "temperature": LLM_TEMPERATURE,
            "maxOutputTokens": LLM_MAX_TOKENS,
        },
    }

    key = quote(LLM_API_KEY, safe="")
    api_base = LLM_API_BASE.rstrip("/")
    url = f"{api_base}/models/{LLM_MODEL}:generateContent?key={key}"

    data, err_meta = _send_json(url=url, payload=payload)
    if err_meta is not None:
        return None, err_meta

    content, empty_reason = _extract_gemini_text(data)
    if not content:
        return None, {
            "mode": "fallback",
            "reason": empty_reason or "gemini_empty_content",
            "model": LLM_MODEL,
            "api_base": api_base,
            "style": "gemini",
        }

    refined = False
    dequoted = False

    content = _strip_reference_dump(content)
    if _should_expand_answer(content, answer_style):
        expand_payload = _build_expand_payload(
            original_answer=content,
            message=message,
            prediction=prediction,
            docs=docs,
            intent=intent,
            style=answer_style,
        )
        rewrite_data, rewrite_err = _send_json(url=url, payload=expand_payload)
        if rewrite_err is None and rewrite_data is not None:
            expanded_content, expanded_empty_reason = _extract_gemini_text(rewrite_data)
            if expanded_content and not expanded_empty_reason and len(expanded_content) > len(content):
                content = _strip_reference_dump(expanded_content)
                refined = True

    if _contains_context_copy(content, docs):
        paraphrase_payload = _build_paraphrase_payload(
            answer=content,
            message=message,
            prediction=prediction,
            docs=docs,
            intent=intent,
            style=answer_style,
        )
        paraphrase_data, paraphrase_err = _send_json(url=url, payload=paraphrase_payload)
        if paraphrase_err is None and paraphrase_data is not None:
            paraphrased_content, paraphrase_empty_reason = _extract_gemini_text(paraphrase_data)
            if paraphrased_content and not paraphrase_empty_reason:
                content = _strip_reference_dump(paraphrased_content)
                dequoted = True

    content = _enrich_if_still_short(
        content=content,
        style=answer_style,
        prediction=prediction,
        docs=docs,
        intent=intent,
    )
    content = _strip_reference_dump(content)

    return content, {
        "mode": "llm",
        "model": LLM_MODEL,
        "api_base": api_base,
        "style": "gemini",
        "answer_style": answer_style,
        "refined": refined,
        "dequoted": dequoted,
    }
