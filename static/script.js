const translateButton = document.getElementById("translateButton");
const refreshHistoryButton = document.getElementById("refreshHistoryButton");
const clearButton = document.getElementById("clearButton");
const copyButton = document.getElementById("copyButton");


// Translation
translateButton.addEventListener("click", async () => {
    const text = document.getElementById("sourceText").value.trim();
    const targetLanguage = document.getElementById("targetLanguage").value;

    const result = document.getElementById("translationResult");
    const languageInfo = document.getElementById("languageInfo");
    const tokenInfo = document.getElementById("tokenInfo");

    if (!text) {
        result.textContent = "Please enter some text.";
        languageInfo.innerHTML = "<strong>Detected Language:</strong> -";
        tokenInfo.innerHTML = "<strong>NLP Tokens:</strong> -";
        return;
    }

    result.textContent = "Translating...";
    languageInfo.innerHTML =
        "<strong>Detected Language:</strong> Detecting...";
    tokenInfo.innerHTML =
        "<strong>NLP Tokens:</strong> Processing...";

    try {
        const response = await fetch("/translate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: text,
                target_language: targetLanguage
            })
        });

        const data = await response.json();

        if (!response.ok) {
            result.textContent = data.error || "Translation failed.";
            languageInfo.innerHTML =
                "<strong>Detected Language:</strong> -";
            tokenInfo.innerHTML =
                "<strong>NLP Tokens:</strong> -";
            return;
        }

        result.textContent = data.translation;

        languageInfo.innerHTML =
            `<strong>Detected Language:</strong> ${data.detected_language}`;

        tokenInfo.innerHTML =
            `<strong>NLP Tokens:</strong> ${data.tokens.join(", ")}`;

        // Refresh history after successful translation
        loadHistory();

    } catch (error) {
        result.textContent = "Unable to connect to the server.";
        languageInfo.innerHTML =
            "<strong>Detected Language:</strong> -";
        tokenInfo.innerHTML =
            "<strong>NLP Tokens:</strong> -";

        console.error(error);
    }
});


// Clear button — resets the form
clearButton.addEventListener("click", () => {
    document.getElementById("sourceText").value = "";

    document.getElementById("translationResult").textContent =
        "Your translation will appear here.";

    document.getElementById("languageInfo").innerHTML =
        "<strong>Detected Language:</strong> -";

    document.getElementById("tokenInfo").innerHTML =
        "<strong>NLP Tokens:</strong> -";

    document.getElementById("sourceText").focus();
});


// Copy button — copies translation to clipboard
copyButton.addEventListener("click", async () => {
    const result = document.getElementById("translationResult");
    const text = result.textContent.trim();

    if (
        !text ||
        text === "Your translation will appear here." ||
        text === "Translating..."
    ) {
        return;
    }

    try {
        await navigator.clipboard.writeText(text);

        const originalText = copyButton.textContent;
        copyButton.textContent = "Copied!";

        setTimeout(() => {
            copyButton.textContent = originalText;
        }, 1500);

    } catch (error) {
        console.error("Copy failed:", error);
    }
});


// Load translation history
async function loadHistory() {
    const historyContainer =
        document.getElementById("historyContainer");

    historyContainer.innerHTML =
        '<div class="history-empty">Loading history...</div>';

    try {
        const response = await fetch("/history");
        const data = await response.json();

        if (!response.ok) {
            historyContainer.innerHTML =
                '<div class="history-empty">Unable to load history.</div>';
            return;
        }

        if (!data.history || data.history.length === 0) {
            historyContainer.innerHTML =
                '<div class="history-empty">No translation history available.</div>';
            return;
        }

        historyContainer.innerHTML = "";

        data.history.forEach(item => {
            const historyItem = document.createElement("div");
            historyItem.className = "history-item";

            historyItem.innerHTML = `
                <div class="history-text">
                    <div class="history-source">
                        ${escapeHtml(item.source_text)}
                    </div>

                    <div class="history-arrow">
                        ↓
                    </div>

                    <div class="history-translation">
                        ${escapeHtml(item.translated_text)}
                    </div>
                </div>

                <div class="history-details">
                    <span>
                        ${escapeHtml(item.source_language)}
                    </span>

                    <span>→</span>

                    <span>
                        ${escapeHtml(getLanguageName(item.target_language))}
                    </span>

                    <span class="history-date">
                        ${escapeHtml(item.created_at)}
                    </span>
                </div>
            `;

            historyContainer.appendChild(historyItem);
        });

    } catch (error) {
        historyContainer.innerHTML =
            '<div class="history-empty">Unable to connect to the server.</div>';

        console.error(error);
    }
}


// Refresh history button
refreshHistoryButton.addEventListener("click", () => {
    loadHistory();
});


// Convert language code to language name
function getLanguageName(code) {
    const languages = {
        "en": "English",
        "te": "Telugu",
        "kn": "Kannada"
    };

    return languages[code] || code;
}


// Prevent HTML from being inserted into the page
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


// Load history when the page opens
loadHistory();