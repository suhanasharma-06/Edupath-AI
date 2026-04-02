let currentStep = "start";
let stateData = {};

function addMessage(text, sender) {
    let chatBox = document.getElementById("chatBox");

    let msg = document.createElement("div");
    msg.className = "message " + sender;
    msg.innerHTML = text;

    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function clearOptions() {
    document.querySelectorAll(".option-btn").forEach(b => b.remove());
}

async function sendStep(step, value) {

    clearOptions();

    let res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({step, value, ...stateData})
    });

    let data = await res.json();

    addMessage(data.reply, "bot");

    if (data.next) currentStep = data.next;

    stateData = {...stateData, ...data};

    if (data.options) showOptions(data.options);
}

function showOptions(options) {
    let chatBox = document.getElementById("chatBox");

    let container = document.createElement("div");
    container.className = "options-container";

    options.forEach(opt => {
        let btn = document.createElement("button");
        btn.className = "option-btn";
        btn.innerText = opt;

        btn.onclick = () => {
            addMessage(opt, "user");
            sendStep(currentStep, opt);
        };

        container.appendChild(btn);
    });

    chatBox.appendChild(container);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
    let input = document.getElementById("userInput");
    let text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    sendStep(currentStep, text);
    input.value = "";
}

document.getElementById("userInput").addEventListener("keypress", e => {
    if (e.key === "Enter") sendMessage();
});

window.onload = () => sendStep("start","");

function startListening() {
    const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    rec.lang = "en-IN";

    rec.onresult = e => {
        document.getElementById("userInput").value = e.results[0][0].transcript;
        sendMessage();
    };

    rec.start();
}