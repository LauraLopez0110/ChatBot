const form = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');

form.addEventListener('submit', async (e) =>{
    e.preventDefault();

    const questionInput = document.getElementById('question');
    const userText = questionInput.value.trim();

    if(!userText) return; // Solo si el texto está vacio

    appendMessage(userText, 'user-message');
    questionInput.value = '';

    chatBox.scrollTop = chatBox.scrollHeight;

    const botMessageDiv = appendMessage("", "bot-message");

    try{
        const response = await fetch('/ask',{
            method:"POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: userText})
        });
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');

        while(true){
            const {done, value} = await reader.read();
            if(done) break;

            const chunk = decoder.decode(value);

            botMessageDiv.textContent += chunk;

            chatBox.scrollTop = chatBox.scrollHeight;
        }
    } catch (error){
        botMessageDiv.textContent = "Error en la conexión";
    }
});

function appendMessage(text, className){
    const messageDiv = document.createElement('div');

    messageDiv.className = `chat-message ${className}`;
    messageDiv.textContent = text;
    
    chatBox.appendChild(messageDiv);

    return messageDiv;
}

// Función para agregar un nuevo mensaje (del usuario o del bot) al chat
function appendMessage(text, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${className}`;
    messageDiv.textContent = text;
    chatBox.appendChild(messageDiv);
    return messageDiv;
}

//const resetBtn = document.createElement = getElementById("reset-btn");
const resetBtn = document.getElementById("reset-btn");

resetBtn.addEventListener("click", async() => {
    await fetch("/reset", {method: 'POST'})

    // Limpiar visualmente el chat-box
    document.getElementById("chat-box").innerHTML = '';

    appendMessage("Conversacion reiniciada", "bot-message");
});

// Mostrar/ocultar la sección de gestión de PDFs
const toggleBtn = document.getElementById("toggle-pdf-section");
const pdfSection = document.getElementById("pdf-section");

toggleBtn.addEventListener("click", () => {
    if (pdfSection.style.display === "none") {
        pdfSection.style.display = "block";
        toggleBtn.textContent = "Ocultar Gestión de PDFs";
    } else {
        pdfSection.style.display = "none";
        toggleBtn.textContent = "Mostrar Gestión de PDFs";
    }
});