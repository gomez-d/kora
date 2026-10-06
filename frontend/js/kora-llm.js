/**
 * kora-llm.js
 * Conecta el frontend con el endpoint LLM del microservicio AI:
 *   POST /ai/process
 *   Body JSON: { "type": "llm", "prompt": "..." }
 *
 * Respuesta esperada:
 *   { success: true, type: "llm", response: string }
 *   o { success: false, type: "llm", error: string }
 *
 * UI: panel de chat flotante controlado por #kora-ai-toggle
 */

(function () {
  "use strict";

  // ─────────────────────────────────────────────
  // Configuración – cambia la URL según tu entorno
  // ─────────────────────────────────────────────
  const AI_BASE_URL = window.KORA_AI_BASE_URL || "http://localhost:8000";

  // ─────────────────────────────────────────────
  // Crear el panel de chat si no existe
  // ─────────────────────────────────────────────
  function ensureChatPanel() {
    if (document.getElementById("kora-chat-panel")) return;

    const panel = document.createElement("div");
    panel.id = "kora-chat-panel";
    panel.className = "kora-chat-panel";
    panel.setAttribute("aria-hidden", "true");
    panel.innerHTML = `
      <div class="kora-chat-panel__header">
        <span class="kora-chat-panel__title">Kora AI</span>
        <button type="button" id="kora-chat-close" class="kora-chat-panel__close" aria-label="Cerrar chat">×</button>
      </div>
      <div class="kora-chat-panel__messages" id="kora-chat-messages">
        <div class="kora-chat-msg kora-chat-msg--bot">
          <p>¡Hola! Soy Kora. ¿En qué puedo ayudarte con tu alimentación?</p>
        </div>
      </div>
      <form class="kora-chat-panel__form" id="kora-chat-form">
        <input
          type="text"
          id="kora-chat-input"
          class="kora-chat-panel__input"
          placeholder="Escribe tu mensaje…"
          autocomplete="off"
          required
        />
        <button type="submit" id="kora-chat-send" class="kora-chat-panel__send" aria-label="Enviar">
          ➤
        </button>
      </form>
    `;
    document.body.appendChild(panel);

    // Estilos mínimos inyectados (puedes moverlos a CSS)
    if (!document.getElementById("kora-chat-styles")) {
      const style = document.createElement("style");
      style.id = "kora-chat-styles";
      style.textContent = `
        .kora-chat-panel {
          position: fixed;
          bottom: 90px;
          right: 24px;
          width: 360px;
          max-width: calc(100vw - 32px);
          height: 480px;
          max-height: calc(100vh - 120px);
          background: #fff;
          border-radius: 16px;
          box-shadow: 0 12px 40px rgba(0,0,0,.18);
          display: flex;
          flex-direction: column;
          z-index: 9999;
          opacity: 0;
          transform: translateY(20px) scale(.96);
          pointer-events: none;
          transition: opacity .25s ease, transform .25s ease;
          overflow: hidden;
          font-family: system-ui, -apple-system, sans-serif;
        }
        .kora-chat-panel.is-open {
          opacity: 1;
          transform: translateY(0) scale(1);
          pointer-events: auto;
        }
        .kora-chat-panel__header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 16px;
          background: linear-gradient(135deg, #4CAF50, #2E7D32);
          color: #fff;
        }
        .kora-chat-panel__title {
          font-weight: 600;
          font-size: 1rem;
        }
        .kora-chat-panel__close {
          background: transparent;
          border: none;
          color: #fff;
          font-size: 1.5rem;
          line-height: 1;
          cursor: pointer;
          padding: 0 4px;
        }
        .kora-chat-panel__messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 10px;
          background: #f7f9f7;
        }
        .kora-chat-msg {
          max-width: 85%;
          padding: 10px 14px;
          border-radius: 14px;
          font-size: .9rem;
          line-height: 1.4;
        }
        .kora-chat-msg p { margin: 0; }
        .kora-chat-msg--bot {
          align-self: flex-start;
          background: #fff;
          border: 1px solid #e0e0e0;
          border-bottom-left-radius: 4px;
        }
        .kora-chat-msg--user {
          align-self: flex-end;
          background: #4CAF50;
          color: #fff;
          border-bottom-right-radius: 4px;
        }
        .kora-chat-msg--error {
          align-self: center;
          background: #ffebee;
          color: #c62828;
          font-size: .8rem;
        }
        .kora-chat-msg--loading {
          align-self: flex-start;
          background: #fff;
          border: 1px solid #e0e0e0;
          color: #888;
          font-style: italic;
        }
        .kora-chat-panel__form {
          display: flex;
          gap: 8px;
          padding: 12px;
          border-top: 1px solid #e8e8e8;
          background: #fff;
        }
        .kora-chat-panel__input {
          flex: 1;
          border: 1px solid #ccc;
          border-radius: 24px;
          padding: 10px 16px;
          font-size: .9rem;
          outline: none;
        }
        .kora-chat-panel__input:focus {
          border-color: #4CAF50;
        }
        .kora-chat-panel__send {
          width: 42px;
          height: 42px;
          border-radius: 50%;
          border: none;
          background: #4CAF50;
          color: #fff;
          font-size: 1.1rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }
        .kora-chat-panel__send:disabled {
          opacity: .5;
          cursor: not-allowed;
        }
      `;
      document.head.appendChild(style);
    }
  }

  // ─────────────────────────────────────────────
  // Inicialización
  // ─────────────────────────────────────────────
  ensureChatPanel();

  const toggleBtn = document.getElementById("kora-ai-toggle");
  const panel = document.getElementById("kora-chat-panel");
  const closeBtn = document.getElementById("kora-chat-close");
  const form = document.getElementById("kora-chat-form");
  const input = document.getElementById("kora-chat-input");
  const messagesBox = document.getElementById("kora-chat-messages");
  const sendBtn = document.getElementById("kora-chat-send");

  function openPanel() {
    if (!panel) return;
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    if (input) input.focus();
  }

  function closePanel() {
    if (!panel) return;
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
  }

  function togglePanel() {
    if (!panel) return;
    if (panel.classList.contains("is-open")) {
      closePanel();
    } else {
      openPanel();
    }
  }

  if (toggleBtn) {
    toggleBtn.addEventListener("click", togglePanel);
  }
  if (closeBtn) {
    closeBtn.addEventListener("click", closePanel);
  }

  // ─────────────────────────────────────────────
  // Envío de mensajes al LLM
  // ─────────────────────────────────────────────
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const prompt = (input.value || "").trim();
      if (!prompt) return;

      appendMessage(prompt, "user");
      input.value = "";
      setSending(true);

      const loadingEl = appendMessage("Pensando…", "loading");

      try {
        const response = await fetch(`${AI_BASE_URL}/ai/process`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            type: "llm",
            prompt: prompt,
          }),
        });

        if (!response.ok) {
          const errBody = await response.json().catch(() => ({}));
          throw new Error(
            errBody.detail || errBody.error || `Error HTTP ${response.status}`
          );
        }

        const data = await response.json();

        // Quitar el mensaje de "Pensando…"
        if (loadingEl && loadingEl.parentNode) {
          loadingEl.parentNode.removeChild(loadingEl);
        }

        if (!data.success) {
          throw new Error(data.error || "El agente no pudo responder.");
        }

        appendMessage(data.response || "(sin respuesta)", "bot");
      } catch (err) {
        console.error("[kora-llm]", err);
        if (loadingEl && loadingEl.parentNode) {
          loadingEl.parentNode.removeChild(loadingEl);
        }
        appendMessage("Error: " + (err.message || err), "error");
      } finally {
        setSending(false);
        if (input) input.focus();
      }
    });
  }

  // ─────────────────────────────────────────────
  // Helpers de UI
  // ─────────────────────────────────────────────
  function appendMessage(text, type) {
    if (!messagesBox) return null;
    const div = document.createElement("div");
    div.className = `kora-chat-msg kora-chat-msg--${type}`;
    const p = document.createElement("p");
    p.textContent = text;
    div.appendChild(p);
    messagesBox.appendChild(div);
    messagesBox.scrollTop = messagesBox.scrollHeight;
    return div;
  }

  function setSending(isSending) {
    if (sendBtn) sendBtn.disabled = isSending;
    if (input) input.disabled = isSending;
  }
})();
