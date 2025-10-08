const socket = io();
const messages = document.getElementById('messages');
const loginSection = document.getElementById('login-section');
const gameSection = document.getElementById('game-section');
const usernameInput = document.getElementById('username-input');
const joinBtn = document.getElementById('join-btn');
const guessInput = document.getElementById('guess-input');
const guessBtn = document.getElementById('guess-btn');
const chatInput = document.getElementById('chat-input');
const chatBtn = document.getElementById('chat-btn');
const currentUserElement = document.getElementById('current-user');

let currentUsername = '';

// Function to display messages in the chat area
function addMessage(msg, type = 'system') {
    const div = document.createElement('div');
    div.className = `message ${type}`;
    
    const time = new Date().toLocaleTimeString();
    const user = msg.user || 'System';
    const text = msg.text || msg.message || '';
    
    div.innerHTML = `<strong>${user}:</strong> ${text} <span class="ts">${time}</span>`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

// Join game handler
joinBtn.addEventListener('click', () => {
    const username = usernameInput.value.trim();
    if (!username) {
        alert('Please enter a username!');
        return;
    }
    
    currentUsername = username;
    currentUserElement.textContent = username;
    
    // Join the game
    socket.emit('join_game', { username: username });
    
    // Switch to game view
    loginSection.style.display = 'none';
    gameSection.style.display = 'block';
    
    guessInput.focus();
});

// Guess button handler
guessBtn.addEventListener('click', () => {
    const guess = guessInput.value.trim();
    if (!guess) return;
    
    socket.emit('make_guess', { 
        guess: parseInt(guess),
        ts: Date.now()
    });
    
    guessInput.value = '';
});

// Chat button handler
chatBtn.addEventListener('click', () => {
    const text = chatInput.value.trim();
    if (!text) return;
    
    socket.emit('send_message', { 
        text: text,
        ts: Date.now()
    });
    
    chatInput.value = '';
});

// Enter key handlers
usernameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') joinBtn.click();
});

guessInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') guessBtn.click();
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') chatBtn.click();
});

// Socket event handlers

// Receive general messages
socket.on('message', (msg) => {
    addMessage(msg, 'chat');
});

// Receive game updates (player joined/left)
socket.on('game_update', (data) => {
    addMessage(data, 'system');
});

// Receive guess result feedback
socket.on('guess_result', (data) => {
    if (data.success) {
        addMessage({ user: 'System', text: data.message }, data.correct ? 'winner' : 'guess');
    } else {
        addMessage({ user: 'System', text: data.message }, 'system');
    }
});

// Receive winner announcement
socket.on('game_winner', (data) => {
    addMessage({ user: 'System', text: data.message }, 'winner');
    guessInput.disabled = true;
    guessBtn.disabled = true;
});

// Receive game info
socket.on('game_info', (data) => {
    addMessage({ user: 'System', text: data.message }, 'system');
    console.log('Target number (for debugging):', data.target_number);
});
