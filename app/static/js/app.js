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

const characteristicsList = document.getElementById("characteristicsList");
const prosList = document.getElementById("prosList");
const consList = document.getElementById("consList");
const bestForList = document.getElementById("bestForList");
const examplesList = document.getElementById("examplesList");

function setList(element, items) {
  element.innerHTML = "";

  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "Không có dữ liệu.";
    element.appendChild(li);
    return;
  }

  items.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item;
    element.appendChild(li);
  });
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (!file) return;

  const imageUrl = URL.createObjectURL(file);
  previewImage.src = imageUrl;
  previewWrapper.classList.remove("hidden");
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = fileInput.files[0];
  if (!file) {
    resultBox.textContent = "Vui lòng chọn một ảnh trước.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  resultBox.textContent = "Đang xử lý...";
  outputImages.classList.add("hidden");
  analysisCard.classList.add("hidden");

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    resultBox.textContent = JSON.stringify(data, null, 2);

    const result = data?.result;
    if (!result) return;

    if (result.original_image_url) {
      originalImage.src = result.original_image_url;
    }

    if (result.crop?.crop_url) {
      croppedImage.src = result.crop.crop_url;
      outputImages.classList.remove("hidden");
    }

    predictedLabel.textContent = result.classification?.predicted_label ?? "-";

    const clsConfidence = result.classification?.confidence;
    confidenceValue.textContent =
      clsConfidence !== null && clsConfidence !== undefined
        ? `${(clsConfidence * 100).toFixed(2)}%`
        : "-";

    const detConfidence = result.detection?.main_car?.confidence;
    detectorConfidence.textContent =
      detConfidence !== null && detConfidence !== undefined
        ? `${(detConfidence * 100).toFixed(2)}%`
        : "-";

    summaryText.textContent = result.summary ?? "-";
    const structuredKnowledge = result.knowledge?.structured;
    const pdfKnowledge = result.knowledge?.pdf;
    const pdfSummary = document.getElementById("pdfSummary");
    pdfSummary.textContent = pdfKnowledge?.summary ?? "-";

    knowledgeSummary.textContent = structuredKnowledge?.summary ?? "-";

    setList(characteristicsList, structuredKnowledge?.characteristics);
    setList(prosList, structuredKnowledge?.pros);
    setList(consList, structuredKnowledge?.cons);
    setList(bestForList, structuredKnowledge?.best_for);
    setList(examplesList, structuredKnowledge?.examples);

    analysisCard.classList.remove("hidden");
  } catch (error) {
    resultBox.textContent = `Lỗi gọi API: ${error.message}`;
  }
});