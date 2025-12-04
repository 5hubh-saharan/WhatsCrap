let socket = null;
let heartbeatInterval = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectDelay = 3000;
let currentUserId = null;
let currentUsername = null;

const WS_STATE = {
    CONNECTING: 0,
    OPEN: 1,
    CLOSING: 2,
    CLOSED: 3
};

function connectWebSocket(roomId, userId, username) {
    currentUserId = userId;
    currentUsername = username;
    
    if (socket && socket.readyState === WS_STATE.OPEN) {
        return;
    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.host}/ws/chat/${roomId}?user_id=${userId}`;

    socket = new WebSocket(wsUrl);
    reconnectAttempts = 0;

    setupWebSocketHandlers(roomId, userId);
    setupMessageForm();
}

function setupWebSocketHandlers(roomId, userId) {
    socket.onopen = () => {
        console.log("✅ WebSocket connected");
        reconnectAttempts = 0;
        startHeartbeat();
        updateConnectionStatus(true);
        showSystemMessage("Connected to chat room");
    };

    socket.onmessage = (event) => {
        const data = event.data;
        
        // 首先检查是否是纯文本的心跳消息
        if (data === "PONG") {
            return; // 忽略心跳响应
        }
        
        // 尝试解析JSON
        try {
            const jsonData = JSON.parse(data);
            
            // 处理系统消息
            if (jsonData.type === "system" && jsonData.message) {
                showSystemMessage(jsonData.message);
                return;
            }
            
            // 处理聊天消息
            if (jsonData.type === "message" && jsonData.content) {
                const isOwnMessage = jsonData.user_id === currentUserId;
                addMessageToList(jsonData.username, jsonData.content, jsonData.created_at, isOwnMessage);
                return;
            }
            
            // 处理旧格式的消息（兼容）
            if (jsonData.content && jsonData.username) {
                const isOwnMessage = jsonData.user_id === currentUserId;
                addMessageToList(jsonData.username, jsonData.content, jsonData.created_at, isOwnMessage);
                return;
            }
            
            // 如果到这里，说明是未知格式的JSON，忽略它
            console.log("Received unknown JSON format:", jsonData);
            
        } catch (error) {
            // 不是JSON，检查是否是纯文本消息
            const text = data.trim();
            
            if (text === "") {
                return; // 忽略空消息
            }
            
            if (text.includes("heartbeat") || text.includes("HEARTBEAT") || text === "PONG") {
                return; // 忽略心跳相关消息
            }
            
            if (text.includes("system") || text.includes("connected") || text.includes("disconnected")) {
                return; // 忽略系统消息
            }
            
            // 如果是纯文本聊天消息
            console.log("Received plain text message:", text);
            addMessageToList("User", text, new Date().toISOString(), false);
        }
    };

    socket.onclose = (event) => {
        console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
        stopHeartbeat();
        updateConnectionStatus(false);
        showSystemMessage("Disconnected from chat");
        
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
            setTimeout(() => {
                reconnectAttempts++;
                console.log(`Reconnecting... Attempt ${reconnectAttempts}`);
                connectWebSocket(roomId, currentUserId, currentUsername);
            }, reconnectDelay);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        stopHeartbeat();
        updateConnectionStatus(false);
        showSystemMessage("Connection error");
    };
}

function setupMessageForm() {
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const messageError = document.getElementById('messageError');
    
    if (!messageForm || !messageInput) return;
    
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
        
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    messageInput.addEventListener('input', function() {
        if (messageError.textContent) {
            messageError.textContent = '';
            messageError.classList.remove('error');
        }
        
        const hasContent = messageInput.value.trim().length > 0;
        sendButton.disabled = !hasContent;
    });
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const messageError = document.getElementById('messageError');
    const sendButton = document.getElementById('sendButton');
    const content = messageInput.value.trim();

    if (!content) {
        messageError.textContent = 'Message cannot be empty';
        messageError.classList.add('error');
        messageInput.focus();
        return;
    }
    
    if (content.length > 1000) {
        messageError.textContent = 'Message is too long (max 1000 characters)';
        messageError.classList.add('error');
        messageInput.focus();
        return;
    }

    if (!socket || socket.readyState !== WS_STATE.OPEN) {
        messageError.textContent = 'Not connected to chat server';
        messageError.classList.add('error');
        return;
    }

    try {
        // 发送纯文本消息
        socket.send(content);
        
        // 清空输入框
        messageInput.value = '';
        
        // 重置按钮状态
        if (sendButton) sendButton.disabled = true;
        
        // 清空错误信息
        if (messageError) {
            messageError.textContent = '';
            messageError.classList.remove('error');
        }
        
        // 自动聚焦输入框
        messageInput.focus();
        
    } catch (error) {
        console.error("Failed to send message:", error);
        messageError.textContent = 'Failed to send message';
        messageError.classList.add('error');
    }
}

function startHeartbeat() {
    stopHeartbeat();
    
    heartbeatInterval = setInterval(() => {
        if (socket && socket.readyState === WS_STATE.OPEN) {
            // 发送简单的心跳字符串
            socket.send("PING");
        }
    }, 25000);
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
}

function addMessageToList(username, content, timestamp = null, isOwnMessage = false) {
    const list = document.getElementById("messageList");
    if (!list) return;

    const li = document.createElement("li");
    li.classList.add("message-item");
    li.classList.add(isOwnMessage ? "my-message" : "other-message");
    
    let timeString = '';
    if (timestamp) {
        try {
            const date = new Date(timestamp);
            timeString = date.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        } catch (e) {
            timeString = new Date().toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }
    } else {
        timeString = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    // 构建消息气泡
    let usernameHtml = '';
    if (isOwnMessage) {
        usernameHtml = `<strong class="message-username">You</strong>`;
    } else {
        usernameHtml = `<strong class="message-username">${escapeHtml(username)}</strong>`;
    }
    
    li.innerHTML = `
        <div class="message-bubble">
            <div class="message-header">
                ${!isOwnMessage ? usernameHtml : ''}
                <span class="message-time">${timeString}</span>
                ${isOwnMessage ? usernameHtml : ''}
            </div>
            <div class="message-content">${escapeHtml(content)}</div>
        </div>
    `;

    list.appendChild(li);
    list.scrollTop = list.scrollHeight;
    
    li.classList.add("new-message");
    setTimeout(() => li.classList.remove("new-message"), 300);
}

function showSystemMessage(message) {
    const list = document.getElementById("messageList");
    if (!list) return;

    const li = document.createElement("li");
    li.classList.add("message-item");
    li.classList.add("system-message");
    
    li.innerHTML = `
        <div class="system-bubble">
            <div class="system-content">${escapeHtml(message)}</div>
        </div>
    `;

    list.appendChild(li);
    list.scrollTop = list.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function updateConnectionStatus(isConnected) {
    const connectionIndicator = document.getElementById('connectionIndicator');
    if (connectionIndicator) {
        connectionIndicator.className = `connection-indicator ${isConnected ? 'connected' : 'disconnected'}`;
        connectionIndicator.title = isConnected ? 'Connected' : 'Disconnected';
    }
}

// 页面事件
document.addEventListener('keydown', function(e) {
    if (e.key === '/' && document.activeElement !== document.getElementById('messageInput')) {
        e.preventDefault();
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.focus();
        }
    }
});

window.addEventListener('beforeunload', function() {
    if (socket) {
        socket.close(1000, "User left the page");
    }
    stopHeartbeat();
});