// Backend base URL. On Vercel, /api/* is proxied to Railway (see vercel.json).
// For local testing you can override it: index.html?api=http://localhost:8000
const API_BASE = (() => {
  try {
    const override = new URLSearchParams(location.search).get("api");
    if (override) {
      localStorage.setItem("apiBase", override);
      return override.replace(/\/$/, "");
    }
    const saved = localStorage.getItem("apiBase");
    if (saved && (location.hostname === "localhost" || location.hostname === "127.0.0.1" || location.protocol === "file:")) {
      return saved.replace(/\/$/, "");
    }
  } catch (_) {}
  return "/api";
})();

const STORAGE_KEY = "mf-chat-history";

const $ = (id) => document.getElementById(id);
const messagesEl = $("messages");
const featuresEl = $("features");
const scrollEl = $("scroll");
const input = $("input");
const sendBtn = $("sendBtn");
const form = $("composer");

let history = [];
let busy = false;

// ---------- Rendering ----------
function renderMarkdown(text) {
  if (window.marked && window.DOMPurify) {
    return DOMPurify.sanitize(marked.parse(text, { breaks: true, gfm: true }));
  }
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML.replace(/\n/g, "<br>");
}

function sourceLabel(url) {
  try {
    const parts = new URL(url).pathname.split("/").filter(Boolean);
    return parts[parts.length - 1] || url;
  } catch (_) {
    return url;
  }
}

function addMessage(msg, { persist = true } = {}) {
  featuresEl.hidden = true;

  const row = document.createElement("div");
  row.className = `msg ${msg.role}${msg.error ? " error" : ""}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = msg.role === "user" ? "👤" : "🤖";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (msg.role === "user") {
    bubble.textContent = msg.content;
  } else {
    bubble.innerHTML = renderMarkdown(msg.content);
    bubble.querySelectorAll("a").forEach((a) => { a.target = "_blank"; a.rel = "noopener noreferrer"; });

    if (msg.sources && msg.sources.length) {
      const wrap = document.createElement("div");
      wrap.className = "sources";
      msg.sources.forEach((url) => {
        if (!/^https?:\/\//i.test(url)) return;
        const a = document.createElement("a");
        a.className = "source-tag";
        a.href = url;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.textContent = "🔗 " + sourceLabel(url);
        wrap.appendChild(a);
      });
      bubble.appendChild(wrap);
    }
    if (msg.footer) {
      const f = document.createElement("div");
      f.className = "footer-meta";
      f.textContent = "🕒 " + msg.footer;
      bubble.appendChild(f);
    }
  }

  row.append(avatar, bubble);
  messagesEl.appendChild(row);
  scrollToBottom();

  if (persist && !msg.error) {
    history.push(msg);
    saveHistory();
  }
  return row;
}

function addTyping() {
  const row = document.createElement("div");
  row.className = "msg assistant";
  row.innerHTML =
    '<div class="avatar">🤖</div><div class="bubble"><span class="typing"><span></span><span></span><span></span></span><span class="typing-label">Retrieving verified facts…</span></div>';
  messagesEl.appendChild(row);
  scrollToBottom();
  return row;
}

function scrollToBottom() {
  requestAnimationFrame(() => { scrollEl.scrollTop = scrollEl.scrollHeight; });
}

// ---------- Persistence (per-browser convenience only) ----------
function saveHistory() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(history.slice(-50))); } catch (_) {}
}

function loadHistory() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    if (Array.isArray(saved)) saved.forEach((m) => addMessage(m, { persist: false }));
    history = Array.isArray(saved) ? saved : [];
  } catch (_) { history = []; }
}

// ---------- API ----------
async function ask(query) {
  if (busy || !query.trim()) return;
  busy = true;
  sendBtn.disabled = true;

  addMessage({ role: "user", content: query });
  const typing = addTyping();

  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) {
      let detail = `${res.status} ${res.statusText}`;
      try { const j = await res.json(); if (j.detail) detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail); } catch (_) {}
      throw new Error(detail);
    }
    const data = await res.json();
    typing.remove();
    addMessage({ role: "assistant", content: data.answer, sources: data.sources, footer: data.footer });
  } catch (err) {
    typing.remove();
    addMessage({ role: "assistant", error: true, content: `Error processing request: ${err.message}. The backend may be waking up — try again in a moment.` }, { persist: false });
  } finally {
    busy = false;
    sendBtn.disabled = false;
    input.focus();
  }
}

async function checkHealth() {
  const status = $("status");
  const text = $("statusText");
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error();
    status.className = "status ok";
    text.textContent = "ChromaDB connected · Facts verified";
    try {
      const info = await (await fetch(`${API_BASE}/info`)).json();
      if (info.llm_model) $("llmModel").textContent = info.llm_model;
      if (info.embedding_model) $("embModel").textContent = info.embedding_model.split("/").pop();
    } catch (_) {}
  } catch (_) {
    status.className = "status down";
    text.textContent = "Backend unavailable";
  }
}

// ---------- Events ----------
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  input.value = "";
  autoGrow();
  ask(q);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

function autoGrow() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 160) + "px";
}
input.addEventListener("input", autoGrow);

$("quickList").addEventListener("click", (e) => {
  const btn = e.target.closest(".quick-btn");
  if (!btn) return;
  closeSidebar();
  ask(btn.textContent.trim());
});

$("clearBtn").addEventListener("click", () => {
  history = [];
  saveHistory();
  messagesEl.innerHTML = "";
  featuresEl.hidden = false;
  closeSidebar();
});

const sidebar = $("sidebar");
const scrim = $("scrim");
function openSidebar() { sidebar.classList.add("open"); scrim.classList.add("open"); }
function closeSidebar() { sidebar.classList.remove("open"); scrim.classList.remove("open"); }
$("openSidebar").addEventListener("click", openSidebar);
$("closeSidebar").addEventListener("click", closeSidebar);
scrim.addEventListener("click", closeSidebar);

loadHistory();
checkHealth();
