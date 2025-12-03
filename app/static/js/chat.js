let socket = null;

// Called from chatroom.html
function connectWebSocket(roomId, userId) {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.host}/ws/chat/${roomId}?user_id=${userId}`;


    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("Connected to WebSocket");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Append message to the UI
        addMessageToList(data.username, data.content);
    };

    socket.onclose = () => {
        console.log("WebSocket closed");
    };

    socket.onerror = (err) => {
        console.log("WebSocket error:", err);
    };
}

function sendMessage() {
    const input = document.getElementById("messageInput");
    const content = input.value.trim();

    if (content === "") return;

    socket.send(content);

    input.value = "";
}

function addMessageToList(username, content) {
    const list = document.getElementById("messageList");

    const li = document.createElement("li");
    li.innerHTML = `<strong>${username}</strong>: ${content}`;

    list.appendChild(li);

    // Auto-scroll
    list.scrollTop = list.scrollHeight;
}
