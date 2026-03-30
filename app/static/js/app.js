const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const resultBox = document.getElementById("result");
const previewWrapper = document.getElementById("previewWrapper");
const previewImage = document.getElementById("previewImage");

const outputImages = document.getElementById("outputImages");
const originalImage = document.getElementById("originalImage");
const croppedImage = document.getElementById("croppedImage");

const analysisCard = document.getElementById("analysisCard");
const predictedLabel = document.getElementById("predictedLabel");
const confidenceValue = document.getElementById("confidenceValue");
const detectorConfidence = document.getElementById("detectorConfidence");
const summaryText = document.getElementById("summaryText");
const knowledgeSummary = document.getElementById("knowledgeSummary");
const pdfSummary = document.getElementById("pdfSummary");

const characteristicsList = document.getElementById("characteristicsList");
const prosList = document.getElementById("prosList");
const consList = document.getElementById("consList");
const bestForList = document.getElementById("bestForList");
const examplesList = document.getElementById("examplesList");

const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");
const chatStatus = document.getElementById("chatStatus");
const promptButtons = document.querySelectorAll(".chip[data-prompt]");

let currentPreviewUrl = null;
let lastPrediction = null;

function setList(element, items) {
  element.innerHTML = "";

  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Không có dữ liệu.";
    element.appendChild(li);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    element.appendChild(li);
  });
}

function setChatStatus(text) {
  chatStatus.textContent = text;
}

function scrollChatToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendMessage(role, text, meta = "") {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role === "user" ? "message-user" : "message-assistant"}`;

  const p = document.createElement("p");
  p.textContent = text;
  wrapper.appendChild(p);

  if (meta) {
    const m = document.createElement("div");
    m.className = "message-meta";
    m.textContent = meta;
    wrapper.appendChild(m);
  }

  chatMessages.appendChild(wrapper);
  scrollChatToBottom();
  return wrapper;
}

function formatConfidence(value) {
  if (value === null || value === undefined) {
    return "-";
  }
  return `${(value * 100).toFixed(2)}%`;
}

function syncAnalysisToUI(result) {
  if (!result) {
    return;
  }

  if (result.original_image_url) {
    originalImage.src = result.original_image_url;
  }

  if (result.crop?.crop_url) {
    croppedImage.src = result.crop.crop_url;
    outputImages.classList.remove("hidden");
  } else {
    outputImages.classList.add("hidden");
  }

  predictedLabel.textContent = result.classification?.predicted_label ?? "-";
  confidenceValue.textContent = formatConfidence(result.classification?.confidence);
  detectorConfidence.textContent = formatConfidence(result.detection?.main_car?.confidence);

  summaryText.textContent = result.summary ?? "-";

  const structuredKnowledge = result.knowledge?.structured;
  const pdfKnowledge = result.knowledge?.pdf;

  knowledgeSummary.textContent = structuredKnowledge?.summary ?? "-";
  pdfSummary.textContent = pdfKnowledge?.summary ?? "-";

  setList(characteristicsList, structuredKnowledge?.characteristics);
  setList(prosList, structuredKnowledge?.pros);
  setList(consList, structuredKnowledge?.cons);
  setList(bestForList, structuredKnowledge?.best_for);
  setList(examplesList, structuredKnowledge?.examples);

  analysisCard.classList.remove("hidden");
}

async function sendChatMessage(message) {
  appendMessage("user", message);

  const typingNode = appendMessage("assistant", "Đang suy luận...");
  chatForm.querySelector("button").disabled = true;

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message })
    });

    const data = await response.json();

    typingNode.remove();

    if (!response.ok) {
      const errText = data?.detail || "Không thể nhận phản hồi từ chat API.";
      appendMessage("assistant", errText);
      return;
    }

    const answer = data?.answer || "Mình chưa tìm được nội dung phù hợp.";
    const sourceCount = Array.isArray(data?.sources) ? data.sources.length : 0;
    const intent = data?.intent ? `intent: ${data.intent}` : "intent: unknown";
    const generationMode = data?.generation?.mode;
    const generationModel = data?.generation?.model;
    const generationReason = data?.generation?.reason;
    const answerStyle = data?.generation?.answer_style;
    const refined = data?.generation?.refined;
    const dequoted = data?.generation?.dequoted;

    let meta = `${intent} | sources: ${sourceCount}`;
    if (lastPrediction?.predicted_label) {
      meta += ` | context: ${lastPrediction.predicted_label}`;
    }
    if (generationMode) {
      meta += ` | gen: ${generationMode}`;
    }
    if (generationModel) {
      meta += ` | model: ${generationModel}`;
    }
    if (answerStyle) {
      meta += ` | style: ${answerStyle}`;
    }
    if (refined) {
      meta += " | refined";
    }
    if (dequoted) {
      meta += " | dequoted";
    }
    if (generationReason && generationMode !== "llm") {
      meta += ` | reason: ${generationReason}`;
    }

    appendMessage("assistant", answer, meta);
  } catch (error) {
    typingNode.remove();
    appendMessage("assistant", `Lỗi gọi chat API: ${error.message}`);
  } finally {
    chatForm.querySelector("button").disabled = false;
  }
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) {
    return;
  }

  if (currentPreviewUrl) {
    URL.revokeObjectURL(currentPreviewUrl);
  }

  currentPreviewUrl = URL.createObjectURL(file);
  previewImage.src = currentPreviewUrl;
  previewWrapper.classList.remove("hidden");
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = fileInput.files[0];
  if (!file) {
    resultBox.textContent = "Vui lòng chọn ảnh trước khi phân tích.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  resultBox.textContent = "Đang xử lý ảnh...";
  outputImages.classList.add("hidden");
  analysisCard.classList.add("hidden");

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    resultBox.textContent = JSON.stringify(data, null, 2);

    if (!response.ok) {
      throw new Error(data?.detail || "Không thể phân tích ảnh.");
    }

    const result = data?.result;
    if (!result) {
      throw new Error("API trả về thiếu trường result.");
    }

    syncAnalysisToUI(result);

    lastPrediction = {
      predicted_label: result.classification?.predicted_label ?? null,
      confidence: result.classification?.confidence ?? null
    };

    if (lastPrediction.predicted_label) {
      const pct = formatConfidence(lastPrediction.confidence);
      setChatStatus(`Đang dùng ngữ cảnh ảnh gần nhất: ${lastPrediction.predicted_label} (${pct}).`);
      appendMessage(
        "assistant",
        `Đã ghi nhận ảnh mới: ${lastPrediction.predicted_label} (${pct}). Bạn có thể hỏi thêm để mình tư vấn sâu hơn.`
      );
    } else {
      setChatStatus("Ảnh chưa phân loại được body type rõ ràng. Bạn vẫn có thể hỏi câu hỏi chung.");
      appendMessage("assistant", "Mình chưa xác định chắc body type từ ảnh này. Bạn có thể gửi câu hỏi để mình hỗ trợ thêm.");
    }
  } catch (error) {
    resultBox.textContent = `Lỗi gọi API: ${error.message}`;
    setChatStatus("Lần phân tích gần nhất gặp lỗi. Chat vẫn dùng được cho câu hỏi chung.");
  }
});

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const message = chatInput.value.trim();
  if (!message) {
    return;
  }

  chatInput.value = "";
  await sendChatMessage(message);
});

promptButtons.forEach((btn) => {
  btn.addEventListener("click", async () => {
    const prompt = btn.dataset.prompt?.trim();
    if (!prompt) {
      return;
    }
    chatInput.value = "";
    await sendChatMessage(prompt);
  });
});
