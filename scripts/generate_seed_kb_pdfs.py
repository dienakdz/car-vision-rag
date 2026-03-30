from pathlib import Path
import textwrap

import fitz  # PyMuPDF

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "kb" / "pdfs"

FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)

PAGE_RECT = fitz.paper_rect("a4")
CONTENT_RECT = fitz.Rect(42, 42, PAGE_RECT.width - 42, PAGE_RECT.height - 42)
MAX_LINE_WIDTH = 95
MAX_LINES_PER_PAGE = 46
FONT_SIZE = 11
LINE_HEIGHT = 1.3


def _build_body_type_guide(
    body_type: str,
    title: str,
    positioning: str,
    strengths: list[str],
    tradeoffs: list[str],
    use_cases: list[str],
    consultation_questions: list[str],
    objection_handlers: list[str],
    test_drive_focus: list[str],
) -> str:
    lines: list[str] = []
    lines.append(f"MINH DIEN SHOWROOM - CAM NANG TU VAN {body_type.upper()}")
    lines.append(f"Tieu de: {title}")
    lines.append("Phien ban: 1.0 | Muc dich: tai lieu noi bo cho chatbot va tu van vien")
    lines.append("")
    lines.append("1) DINH VI NHOM XE")
    lines.append(positioning)
    lines.append("")
    lines.append("2) UU DIEM NOI BAT")
    for item in strengths:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("3) DIEM CAN LUU Y / TRADE-OFF")
    for item in tradeoffs:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("4) KICH BAN SU DUNG PHU HOP")
    for idx, case in enumerate(use_cases, start=1):
        lines.append(f"{idx}. {case}")
    lines.append("")
    lines.append("5) BO CAU HOI KHAI THAC NHU CAU")
    for idx, q in enumerate(consultation_questions, start=1):
        lines.append(f"{idx}. {q}")
    lines.append("")
    lines.append("6) XU LY PHAN BIEN THUONG GAP")
    for idx, handler in enumerate(objection_handlers, start=1):
        lines.append(f"{idx}. {handler}")
    lines.append("")
    lines.append("7) CHECKLIST TEST DRIVE")
    for idx, point in enumerate(test_drive_focus, start=1):
        lines.append(f"{idx}. {point}")
    lines.append("")
    lines.append("8) MAU CAU TRA LOI CHO CHATBOT")
    lines.append(
        f"- Neu nguoi dung hoi chung ve {body_type}: nen bat dau bang 2 cau mo ta gia tri cot loi,"
    )
    lines.append(
        "  sau do dua 2 uu diem + 1 luu y, ket thuc bang 1 cau hoi tiep de ca nhan hoa goi y."
    )
    lines.append(
        "- Neu nguoi dung da co nhu cau ro: tra loi truc tiep, ngan gon, va dan nguon tham chieu"
    )
    lines.append("  theo dinh dang [1], [2] khi co trich doan tu tai lieu.")
    lines.append("")
    lines.append("9) NGUYEN TAC AN TOAN THONG TIN")
    lines.append("- Khong tu y dua gia ban, uu dai, lai suat neu khong co du lieu cap nhat.")
    lines.append("- Khong cam ket giao xe ngay neu chua xac nhan ton kho thuc te.")
    lines.append("- Neu thong tin thieu: phai noi ro va goi y buoc xac minh tiep theo.")
    lines.append("")
    lines.append("10) TOI UU CHATBOT RAG")
    lines.append(
        f"- Tu khoa uu tien retrieval cho {body_type}: body type, nhu cau su dung, uu/nhuoc diem, test drive."
    )
    lines.append("- Khi tra loi so sanh, luon dua theo cau truc: boi canh -> khac biet -> goi y.")
    lines.append("- Giu giong dieu chuyen nghiep, trung lap voi phong cach Minh Dien Showroom.")
    lines.append("")
    lines.append("=== KET THUC TAI LIEU ===")
    return "\n".join(lines)


def _build_consultation_bank() -> str:
    lines: list[str] = [
        "MINH DIEN SHOWROOM - BO CAU HOI TU VAN THEO NHU CAU",
        "Phien ban: 1.0 | Dung cho chatbot va tu van vien tai quay",
        "",
        "1) MUC TIEU",
        "- Chuan hoa luong hoi dap de chatbot khong tra loi chung chung.",
        "- Giup tu van vien phan loai nhanh nhu cau va body type phu hop.",
        "",
        "2) NHOM CAU HOI KHAI THAC NHANH (QUALIFY)",
        "A. Nhu cau su dung",
        "- Xe dung chinh cho gia dinh, di lam, hay ket hop cong viec?",
        "- Ty le di trong pho / duong truong / duong xau la bao nhieu?",
        "- So nguoi di thuong xuyen? Co tre nho hay nguoi cao tuoi khong?",
        "B. Dieu kien tai chinh",
        "- Muc ngan sach du kien trong khoang nao?",
        "- Uu tien mua tien mat hay can phuong an tra gop?",
        "- Co nhu cau thu cu doi moi hay khong?",
        "C. Uu tien ky thuat",
        "- Uu tien em ai, tiet kiem, hay manh me va linh hoat?",
        "- Co yeu cau ve cong nghe an toan chu dong khong?",
        "- Co can khoang hanh ly lon hoac kha nang cho hang thuong xuyen khong?",
        "",
        "3) KHUNG GOI Y BODY TYPE",
        "- Sedan: uu tien su em ai, on dinh, di lam va gia dinh nho.",
        "- SUV: da dung, tam nhin cao, linh hoat nhieu dieu kien duong.",
        "- Hatchback: gon, linh hoat, de do xe trong do thi.",
        "- Pickup: phuc vu cho hang, cong viec, va chuyen di da dia hinh.",
        "",
        "4) MAU KICH BAN CHAT 5 BUOC",
        "Buoc 1: Xac nhan boi canh su dung cua khach.",
        "Buoc 2: Chon 2 body type phu hop nhat de so sanh nhanh.",
        "Buoc 3: Neu uu tien tai chinh ro, de xuat phuong an mua.",
        "Buoc 4: Chot de xuat 1 huong uu tien + 1 huong du phong.",
        "Buoc 5: Goi y dat lich test drive hoac gui danh sach mau xe tham khao.",
        "",
        "5) MAU PHAN HOI NGAN CHO CHATBOT",
        "- Cau hoi: 'Xe nay hop di gia dinh khong?'",
        "  Tra loi mau: Neu gia dinh di nhieu trong pho va uu tien em ai, sedan rat hop.",
        "  Neu can khoang cabin linh hoat hon cho du lich cuoi tuan, SUV la lua chon can bang.",
        "- Cau hoi: 'Sedan khac SUV o diem nao?'",
        "  Tra loi mau: Sedan thuong em va tiet kiem hon trong do thi, SUV linh hoat hon ve tam nhin",
        "  va khoang sang gam. Lua chon phu thuoc vao tuyen duong va nhu cau khoang khong gian.",
        "",
        "6) NGUYEN TAC RANG BUOC",
        "- Khong dua thong tin gia chi tiet neu chua xac minh bang bang gia hien hanh.",
        "- Khong tra loi thay bo phan tai chinh ve lai suat cu the theo ngay.",
        "- Luon co cau ket mo huong hanh dong: test drive, xem xe, ho so tra gop.",
        "",
        "7) KPI CHATBOT NOI BO",
        "- Ty le tra loi co cau hoi lam ro tiep theo >= 70%.",
        "- Ty le tra loi co lien ket nguon KB >= 80%.",
        "- Ty le phan hoi dung intent >= 90%.",
        "",
        "=== KET THUC TAI LIEU ===",
    ]
    return "\n".join(lines)


def _build_workflow_doc() -> str:
    lines: list[str] = [
        "MINH DIEN SHOWROOM - QUY TRINH TEST DRIVE VA DINH GIA THU CU DOI MOI",
        "Phien ban: 1.0 | Dung cho bo phan kinh doanh va chatbot huong dan",
        "",
        "1) QUY TRINH TEST DRIVE CHUAN",
        "Giai doan A - Truoc khi lai thu",
        "- Kiem tra giay phep lai xe va thong tin lien he khach hang.",
        "- Chot nhu cau test: trong pho, duong truong, kha nang quay dau, phanh.",
        "- Gioi thieu nhanh tinh nang an toan can biet truoc khi van hanh.",
        "",
        "Giai doan B - Trong khi lai thu",
        "- Doan 1 (toc do thap): danh gia do em, tanh lanh, tam nhin.",
        "- Doan 2 (toc do trung binh): danh gia kha nang vuot, on dinh than xe.",
        "- Doan 3 (tinh huong mo phong): quay dau, de xe, phanh gan.",
        "",
        "Giai doan C - Sau khi lai thu",
        "- Tong hop nhan xet theo 4 tieu chi: cam giac lai, thoai mai, tien nghi, an toan.",
        "- So sanh voi nhu cau ban dau cua khach.",
        "- Chot de xuat tiep theo: bao gia, tra gop, dat coc, hen lai thu mau khac.",
        "",
        "2) QUY TRINH DINH GIA THU CU DOI MOI",
        "Buoc 1 - Tiep nhan thong tin ban dau",
        "- Nam san xuat, so km, lich su bao duong, tinh trang giay to.",
        "- Hinh anh 6 goc xe, noi that, khoang may, cong to met.",
        "",
        "Buoc 2 - Khao sat thuc te",
        "- Danh gia ngoai that: son, gam, vo meo, den kinh.",
        "- Danh gia noi that: ghe, taplo, man hinh, dieu hoa.",
        "- Danh gia ky thuat: dong co, hop so, phanh, lop.",
        "",
        "Buoc 3 - Dinh gia va de xuat",
        "- Doi chieu mat bang gia thi truong theo tinh trang tuong dong.",
        "- Tru/ cong he so theo lich su su dung va kha nang ban lai.",
        "- Dua khung gia de xuat va dieu kien hieu luc.",
        "",
        "Buoc 4 - Chot giao dich",
        "- Xac nhan gia thu cu vao hop dong mua xe moi.",
        "- Huong dan bo sung ho so neu thieu.",
        "- Cam ket moc thoi gian xu ly va ban giao xe.",
        "",
        "3) MAU THONG BAO CHO CHATBOT",
        "- Neu khach hoi thu cu doi moi: chatbot phai noi ro day la gia tam tinh.",
        "- Neu khach hoi test drive: chatbot de xuat 2-3 khung gio va diem hen.",
        "- Neu khach hoi lai suat: chatbot huong dan lien he tu van vien tai chinh de nhan",
        "  thong tin cap nhat theo ngay.",
        "",
        "4) KIEM SOAT CHAT LUONG NOI BO",
        "- Moi phien test drive can co bien ban cam nhan ngan.",
        "- Moi case thu cu can luu bo anh toi thieu va checklist tinh trang.",
        "- Chatbot phai luon giu thong diep trung lap, khong over-claim.",
        "",
        "5) CAC LOI CAN TRANH",
        "- Bao gia cam ket khi chua check tinh trang xe thuc te.",
        "- Cam ket tien do giao xe khi chua xac nhan ton kho.",
        "- Tu van sai pham vi nghiep vu tai chinh hoac phap ly.",
        "",
        "=== KET THUC TAI LIEU ===",
    ]
    return "\n".join(lines)


SEED_DOCS = {
    "05_Guide_Sedan_Minh_Dien_Showroom.pdf": _build_body_type_guide(
        body_type="sedan",
        title="Cam nang tu van Sedan",
        positioning=(
            "Sedan phu hop nguoi dung uu tien su em ai, on dinh than xe va hieu qua van hanh "
            "trong boi canh di lam hang ngay, di gia dinh nho, va di duong dai theo cao toc."
        ),
        strengths=[
            "Van hanh on dinh tren mat duong dep, cam giac lai dam chac.",
            "Muc tieu hao nhien lieu de kiem soat chi phi su dung hang thang.",
            "Khoang hanh ly kieu cop sau phu hop nhu cau gia dinh nho.",
            "Phu hop khach can xe lich su va hinh anh chuyen nghiep.",
            "Nguoi ngoi hang 2 thoai mai trong cac chuyen di tam trung.",
        ],
        tradeoffs=[
            "Gam xe thuong thap hon SUV, can chu y duong ngap va via he cao.",
            "Tinh linh hoat cho hang lon kem hon hatchback va pickup.",
            "Neu can 7 cho hoac khoang rong toi da thi can nhac SUV.",
        ],
        use_cases=[
            "Khach di lam 20-40 km/ngay trong do thi va duong vanh dai.",
            "Gia dinh 3-4 nguoi, uu tien su em va kha nang cach am.",
            "Khach can xe tiep doi tac, de lai an tuong chuyen nghiep.",
            "Khach can xe cho chuyen du lich cuoi tuan den noi ha tang tot.",
        ],
        consultation_questions=[
            "Anh/chị đi trong phố hay cao tốc nhiều hơn?",
            "Gia đình mình thường đi mấy người, có nhu cầu ghế trẻ em không?",
            "Ưu tiên lớn nhất là êm ái, tiết kiệm hay công nghệ an toàn?",
            "Nhu cầu chở đồ cồng kềnh có xuất hiện thường xuyên không?",
            "Anh/chị có sẵn bãi đỗ cố định ở nhà và công ty chưa?",
        ],
        objection_handlers=[
            "Neu khach noi sedan gam thap: giai thich dung lop va toc do phu hop van di do thi tot.",
            "Neu khach so cop sau nho: de xuat bo to chuc hanh ly va so sanh nhu cau thuc te.",
            "Neu khach phan van SUV: de xuat lai thu 2 mau de so sanh cam giac lai.",
        ],
        test_drive_focus=[
            "Do em o ga giam toc va mat duong noi.",
            "Do on khi chuyen lan o toc do trung binh.",
            "Cam giac vo-lang trong bai quay dau va ghep xe.",
            "Muc do cach am o 40-60 km/h.",
            "Do thoai mai hang ghe sau khi ngoi 20 phut.",
        ],
    ),
    "06_Guide_SUV_Minh_Dien_Showroom.pdf": _build_body_type_guide(
        body_type="suv",
        title="Cam nang tu van SUV",
        positioning=(
            "SUV la lua chon da dung, phu hop khach can tam nhin cao, khoang khong gian linh hoat "
            "va kha nang di nhieu dieu kien duong khac nhau."
        ),
        strengths=[
            "Khoang sang gam cao, tu tin hon khi qua duong xau va o ga.",
            "Tu the ngoi cao cho tam nhin bao quat, de quan sat giao thong.",
            "Khoang cabin va khoang hanh ly linh hoat cho gia dinh.",
            "Phu hop chuyen di xa va hoat dong cuoi tuan.",
            "Nhieu phien ban co cong nghe ho tro lai va an toan chu dong.",
        ],
        tradeoffs=[
            "Chi phi nhien lieu va bao duong co the cao hon xe nho.",
            "Kich thuoc than xe lon hon, can lam quen khi do xe noi hep.",
            "Cam giac lanh than xe co the ro hon sedan o cua cua nhanh.",
        ],
        use_cases=[
            "Gia dinh 4-6 nguoi di lai hon hop trong tuan va cuoi tuan.",
            "Khach hay di du lich, can khoang hanh ly rong.",
            "Khach di nhieu tuyen duong co chat luong mat duong khong dong deu.",
            "Khach uu tien tam nhin lai xe thoang va tu the ngoi thoai mai.",
        ],
        consultation_questions=[
            "Muc do su dung xe cho gia dinh va tre nho nhu the nao?",
            "Anh/chị có thường xuyên đi xa hoặc đi tỉnh không?",
            "Bãi đỗ xe tại nhà/chung cư có giới hạn chiều dài hoặc chiều cao không?",
            "Anh/chị ưu tiên độ êm hay ưu tiên không gian và tầm nhìn cao?",
            "Nhu cầu chở hành lý cho du lịch gia đình thường xuyên không?",
        ],
        objection_handlers=[
            "Neu khach ngai ton nhien lieu: dua thong tin thuc te theo dieu kien su dung hop ly.",
            "Neu khach ngai do xe kho: de xuat ban co camera, cam bien va tinh nang ho tro do xe.",
            "Neu khach phan van sedan: so sanh theo nhu cau duong dai va khoang hanh ly.",
        ],
        test_drive_focus=[
            "Tam nhin truoc sau va hai ben khi vao giao lo dong.",
            "Do em he thong treo khi di qua giam toc.",
            "Do de dieu khien khi quay dau o duong hep.",
            "Do on o khoang toc do 50-80 km/h.",
            "Toc do phan hoi chan ga khi can vuot xe an toan.",
        ],
    ),
    "07_Guide_Pickup_Minh_Dien_Showroom.pdf": _build_body_type_guide(
        body_type="pickup",
        title="Cam nang tu van Pickup",
        positioning=(
            "Pickup toi uu cho nhu cau cong viec va cho hang, dong thoi van duy tri kha nang "
            "su dung hang ngay voi do ben va tinh da nhiem."
        ),
        strengths=[
            "Thung hang mo linh hoat, phu hop van chuyen vat dung kich thuoc lon.",
            "Khung gam ben, phu hop dieu kien khai thac cuong do cao.",
            "Kha nang ket hop cong viec va di lai ca nhan trong cung mot xe.",
            "Phu hop nguoi dung can kha nang keo, cho do, di duong hon hop.",
            "Gia tri su dung thuc te cao voi khach hang kinh doanh nho.",
        ],
        tradeoffs=[
            "Cam giac em ai trong pho co the khong bang sedan.",
            "Than xe dai, can ky nang quay dau va ghep xe tot hon.",
            "Chi phi van hanh phu thuoc lon vao tan suat cho tai.",
        ],
        use_cases=[
            "Khach co cong viec can cho hang cong cu hoac vat tu.",
            "Khach di cong trinh va can xe ben bi.",
            "Khach co nhu cau du lich da ngoai kem van chuyen do.",
            "Khach can mot xe da dung cho ca cong viec va sinh hoat.",
        ],
        consultation_questions=[
            "Mỗi tuần anh/chị chở hàng bao nhiêu lần, tải trọng trung bình?",
            "Chủ yếu xe đi trong phố hay công trường/đường hỗn hợp?",
            "Anh/chị có cần ghế sau cho gia đình dùng thường xuyên không?",
            "Kích thước hàng hóa lớn nhất thường chở là gì?",
            "Ưu tiên lớn hơn là độ bền hay độ êm khi đi phố?",
        ],
        objection_handlers=[
            "Neu khach ngai do em: de xuat lai thu co tai gia dinh de cam nhan thuc te.",
            "Neu khach ngai do xe: huong dan bai ghep xe, camera va cam bien.",
            "Neu khach ngai ton chi phi: tinh TCO theo kich ban su dung thuc te.",
        ],
        test_drive_focus=[
            "Do phan hoi vo-lang khi quay dau.",
            "Do on va do rung o toc do trung binh.",
            "Cam giac phanh khi xe co tai gia dinh.",
            "Kha nang tan dung guong va camera khi ghep xe.",
            "Kha nang but toc o dai toc do 40-70 km/h.",
        ],
    ),
    "08_Guide_Hatchback_Minh_Dien_Showroom.pdf": _build_body_type_guide(
        body_type="hatchback",
        title="Cam nang tu van Hatchback",
        positioning=(
            "Hatchback phu hop nguoi dung do thi, can xe gon nhe, linh hoat, de quay dau "
            "va de do trong khong gian han che."
        ),
        strengths=[
            "Kich thuoc gon, linh hoat trong duong pho dong duc.",
            "Cua khoang hanh ly dang hatch tien cho bo xep vat dung hang ngay.",
            "Thuong co chi phi su dung hop ly cho nguoi mua xe dau tien.",
            "Phan than sau gon giup ghep xe nhanh trong bai do hep.",
            "Phu hop nguoi dung uu tien tinh co dong va tien dung do thi.",
        ],
        tradeoffs=[
            "Khong gian hang 2 va hanh ly co the nho hon SUV.",
            "Khong phu hop nhu cau cho do qua lon thuong xuyen.",
            "Di duong dai day tai co the kem thoai mai hon xe lon.",
        ],
        use_cases=[
            "Nguoi mua xe dau tien can de su dung, de bao duong.",
            "Khach di lai chu yeu trong noi thanh va can de do xe.",
            "Gia dinh tre 2-3 nguoi can xe gon nhung van thuc dung.",
            "Khach uu tien chi phi su dung theo thang.",
        ],
        consultation_questions=[
            "Mỗi ngày anh/chị đi bao nhiêu km trong giờ cao điểm?",
            "Nhu cầu bãi đỗ tại nhà/công ty có giới hạn kích thước không?",
            "Mức ưu tiên giữa tiết kiệm chi phí và không gian nội thất là gì?",
            "Anh/chị thường đi mấy người và chở hành lý ra sao?",
            "Có nhu cầu đi tỉnh đường dài thường xuyên hay không?",
        ],
        objection_handlers=[
            "Neu khach ngai nho: doi chieu thuc te theo so nguoi di thuong xuyen.",
            "Neu khach can du lich xa: de xuat phuong an bo xep hanh ly toi uu.",
            "Neu khach so an toan: nhan manh goi cong nghe ho tro lai va phanh.",
        ],
        test_drive_focus=[
            "Quay dau trong ngo hep va ghep xe song song.",
            "Do muot chan ga o toc do thap trong do thi.",
            "Do em khi qua o ga va mat duong noi.",
            "Tam nhin khi ra vao bai do va quay dau.",
            "Muc tieu hao uoc tinh theo hanh trinh thu nghiem.",
        ],
    ),
    "09_Bo_cau_hoi_tu_van_theo_nhu_cau_Minh_Dien_Showroom.pdf": _build_consultation_bank(),
    "10_Quy_trinh_Test_Drive_va_Dinh_gia_Thu_xe_cu_Minh_Dien_Showroom.pdf": _build_workflow_doc(),
}


def _resolve_font() -> tuple[str, str | None]:
    for font_path in FONT_CANDIDATES:
        if font_path.exists():
            return "customfont", str(font_path)
    return "helv", None


def _wrap_content(content: str) -> list[str]:
    lines: list[str] = []
    for raw_line in content.splitlines():
        if not raw_line.strip():
            lines.append("")
            continue

        wrapped = textwrap.wrap(
            raw_line,
            width=MAX_LINE_WIDTH,
            break_long_words=False,
            break_on_hyphens=False,
        )
        lines.extend(wrapped if wrapped else [""])
    return lines


def _paginate_lines(lines: list[str]) -> list[list[str]]:
    pages: list[list[str]] = []
    for start in range(0, len(lines), MAX_LINES_PER_PAGE):
        pages.append(lines[start:start + MAX_LINES_PER_PAGE])
    return pages


def _write_pdf(path: Path, content: str) -> None:
    font_name, font_file = _resolve_font()
    lines = _wrap_content(content)
    page_lines = _paginate_lines(lines)

    doc = fitz.open()
    for chunk in page_lines:
        page = doc.new_page(width=PAGE_RECT.width, height=PAGE_RECT.height)
        text = "\n".join(chunk)
        kwargs = {
            "fontname": font_name,
            "fontsize": FONT_SIZE,
            "lineheight": LINE_HEIGHT,
            "align": 0,
        }
        if font_file:
            kwargs["fontfile"] = font_file
        page.insert_textbox(CONTENT_RECT, text, **kwargs)
    doc.save(path)
    doc.close()


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    for filename, content in SEED_DOCS.items():
        path = PDF_DIR / filename
        _write_pdf(path, content)
        created += 1
        print(f"Created: {filename}")
    print(f"Done. Created {created} PDF files in {PDF_DIR}")


if __name__ == "__main__":
    main()
