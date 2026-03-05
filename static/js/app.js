/**
 * AI Avatar — Frontend Application Logic
 * Handles chat messaging, streaming responses, lip-sync video playback
 */

// ============ State ============
const state = {
    isGenerating: false,
    messageCount: 0,
    totalTokens: 0,
    startTime: null,
};

// ============ DOM Elements ============
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const charCount = document.getElementById('charCount');
const msgCount = document.getElementById('msgCount');
const responseTime = document.getElementById('responseTime');
const tokenCount = document.getElementById('tokenCount');
const speakingIndicator = document.getElementById('speakingIndicator');
const processingOverlay = document.getElementById('processingOverlay');
const processingText = document.getElementById('processingText');
const avatarImage = document.getElementById('avatarImage');
const avatarVideo = document.getElementById('avatarVideo');

// ============ Auto-resize Textarea ============
messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    charCount.textContent = messageInput.value.length;
});

// ============ Send on Enter ============
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);
clearBtn.addEventListener('click', clearChat);

// ============ Avatar: Switch between image and video ============
function showIdleAvatar() {
    avatarImage.classList.add('active');
    avatarVideo.classList.remove('active');
    speakingIndicator.classList.remove('active');
    processingOverlay.classList.remove('active');
}

function showProcessing() {
    processingOverlay.classList.add('active');
}

function hideProcessing() {
    processingOverlay.classList.remove('active');
}

function playLipSyncVideo(videoUrl) {
    console.log('playLipSyncVideo called with:', videoUrl);
    return new Promise((resolve) => {
        // Set up video
        avatarVideo.src = videoUrl;
        avatarVideo.muted = false;
        avatarVideo.currentTime = 0;

        console.log('Video element configured');

        // Switch to video display
        avatarImage.classList.remove('active');
        avatarVideo.classList.add('active');
        speakingIndicator.classList.add('active');
        hideProcessing();

        console.log('Switched to video display');

        // Play the video
        avatarVideo.play().then(() => {
            console.log('Video playing successfully');
        }).catch(err => {
            console.warn('Video autoplay blocked, trying muted:', err);
            avatarVideo.muted = true;
            avatarVideo.play().then(() => {
                console.log('Video playing (muted) successfully');
            }).catch(err2 => {
                console.error('Failed to play video even when muted:', err2);
            });
        });

        // When video ends, switch back to idle
        avatarVideo.onended = () => {
            console.log('Video ended');
            showIdleAvatar();
            resolve();
        };

        avatarVideo.onerror = (e) => {
            console.error('Video playback error:', e, avatarVideo.error);
            showIdleAvatar();
            resolve();
        };
    });
}

// ============ Send Message ============
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || state.isGenerating) return;

    state.isGenerating = true;
    sendBtn.disabled = true;

    // Add user message
    addMessage('user', text);

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    charCount.textContent = '0';

    // Update stats
    state.messageCount++;
    msgCount.textContent = state.messageCount;

    // Show typing indicator
    const typingEl = addTypingIndicator();

    // Start timer
    state.startTime = performance.now();

    try {
        // Stream response from backend
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text }),
        });

        // Remove typing indicator
        typingEl.remove();

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        // Create AI message container
        const aiMsgEl = addMessage('ai', '', true);
        const textEl = aiMsgEl.querySelector('.message-text');

        // Read SSE stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';
        let tokenCountLocal = 0;
        let videoUrl = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;

                    try {
                        const parsed = JSON.parse(data);
                        console.log('SSE event:', parsed);

                        // Text token
                        if (parsed.token) {
                            fullText += parsed.token;
                            tokenCountLocal++;
                            textEl.innerHTML = formatText(fullText);
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }

                        // Status: generating speech
                        if (parsed.status === 'generating_speech') {
                            processingText.textContent = '🎤 Generating speech audio...';
                            showProcessing();
                        }

                        // Status: generating lip sync
                        if (parsed.status === 'generating_lipsync') {
                            processingText.textContent = '🎬 Creating lip-sync animation...';
                            showProcessing();
                        }

                        // Lip-sync video ready
                        if (parsed.video) {
                            console.log('Video URL received:', parsed.video);
                            videoUrl = parsed.video;
                        }

                        // Error
                        if (parsed.error) {
                            textEl.innerHTML = `<span style="color: var(--error);">⚠️ ${parsed.error}</span>`;
                        }

                        // Speech generation error
                        if (parsed.status === 'speech_error') {
                            hideProcessing();
                        }
                    } catch (e) {
                        // Ignore partial JSON
                        console.log('JSON parse error:', e, 'data:', data.substring(0, 100));
                    }
                }
            }
        }

        // Update stats
        const elapsed = performance.now() - state.startTime;
        responseTime.textContent = (elapsed / 1000).toFixed(1) + 's';
        state.totalTokens += tokenCountLocal;
        tokenCount.textContent = state.totalTokens;
        state.messageCount++;
        msgCount.textContent = state.messageCount;

        // Play lip-synced video if available
        console.log('Stream ended. Video URL:', videoUrl);
        if (videoUrl) {
            console.log('Playing video:', videoUrl);
            await playLipSyncVideo(videoUrl);
        } else {
            console.log('No video URL, hiding processing overlay');
            hideProcessing();
        }

    } catch (error) {
        console.error('Error:', error);
        const existingTyping = document.querySelector('.typing-message');
        if (existingTyping) existingTyping.remove();

        addMessage('ai', `⚠️ Error: ${error.message}`);
        hideProcessing();
    } finally {
        state.isGenerating = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// ============ Add Message ============
function addMessage(type, text, isStreaming = false) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${type}-message`;

    const avatarSvg = type === 'ai'
        ? `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M12 2a5 5 0 0 1 5 5v3a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5Z"/>
               <path d="M17 10v1a5 5 0 0 1-10 0v-1"/>
           </svg>`
        : `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
               <circle cx="12" cy="7" r="4"></circle>
           </svg>`;

    const name = type === 'ai' ? 'AI Avatar' : 'You';

    msgDiv.innerHTML = `
        <div class="message-avatar">${avatarSvg}</div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-name">${name}</span>
                <span class="message-time">${timeStr}</span>
            </div>
            <div class="message-text">${isStreaming ? '<span class="cursor-blink">|</span>' : formatText(text)}</div>
        </div>
    `;

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgDiv;
}

// ============ Typing Indicator ============
function addTypingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message typing-message';
    msgDiv.innerHTML = `
        <div class="message-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a5 5 0 0 1 5 5v3a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5Z"/>
                <path d="M17 10v1a5 5 0 0 1-10 0v-1"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-name">AI Avatar</span>
                <span class="message-time">thinking...</span>
            </div>
            <div class="message-text">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgDiv;
}

// ============ Format Text ============
function formatText(text) {
    let formatted = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/`(.*?)`/g, '<code style="background: var(--bg-elevated); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 0.85em;">$1</code>');
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

// ============ Clear Chat ============
function clearChat() {
    chatMessages.innerHTML = '';

    const freshWelcome = document.createElement('div');
    freshWelcome.className = 'message ai-message';
    freshWelcome.innerHTML = `
        <div class="message-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a5 5 0 0 1 5 5v3a5 5 0 0 1-10 0V7a5 5 0 0 1 5-5Z"/>
                <path d="M17 10v1a5 5 0 0 1-10 0v-1"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="message-header">
                <span class="message-name">AI Avatar</span>
                <span class="message-time">now</span>
            </div>
            <div class="message-text">
                👋 Chat cleared! Ready for a new conversation.
            </div>
        </div>
    `;
    chatMessages.appendChild(freshWelcome);

    state.messageCount = 0;
    state.totalTokens = 0;
    msgCount.textContent = '0';
    tokenCount.textContent = '0';
    responseTime.textContent = '—';

    showIdleAvatar();
    fetch('/clear', { method: 'POST' });
}

// ============ Cursor Blink Style ============
const style = document.createElement('style');
style.textContent = `
    .cursor-blink {
        animation: blink 1s step-end infinite;
        color: var(--accent-secondary);
        font-weight: 300;
    }
    @keyframes blink { 50% { opacity: 0; } }
`;
document.head.appendChild(style);

// ============ Focus Input on Load ============
window.addEventListener('load', () => {
    messageInput.focus();
});
