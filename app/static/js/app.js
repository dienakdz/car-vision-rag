const form = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const resultBox = document.getElementById("result");
const previewWrapper = document.getElementById("previewWrapper");
const previewImage = document.getElementById("previewImage");

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

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    resultBox.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    resultBox.textContent = `Lỗi gọi API: ${error.message}`;
  }
});