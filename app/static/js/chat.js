let socket = null;
let heartbeatInterval = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectDelay = 3000; // 3秒

// 心跳配置
const HEARTBEAT_INTERVAL = 25000; // 25秒发送一次心跳
const HEARTBEAT_TIMEOUT = 30000;  // 30秒无响应视为超时
let lastHeartbeat = null;

// WebSocket 状态
const WS_STATE = {
    CONNECTING: 0,
    OPEN: 1,
    CLOSING: 2,
    CLOSED: 3
};

function connectWebSocket(roomId, userId) {
    if (socket && socket.readyState === WS_STATE.OPEN) {
        console.log("WebSocket already connected");
        return;
    }

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.host}/ws/chat/${roomId}?user_id=${userId}`;

    console.log(`Connecting to WebSocket: ${wsUrl}`);
    
    socket = new WebSocket(wsUrl);
    reconnectAttempts = 0;

    setupWebSocketHandlers(roomId, userId);
    setupMessageForm();
}

function setupWebSocketHandlers(roomId, userId) {
    socket.onopen = () => {
        console.log("✅ WebSocket connected successfully");
        reconnectAttempts = 0;
        
        // 启动心跳
        startHeartbeat();
        
        // 发送连接确认
        sendSystemMessage("connected");
        
        // 更新UI状态
        updateConnectionStatus(true);
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            // 处理系统消息
            if (data.type === "system") {
                console.log(`System: ${data.message}`);
                showNotification(data.message, "info");
                return;
            }
            
            // 处理心跳
            if (data.type === "heartbeat" || data.type === "heartbeat_ack") {
                lastHeartbeat = Date.now();
                console.log("❤️ Heartbeat received");
                return;
            }
            
            // 处理聊天消息
            if (data.type === "message") {
                addMessageToList(data.username, data.content, data.created_at);
                return;
            }
            
            // 默认处理为普通消息
            addMessageToList(data.username || "Unknown", data.content || event.data, new Date().toISOString());
            
        } catch (error) {
            // 如果不是JSON，当作纯文本消息处理
            console.log("Received plain text message:", event.data);
            addMessageToList("System", event.data, new Date().toISOString());
        }
    };

    socket.onclose = (event) => {
        console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
        stopHeartbeat();
        updateConnectionStatus(false);
        
        // 显示断开连接消息
        showNotification("Disconnected from chat. Attempting to reconnect...", "warning");
        
        // 自动重连（如果不是正常关闭）
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
            setTimeout(() => {
                reconnectAttempts++;
                console.log(`Reconnecting... Attempt ${reconnectAttempts}`);
                connectWebSocket(roomId, userId);
            }, reconnectDelay);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        showNotification("Connection error. Check your network.", "error");
        stopHeartbeat();
        updateConnectionStatus(false);
    };
}

function setupMessageForm() {
    const messageForm = document.getElementById('messageForm');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const messageError = document.getElementById('messageError');
    
    if (!messageForm || !messageInput) return;
    
    // 表单提交事件
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        sendMessage();
    });
    
    // 输入框键盘事件
    messageInput.addEventListener('keydown', function(e) {
        // 阻止回车键的默认行为（提交表单），但我们已经在submit事件中处理了
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
        
        // Ctrl+Enter 或 Cmd+Enter 发送
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 输入框输入事件
    messageInput.addEventListener('input', function() {
        if (messageError.textContent) {
            messageError.textContent = '';
            messageError.classList.remove('error');
        }
        
        // 动态调整按钮状态
        const hasContent = messageInput.value.trim().length > 0;
        sendButton.disabled = !hasContent;
    });
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const messageError = document.getElementById('messageError');
    const sendButton = document.getElementById('sendButton');
    const content = messageInput.value.trim();

    // 验证消息内容
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
        showNotification("Not connected to chat server", "error");
        return;
    }

    try {
        // 发送消息
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
        showNotification("Failed to send message", "error");
    }
}

function startHeartbeat() {
    // 清除已有的心跳定时器
    stopHeartbeat();
    
    // 重置心跳时间
    lastHeartbeat = Date.now();
    
    // 发送心跳的定时器
    heartbeatInterval = setInterval(() => {
        if (socket && socket.readyState === WS_STATE.OPEN) {
            // 检查是否超时
            if (Date.now() - lastHeartbeat > HEARTBEAT_TIMEOUT) {
                console.warn("Heartbeat timeout, reconnecting...");
                socket.close(1006, "Heartbeat timeout");
                return;
            }
            
            // 发送心跳
            socket.send(JSON.stringify({
                type: "heartbeat",
                timestamp: new Date().toISOString()
            }));
        }
    }, HEARTBEAT_INTERVAL);
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
}

function sendSystemMessage(type) {
    if (socket && socket.readyState === WS_STATE.OPEN) {
        socket.send(JSON.stringify({
            type: "system",
            action: type,
            timestamp: new Date().toISOString()
        }));
    }
}

function addMessageToList(username, content, timestamp = null) {
    const list = document.getElementById("messageList");
    if (!list) return;

    const li = document.createElement("li");
    li.classList.add("message-item");
    
    // 格式化时间
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
    
    li.innerHTML = `
        <div class="message-header">
            <strong class="message-username">${escapeHtml(username)}</strong>
            <span class="message-time">${timeString}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;

    list.appendChild(li);
    
    // 自动滚动到底部
    list.scrollTop = list.scrollHeight;
    
    // 添加新消息动画
    li.classList.add("new-message");
    setTimeout(() => li.classList.remove("new-message"), 300);
    
    // 如果用户不在底部，显示新消息提示
    const isScrolledToBottom = list.scrollHeight - list.clientHeight <= list.scrollTop + 50;
    if (!isScrolledToBottom) {
        showNewMessageNotification();
    }
}

function showNewMessageNotification() {
    // 可以在这里添加新消息通知，例如显示一个小图标
    const notification = document.createElement('div');
    notification.className = 'new-message-notification';
    notification.textContent = 'New message';
    notification.onclick = () => {
        const list = document.getElementById("messageList");
        if (list) {
            list.scrollTop = list.scrollHeight;
        }
        notification.remove();
    };
    
    // 移除已有的通知
    const existing = document.querySelector('.new-message-notification');
    if (existing) existing.remove();
    
    document.body.appendChild(notification);
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 显示通知
function showNotification(message, type = "info") {
    // 简单的控制台日志
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // 可以在这里实现更美观的通知系统
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// 更新连接状态
function updateConnectionStatus(isConnected) {
    const connectionIndicator = document.getElementById('connectionIndicator');
    if (!connectionIndicator) {
        // 如果没有连接指示器，创建一个
        const navRight = document.querySelector('.nav-right');
        if (navRight) {
            const indicator = document.createElement('div');
            indicator.id = 'connectionIndicator';
            indicator.className = `connection-indicator ${isConnected ? 'connected' : 'disconnected'}`;
            indicator.title = isConnected ? 'Connected' : 'Disconnected';
            indicator.innerHTML = `<span class="indicator-dot"></span>`;
            navRight.insertBefore(indicator, navRight.firstChild);
        }
    } else {
        connectionIndicator.className = `connection-indicator ${isConnected ? 'connected' : 'disconnected'}`;
        connectionIndicator.title = isConnected ? 'Connected' : 'Disconnected';
    }
}

// 页面可见性变化时检查连接
document.addEventListener('visibilitychange', function() {
    if (!document.hidden && socket && socket.readyState !== WS_STATE.OPEN) {
        console.log("Page became visible, checking connection...");
        // 可以在这里触发重连
    }
});

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (socket) {
        socket.close(1000, "User left the page");
    }
    stopHeartbeat();
});

// 键盘快捷键
document.addEventListener('keydown', function(e) {
    // Ctrl+K 或 Cmd+K 聚焦到消息输入框
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.focus();
            messageInput.select();
        }
    }
    
    // Esc 键清除输入框
    if (e.key === 'Escape') {
        const messageInput = document.getElementById('messageInput');
        if (messageInput && messageInput === document.activeElement) {
            messageInput.value = '';
            messageInput.blur();
        }
    }
});