
(function () {
  "use strict";


  const AI_BASE_URL =
    (window.KoraConfig && window.KoraConfig.AI_BASE) ||
    window.KORA_AI_BASE_URL ||
    "http://localhost:8000";

  const fileInput = document.getElementById("alimento-file");
  const previewBox = document.getElementById("alimento-preview");
  const previewImg = document.getElementById("alimento-preview-img");
  const previewPlaceholder = previewBox
    ? previewBox.querySelector(".s-alimento__preview-placeholder")
    : null;
  const btnObtener = document.getElementById("btn-obtener-ingredientes");
  const textareaIngredientes = document.getElementById("alimento-detecciones");
  const btnModificar = document.getElementById("btn-usar-deteccion");
  const inputNombre = document.getElementById("alimento-nombre");

  let selectedFile = null;

  if (fileInput) {
    fileInput.addEventListener("change", function (e) {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      if (!file.type.startsWith("image/")) {
        alert("El archivo debe ser una imagen.");
        fileInput.value = "";
        return;
      }

      selectedFile = file;

      const reader = new FileReader();
      reader.onload = function (ev) {
        if (previewImg) {
          previewImg.src = ev.target.result;
          previewImg.style.display = "block";
        }
        if (previewPlaceholder) {
          previewPlaceholder.style.display = "none";
        }
      };
      reader.readAsDataURL(file);
    });
  }

  if (btnObtener) {
    btnObtener.addEventListener("click", async function () {
      if (!selectedFile) {
        alert("Primero agrega una imagen del alimento.");
        return;
      }

      setLoading(true);

      try {
        const formData = new FormData();
        formData.append("image", selectedFile);

        const response = await fetch("/api/ai/vision/analyze", {
          method: "POST",
          body: formData,
      
        });

        if (!response.ok) {
          const errBody = await response.json().catch(() => ({}));
          throw new Error(
            errBody.detail || errBody.error || `Error HTTP ${response.status}`
          );
        }

        const data = await response.json();

        if (!data.success) {
          throw new Error(data.error || "El análisis de la imagen falló.");
        }

        const detections = data.detections || [];

        if (detections.length === 0) {
          if (textareaIngredientes) {
            textareaIngredientes.value =
              "No se detectaron ingredientes en la imagen.";
            textareaIngredientes.disabled = false;
          }
          return;
        }

        const sorted = detections
          .slice()
          .sort((a, b) => (b.confidence || 0) - (a.confidence || 0));

        const text = sorted
          .map((d) => {
            const conf = Math.round((d.confidence || 0) * 100);
            return `• ${capitalize(d.food)} (${conf}%)`;
          })
          .join("\n");

        if (textareaIngredientes) {
          textareaIngredientes.value = text;
          textareaIngredientes.disabled = false;
        }
      } catch (err) {
        console.error("[kora-vision]", err);
        alert("Error al analizar la imagen: " + (err.message || err));
      } finally {
        setLoading(false);
      }
    });
  }
  if (btnModificar && textareaIngredientes && inputNombre) {
    btnModificar.addEventListener("click", function () {
        const seleccion = window.getSelection().toString().trim();

        if (!seleccion) {
            alert("Selecciona con el cursor el alimento que deseas utilizar.");
            return;
        }

        const alimento = seleccion
            .replace(/^•\s*/, "")
            .replace(/\s*\(\d+(?:\.\d+)?%\)\s*$/, "")
            .trim();

        if (!alimento) {
            alert("Selecciona un alimento válido.");
            return;
        }

        inputNombre.value = alimento;
        inputNombre.dispatchEvent(new Event("input", { bubbles: true }));
    });
}

  function setLoading(isLoading) {
      if (!btnObtener) return;

      btnObtener.disabled = isLoading;
      btnObtener.textContent = isLoading
          ? "Analizando..."
          : "Analizar imagen";
  }
  function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
})();
