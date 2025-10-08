const socket = io();
const messages = document.getElementById('messages');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('user');
const textInput = document.getElementById('text');

// Function to display messages in the chat area
function addMessage(msg) {
const div = document.createElement('div');
div.className = 'message';
const time = msg && msg.ts ? new Date(msg.ts).toLocaleTimeString() : '';
const user = (msg && msg.user) ? msg.user : 'anonymous';
const text = (msg && msg.text) ? msg.text : '';
div.innerHTML = `<strong>${user}:</strong> ${text} <span class="ts">${time}</span>`;
messages.appendChild(div);
messages.scrollTop = messages.scrollHeight;
}

// Receive general chat messages
socket.on('message', (msg) => {
addMessage(msg);
});

// Receive guess result feedback
socket.on('guess_result', (data) => {
addMessage({ user: 'System', text: data.message });
});

// Receive winner announcement
socket.on('game_winner', (data) => {
addMessage({ user: 'System', text: `${data.user} guessed the number correctly! 🎉` });
});

// Form submission handler
chatForm.addEventListener('submit', (e) => {
e.preventDefault();
const user = userInput.value || 'anonymous';
const text = textInput.value.trim();
if (!text) return;

// If message starts with "/chat", send as normal chat
if (text.startsWith('/chat ')) {
socket.emit('send_message', { user, text: text.slice(6), ts: Date.now() });
}
// Otherwise, treat input as a guess
else {
socket.emit('make_guess', { user, guess: text, ts: Date.now() });
}

textInput.value = '';
textInput.focus();
});
