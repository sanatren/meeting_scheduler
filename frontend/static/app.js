// Configuration
const API_BASE_URL = 'http://localhost:8003/api';
const CHAT_ID = 2; // Use the new chat with real users

// State
let messages = [];
let meetings = [];
let participants = [];
let currentUser = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
});

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
        // Redirect to login
        window.location.href = '/auth.html';
        return;
    }
    
    currentUser = JSON.parse(user);
    
    // Update UI with user info
    updateUserInfo();
    
    // Load data
    loadMessages();
    loadMeetings();
    loadParticipants();
}

function updateUserInfo() {
    // Add user info to header
    const header = document.querySelector('header .flex');
    if (header && currentUser) {
        const userInfo = document.createElement('div');
        userInfo.className = 'flex items-center space-x-3';
        userInfo.innerHTML = `
            <div class="text-sm text-gray-600">
                Welcome, ${currentUser.name}
            </div>
            <button onclick="logout()" class="text-sm text-red-600 hover:text-red-800">
                <i class="fas fa-sign-out-alt"></i> Logout
            </button>
        `;
        header.appendChild(userInfo);
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.href = '/auth.html';
}

// Get auth headers
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Load messages
async function loadMessages() {
    try {
        const response = await fetch(`${API_BASE_URL}/messages?chat_id=${CHAT_ID}`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        messages = await response.json();
        displayMessages();
    } catch (error) {
        console.error('Error loading messages:', error);
        document.getElementById('chatMessages').innerHTML = '<div class="text-red-500 p-4">Error loading messages</div>';
    }
}

// Display messages
function displayMessages() {
    const container = document.getElementById('chatMessages');
    container.innerHTML = '';
    
    messages.forEach(message => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'mb-4';
        
        const time = new Date(message.created_at).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        messageDiv.innerHTML = `
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        ${message.user_name.charAt(0)}
                    </div>
                </div>
                <div class="flex-1">
                    <div class="flex items-baseline space-x-2">
                        <span class="font-semibold text-gray-900">${message.user_name}</span>
                        <span class="text-xs text-gray-500">${time}</span>
                    </div>
                    <p class="text-gray-700 mt-1">${message.text}</p>
                </div>
            </div>
        `;
        
        container.appendChild(messageDiv);
    });
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Send message
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const text = input.value.trim();
    
    if (!text || !currentUser) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/messages`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                chat_id: CHAT_ID,
                user_id: currentUser.id,
                text: text
            })
        });
        
        if (response.ok) {
            const newMessage = await response.json();
            messages.push(newMessage);
            displayMessages();
            input.value = '';
        } else if (response.status === 401) {
            // Token expired, redirect to login
            alert('Session expired. Please login again.');
            logout();
        } else {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error response:', response.status, errorData);
            alert(`Error sending message: ${errorData.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Error sending message');
    }
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Schedule meeting
async function scheduleMeeting() {
    const button = event.target;
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Scheduling...';
    button.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/schedule`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_id: CHAT_ID
            })
        });
        
        const result = await response.json();
        const resultDiv = document.getElementById('scheduleResult');
        
        if (result.status === 'scheduled') {
            resultDiv.innerHTML = `
                <div class="bg-green-100 border border-green-400 text-green-700 px-3 py-2 rounded">
                    <i class="fas fa-check-circle mr-2"></i>
                    Meeting scheduled successfully!
                </div>
            `;
            loadMeetings(); // Refresh meetings list
        } else if (result.status === 'need_info') {
            resultDiv.innerHTML = `
                <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-3 py-2 rounded">
                    <i class="fas fa-info-circle mr-2"></i>
                    ${result.ask}
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    ${result.message || 'Error scheduling meeting'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error scheduling meeting:', error);
        document.getElementById('scheduleResult').innerHTML = `
            <div class="bg-red-100 border border-red-400 text-red-700 px-3 py-2 rounded">
                Error scheduling meeting
            </div>
        `;
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Load meetings
async function loadMeetings() {
    try {
        // Fetch meetings for the current chat
        const response = await fetch(`${API_BASE_URL}/meetings?chat_id=${CHAT_ID}`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            const meetings = await response.json();
            displayMeetings(meetings);
        } else {
            console.error('Error response:', response.status);
            displayMeetings([]);
        }
    } catch (error) {
        console.error('Error loading meetings:', error);
        displayMeetings([]);
    }
}

// Display meetings
function displayMeetings(meetingsList) {
    const container = document.getElementById('meetingsList');
    
    if (meetingsList.length === 0) {
        container.innerHTML = '<p class="text-gray-500 text-sm">No meetings scheduled yet</p>';
        return;
    }
    
    container.innerHTML = '';
    meetingsList.forEach(meeting => {
        const meetingDiv = document.createElement('div');
        meetingDiv.className = 'border-l-4 border-blue-500 pl-3 py-2';
        
        const time = new Date(meeting.start_utc).toLocaleString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        meetingDiv.innerHTML = `
            <div class="text-sm">
                <div class="font-semibold text-gray-900">${meeting.title}</div>
                <div class="text-gray-600">${time}</div>
                <div class="text-gray-500 text-xs">${meeting.participants.length} participants</div>
            </div>
        `;
        
        container.appendChild(meetingDiv);
    });
}

// Load participants
async function loadParticipants() {
    try {
        const response = await fetch(`${API_BASE_URL}/chats/${CHAT_ID}/participants`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            const participants = await response.json();
            displayParticipants(participants);
        } else {
            console.error('Error response:', response.status);
            displayParticipants([]);
        }
    } catch (error) {
        console.error('Error loading participants:', error);
        displayParticipants([]);
    }
}

// Display participants
function displayParticipants(participantsList) {
    const container = document.getElementById('participantsList');
    container.innerHTML = '';
    
    participantsList.forEach(participant => {
        const participantDiv = document.createElement('div');
        participantDiv.className = 'flex items-center space-x-2 mb-2';
        
        participantDiv.innerHTML = `
            <div class="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center text-xs font-semibold">
                ${participant.name.charAt(0)}
            </div>
            <div class="text-sm">
                <div class="font-medium text-gray-900">${participant.name}</div>
                <div class="text-gray-500 text-xs">${participant.email}</div>
            </div>
        `;
        
        container.appendChild(participantDiv);
    });
}

// Auto-refresh messages every 5 seconds
setInterval(loadMessages, 5000);
