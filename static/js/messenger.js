// Глобальные переменные
let currentChatId = null;
let currentOtherUserId = null;
let currentUserId = null;
let messagePolling = null;
let prevMessageCount = 0;

// DOM загружен
document.addEventListener('DOMContentLoaded', function() {
    const userIdElement = document.getElementById('currentUserId');
    if (userIdElement) {
        currentUserId = parseInt(userIdElement.value);
    }
    initSound();
});

// Простой звук
function initSound() {
    window.notifySound = new Audio();
    window.notifySound.src = 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=';
}

function playSound() {
    if (window.notifySound) {
        window.notifySound.play().catch(function() {});
    }
}

// Открытие чата
function openChat(chatId) {
    currentChatId = chatId;
    prevMessageCount = 0;
    
    const chatItem = document.querySelector('[data-chat-id="' + chatId + '"]');
    if (chatItem) {
        currentOtherUserId = parseInt(chatItem.getAttribute('data-other-user-id'));
    }
    
    document.querySelectorAll('.chat-item').forEach(function(item) {
        item.classList.remove('active');
    });
    if (chatItem) chatItem.classList.add('active');
    
    updateChatHeader();
    document.getElementById('inputArea').style.display = 'flex';
    document.getElementById('messageInput').focus();
    loadMessages(chatId);
    
    if (messagePolling) clearInterval(messagePolling);
    messagePolling = setInterval(function() { loadMessages(chatId); }, 2000);
    
    if (window.innerWidth <= 768) {
        document.getElementById('sidebar').style.transform = 'translateX(-100%)';
    }
}

function updateChatHeader() {
    if (!currentChatId || !currentOtherUserId) return;
    const chatItem = document.querySelector('[data-chat-id="' + currentChatId + '"]');
    if (chatItem) {
        document.getElementById('chatHeaderAvatar').innerHTML = chatItem.querySelector('.chat-avatar').innerHTML;
        document.getElementById('chatHeaderName').textContent = chatItem.querySelector('.chat-name').textContent.trim();
    }
}

// Загрузка сообщений
function loadMessages(chatId) {
    if (!chatId) return;
    
    fetch('/chat/' + chatId + '/')
        .then(function(response) { return response.json(); })
        .then(function(data) {
            const area = document.getElementById('messagesArea');
            const shouldScroll = area.scrollHeight - area.scrollTop - area.clientHeight < 100;
            
            // Уведомление о новых сообщениях
            if (data.messages && data.messages.length > prevMessageCount && prevMessageCount > 0) {
                const lastMsg = data.messages[data.messages.length - 1];
                if (lastMsg.sender_id !== currentUserId) {
                    playSound();
                    document.title = '🔔 Новое сообщение!';
                    setTimeout(function() { document.title = 'TeleWeb Messenger'; }, 3000);
                }
            }
            prevMessageCount = data.messages ? data.messages.length : 0;
            
            area.innerHTML = '';
            
            if (!data.messages || data.messages.length === 0) {
                area.innerHTML = '<div class="empty-chat"><div class="empty-icon">🔒</div><p>Нет сообщений</p></div>';
                return;
            }
            
            data.messages.forEach(function(msg) {
                const div = document.createElement('div');
                div.className = 'message ' + (msg.sender_id === currentUserId ? 'message-own' : 'message-other');
                
                let content = '';
                if (msg.type === 'image' && msg.file_url) {
                    content = '<img src="' + msg.file_url + '" style="max-width:200px;border-radius:8px;cursor:pointer" onclick="window.open(this.src)">';
                } else if (msg.type === 'video' && msg.file_url) {
                    content = '<video controls style="max-width:200px;border-radius:8px"><source src="' + msg.file_url + '"></video>';
                } else if (msg.type === 'file' && msg.file_url) {
                    content = '<a href="' + msg.file_url + '" target="_blank">📎 Скачать файл</a>';
                } else {
                    content = msg.text || '';
                }
                
                div.innerHTML = content + '<span class="message-time">' + (msg.timestamp || '') + '</span>';
                area.appendChild(div);
            });
            
            if (shouldScroll) area.scrollTop = area.scrollHeight;
        });
}

// Отправка сообщения
function sendMessage() {
    const input = document.getElementById('messageInput');
    const text = input.value.trim();
    if (!text || !currentChatId) return;
    
    fetch('/chat/' + currentChatId + '/send/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ text: text })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.status === 'ok') {
            input.value = '';
            loadMessages(currentChatId);
        }
    });
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
}

// Отправка файла
function sendFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file || !currentChatId) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/chat/' + currentChatId + '/send/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.status === 'ok') {
            fileInput.value = '';
            loadMessages(currentChatId);
        }
    });
}

// Поиск
function filterUsers() {
    const search = document.getElementById('userSearch').value.toLowerCase();
    document.querySelectorAll('.user-item').forEach(function(item) {
        const username = item.getAttribute('data-username') || '';
        item.style.display = username.includes(search) ? 'flex' : 'none';
    });
}

function startChat(userId) {
    window.location.href = '/start-chat/' + userId + '/';
}

// Эмодзи
function toggleEmojiPicker() {
    document.getElementById('emojiPicker').classList.toggle('active');
}

function insertEmoji(emoji) {
    document.getElementById('messageInput').value += emoji;
    document.getElementById('messageInput').focus();
    toggleEmojiPicker();
}

document.addEventListener('click', function(e) {
    if (!e.target.closest('.emoji-picker') && !e.target.closest('.emoji-btn')) {
        const picker = document.getElementById('emojiPicker');
        if (picker) picker.classList.remove('active');
    }
});

// Никнейм
function showNicknameModal() {
    if (!currentOtherUserId) { alert('Выберите чат'); return; }
    document.getElementById('nicknameModal').classList.add('active');
}

function closeModal() {
    document.getElementById('nicknameModal').classList.remove('active');
}

function saveNickname() {
    const nickname = document.getElementById('nicknameInput').value.trim();
    if (!nickname || !currentOtherUserId) return;
    
    fetch('/set-nickname/' + currentOtherUserId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: 'nickname=' + encodeURIComponent(nickname)
    }).then(function() {
        closeModal();
        location.reload();
    });
}

// Сайдбар
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar.style.transform === 'translateX(-100%)') {
        sidebar.style.transform = 'translateX(0)';
    } else {
        sidebar.style.transform = 'translateX(-100%)';
    }
}

// Вспомогательные
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        document.getElementById('sidebar').style.transform = 'translateX(0)';
    }
});
