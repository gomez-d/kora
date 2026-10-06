/**
 * kora-vision.js
 * Conecta el frontend con el endpoint de visión del microservicio AI:
 *   POST /vision/analyze  (multipart/form-data, campo "image")
 *
 * Respuesta esperada:
 *   { success: true, detections: [ { food: string, confidence: number }, ... ] }
 *   o { success: false, detections: [], error: string }
 */

(function () {
  "use strict";

  // ─────────────────────────────────────────────
  // Configuración – cambia la URL según tu entorno
  // ─────────────────────────────────────────────
  const AI_BASE_URL = window.KORA_AI_BASE_URL || "http://localhost:8000";

  // ─────────────────────────────────────────────
  // Elementos del DOM
  // ─────────────────────────────────────────────
  const fileInput = document.getElementById("alimento-file");
  const previewBox = document.getElementById("alimento-preview");
  const previewImg = document.getElementById("alimento-preview-img");
  const previewPlaceholder = previewBox
    ? previewBox.querySelector(".s-alimento__preview-placeholder")
    : null;
  const btnObtener = document.getElementById("btn-obtener-ingredientes");
  const textareaIngredientes = document.getElementById("alimento-ingredientes");
  const btnModificar = document.getElementById("btn-modificar-ingredientes");

  let selectedFile = null;

  // ─────────────────────────────────────────────
  // Preview de la imagen seleccionada
  // ─────────────────────────────────────────────
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

  // ─────────────────────────────────────────────
  // Botón "Obtener ingredientes"
  // ─────────────────────────────────────────────
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

        const response = await fetch(`${AI_BASE_URL}/vision/analyze`, {
          method: "POST",
          body: formData,
          // No poner Content-Type: el navegador lo establece con el boundary
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

        // Ordenar por confianza descendente y formatear
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

  // ─────────────────────────────────────────────
  // Botón "Modificar" – habilita edición manual
  // ─────────────────────────────────────────────
  if (btnModificar && textareaIngredientes) {
    btnModificar.addEventListener("click", function () {
      textareaIngredientes.disabled = false;
      textareaIngredientes.focus();
    });
  }

  // ─────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────
  function setLoading(isLoading) {
    if (!btnObtener) return;
    btnObtener.disabled = isLoading;
    btnObtener.textContent = isLoading
      ? "Analizando…"
      : "Obtener ingredientes";
  }

  function capitalize(str) {
    if (!str) return "";
    return str.charAt(0).toUpperCase() + str.slice(1);
  }
})();
