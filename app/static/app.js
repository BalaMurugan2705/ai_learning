const chat = document.getElementById("chat");
const emptyState = document.getElementById("emptyState");
const composer = document.getElementById("composer");
const questionInput = document.getElementById("question");
const askButton = document.getElementById("askButton");

const USER_AVATAR = `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="8" r="3.2" stroke="currentColor" stroke-width="1.6"/>
        <path d="M5 20c1.2-3.5 4-5.2 7-5.2s5.8 1.7 7 5.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
    </svg>
`;

const BOT_AVATAR = `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2l2 4 4 .6-3 3 .7 4.2L12 12l-3.7 1.8L9 9.6l-3-3L10 6l2-4z" fill="currentColor"/>
    </svg>
`;

const COPY_ICON = `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="9" y="9" width="11" height="11" rx="2" stroke="currentColor" stroke-width="1.6"/>
        <path d="M5 15V5a2 2 0 012-2h10" stroke="currentColor" stroke-width="1.6"/>
    </svg>
`;

const CHECK_ICON = `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
`;

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function renderCodeBlock(lang, code) {
    return `
        <div class="code-block">
            <div class="code-block-header">
                <span class="code-block-lang">${escapeHtml(lang || "text")}</span>
                <button type="button" class="copy-button">
                    ${COPY_ICON}
                    <span>Copy</span>
                </button>
            </div>
            <pre><code>${escapeHtml(code)}</code></pre>
        </div>
    `;
}

// A small, dependency-free markdown renderer. The generator only ever
// produces bold text, inline code, code fences, and simple lists, so this
// covers what actually shows up without pulling in a library.
function renderMarkdown(raw) {
    const codeBlocks = [];

    let text = raw.replace(/```(\w*)\n([\s\S]*?)```/g, function (match, lang, code) {
        const index = codeBlocks.length;
        codeBlocks.push({ lang, code: code.trim() });
        return "CODEBLOCK_MARKER_" + index;
    });

    text = escapeHtml(text);

    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
    text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

    const lines = text.split("\n");
    let html = "";
    let inList = false;

    for (const line of lines) {
        const trimmed = line.trim();
        const codeBlockMatch = trimmed.match(/^CODEBLOCK_MARKER_(\d+)$/);

        if (codeBlockMatch) {
            if (inList) {
                html += "</ul>";
                inList = false;
            }
            const block = codeBlocks[Number(codeBlockMatch[1])];
            html += renderCodeBlock(block.lang, block.code);
            continue;
        }

        const listMatch = line.match(/^\s*[-*]\s+(.*)$/);

        if (listMatch) {
            if (!inList) {
                html += "<ul>";
                inList = true;
            }
            html += "<li>" + listMatch[1] + "</li>";
            continue;
        }

        if (inList) {
            html += "</ul>";
            inList = false;
        }

        if (trimmed === "") {
            html += "<br>";
        } else {
            html += "<p>" + line + "</p>";
        }
    }

    if (inList) {
        html += "</ul>";
    }

    return html;
}

function scrollToBottom() {
    chat.scrollTop = chat.scrollHeight;
}

function hideEmptyState() {
    if (emptyState) {
        emptyState.style.display = "none";
    }
}

function addUserMessage(question) {
    hideEmptyState();

    const message = document.createElement("div");
    message.className = "message message-user";
    message.innerHTML = `
        <div class="avatar">${USER_AVATAR}</div>
        <div class="bubble-wrap"><div class="bubble">${escapeHtml(question)}</div></div>
    `;

    chat.appendChild(message);
    scrollToBottom();
}

function addPendingAssistantMessage() {
    hideEmptyState();

    const message = document.createElement("div");
    message.className = "message message-assistant";
    message.innerHTML = `
        <div class="avatar">${BOT_AVATAR}</div>
        <div class="bubble-wrap">
            <div class="bubble pending">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        </div>
    `;

    chat.appendChild(message);
    scrollToBottom();

    return message;
}

function renderSources(sources) {
    if (!sources || sources.length === 0) {
        return "";
    }

    const chips = sources
        .map((source, index) => {
            const section = source.section || "Not specified";
            return `
                <details class="source-chip">
                    <summary>[${index + 1}] ${escapeHtml(source.source_file)}</summary>
                    <div class="source-detail">
                        <div><span>Chunk</span>${escapeHtml(source.chunk_id)}</div>
                        <div><span>Page</span>${escapeHtml(source.page_id)}</div>
                        <div><span>Section</span>${escapeHtml(section)}</div>
                    </div>
                </details>
            `;
        })
        .join("");

    return `<div class="sources">${chips}</div>`;
}

function fillAssistantMessage(messageElement, answer, sources, isError) {
    const bubble = messageElement.querySelector(".bubble");
    bubble.classList.remove("pending");

    if (isError) {
        bubble.classList.add("error");
        bubble.innerHTML = `<p>${escapeHtml(answer)}</p>`;
        return;
    }

    bubble.innerHTML = renderMarkdown(answer) + renderSources(sources);
    scrollToBottom();
}

async function askQuestion() {
    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    addUserMessage(question);

    questionInput.value = "";
    autoResizeTextarea();

    askButton.disabled = true;
    const pendingMessage = addPendingAssistantMessage();

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                sdk_version: selectedSdkVersion || null
            })
        });

        const data = await response.json();

        if (!response.ok) {
            fillAssistantMessage(pendingMessage, data.detail || "Something went wrong.", null, true);
            return;
        }

        fillAssistantMessage(pendingMessage, data.answer, data.sources, false);

    } catch (error) {
        fillAssistantMessage(
            pendingMessage,
            "Unable to connect to the server.",
            null,
            true
        );
        console.error(error);

    } finally {
        askButton.disabled = false;
    }
}

function startNewChat() {
    chat.innerHTML = "";
    chat.appendChild(emptyState);
    emptyState.style.display = "";
}

function autoResizeTextarea() {
    questionInput.style.height = "auto";
    questionInput.style.height = `${Math.min(questionInput.scrollHeight, 160)}px`;
}

composer.addEventListener("submit", askQuestion);

questionInput.addEventListener("input", autoResizeTextarea);

questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        askQuestion();
    }
});

document.querySelectorAll(".example-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
        questionInput.value = chip.textContent.trim();
        autoResizeTextarea();
        askQuestion();
    });
});

// Copy-to-clipboard on generated code blocks (event delegation, since
// bubbles are rendered dynamically after the listener is attached).
chat.addEventListener("click", (event) => {
    const button = event.target.closest(".copy-button");

    if (!button) {
        return;
    }

    const code = button.closest(".code-block").querySelector("code").textContent;

    navigator.clipboard.writeText(code).then(() => {
        const originalHtml = button.innerHTML;
        button.innerHTML = `${CHECK_ICON}<span>Copied</span>`;

        setTimeout(() => {
            button.innerHTML = originalHtml;
        }, 1500);
    });
});

// --- Upload (drag & drop + click-to-browse) ---

const dropZone = document.getElementById("dropZone");
const dropZoneLabel = document.getElementById("dropZoneLabel");
const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");

const DEFAULT_DROP_ZONE_LABEL = dropZoneLabel.innerHTML;

async function uploadDocument(file) {
    if (!file) {
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    dropZone.classList.add("is-busy");
    dropZoneLabel.innerHTML = `<strong>Uploading ${escapeHtml(file.name)}...</strong>`;
    uploadStatus.textContent = "";
    uploadStatus.className = "status";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            uploadStatus.textContent = data.detail || "Upload failed.";
            uploadStatus.className = "status is-error";
            return;
        }

        uploadStatus.textContent = `${data.message} ${data.filename}: ${data.chunks_indexed} chunks created.`;
        uploadStatus.className = "status is-success";

    } catch (error) {
        uploadStatus.textContent = "Unable to connect to the server.";
        uploadStatus.className = "status is-error";
        console.error(error);

    } finally {
        dropZone.classList.remove("is-busy");
        dropZoneLabel.innerHTML = DEFAULT_DROP_ZONE_LABEL;
        fileInput.value = "";
    }
}

fileInput.addEventListener("change", () => {
    uploadDocument(fileInput.files[0]);
});

["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.add("is-dragover");
    });
});

["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.remove("is-dragover");
    });
});

dropZone.addEventListener("drop", (event) => {
    uploadDocument(event.dataTransfer.files[0]);
});

// --- SDK version filter (segmented control) ---

const sdkVersionGroup = document.getElementById("sdkVersionGroup");
let selectedSdkVersion = "";

sdkVersionGroup.addEventListener("click", (event) => {
    const button = event.target.closest(".segmented-option");

    if (!button) {
        return;
    }

    selectedSdkVersion = button.dataset.value;

    sdkVersionGroup.querySelectorAll(".segmented-option").forEach((option) => {
        option.classList.toggle("is-active", option === button);
    });
});

// --- Theme toggle (persisted, defaults to system preference) ---

const THEME_STORAGE_KEY = "docs-assistant-theme";
const themeToggle = document.getElementById("themeToggle");
const rootElement = document.documentElement;

function systemPrefersDark() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function applyStoredTheme() {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);

    if (stored) {
        rootElement.setAttribute("data-theme", stored);
    }
}

themeToggle.addEventListener("click", () => {
    const active = rootElement.getAttribute("data-theme") || (systemPrefersDark() ? "dark" : "light");
    const next = active === "dark" ? "light" : "dark";

    rootElement.setAttribute("data-theme", next);
    localStorage.setItem(THEME_STORAGE_KEY, next);
});

applyStoredTheme();
