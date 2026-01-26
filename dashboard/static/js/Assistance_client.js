//------------------------------------------------------------------------- Global Functions and constants
const notificationSound = new Audio("/media/uploads/2026/01/25/surplusindex-notification.mp3");
notificationSound.volume = 0.6;
let previousUnreadCounts = {};
let sidebarInitialized = false;
let lastMessageId = null;
let pollingInterval = null;
let hasPolledOnce = false;
let activeConversationId = document.getElementById("selectedchat").value || null; // set this when conversation is clicked

//------------------------------------------------------------------------- CSRF helper
function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}
//-------------------------------------------------------------------------

//------------------------------------------------------------------------- Functions to be run on pageload
document.addEventListener("DOMContentLoaded", function () {
    if (document.visibilityState === "visible") {
        startPolling();
    }
    scrollToBottom();
});

document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") {
        startPolling();
    } else {
        stopPolling();
    }
});
//------------------------------------------------------------------------- 

//------------------------------------------------------------------------- Press Enter to send message
document.getElementById("chatInput").addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendMessage();
});
//-------------------------------------------------------------------------

//------------------------------------------------------------------------- Scroll to bottom
function scrollToBottom() {
    const container = document.getElementById("chatMessages");
    if (!container) return;

    requestAnimationFrame(() => {
        container.scrollTop = container.scrollHeight;
    });
}
//-------------------------------------------------------------------------

//------------------------------------------------------------------------- Create Message Elements (used in loadConversation, sendMessage)

function createMessageElement(msg) {
    const div = document.createElement("div");
    div.className = `message ${msg.sender_type === "user" ? "sent" : "received"}`;

    div.innerHTML = `
        <div class="msg-text">${msg.text}</div>
        <div class="msg-time">${msg.message_time}</div>
    `;
    return div;
}
//------------------------------------------------------------------------- 

//------------------------------------------------------------------------- Load Conversation
function loadConversation(el) {
    activeConversationId = el.dataset.convId;
    const convId = el.dataset.convId;
    // 🔹 Remove 'selected' class from all conversations
    document.querySelectorAll('.conversation.selected').forEach(item => {
        item.classList.remove('selected');
    });
    // 🔹 Add 'selected' class to the clicked conversation
    el.classList.add('selected');

    fetch(`/support/${convId}/`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("chatMessages");
            container.innerHTML = "";

            data.messages.forEach(msg => {
                container.appendChild(createMessageElement(msg));
                lastMessageId = msg.id;
            });

            // auto scroll to bottom
            scrollToBottom();
            const unreadBlock = document.getElementById(`unread-${convId}`);
            unreadBlock.style.display = "none";
            unreadBlock.innerText = "";
            const input = document.getElementById("chatInput");
            input.focus()
        });
}
//------------------------------------------------------------------------- 

//------------------------------------------------------------------------- Send Messages
function sendMessage() {
    const input = document.getElementById("chatInput");
    const text = input.value.trim();

    if (!text || !activeConversationId) return;

    fetch("/support/send/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify({
            conversation_id: activeConversationId,
            message: text
        })
    })
        .then(res => res.json())
        .then(data => {
            container = document.getElementById("chatMessages");
            container.appendChild(
                createMessageElement({
                    text: data.text,
                    sender_type: "user",
                    message_time: data.message_time,

                })
            );
            //        appendMessage(data.text, "sent");
            input.value = "";
            lastMessageId = data.id;
            scrollToBottom();
        });
}
//------------------------------------------------------------------------- 

//------------------------------------------------------------------------- Poll messages
function pollNewMessages() {
    if (!activeConversationId) return;

    let url = `/support/poll/${activeConversationId}/`;
    if (lastMessageId) {
        url += `?last_id=${lastMessageId}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (!data.messages.length) return;

            const container = document.getElementById("chatMessages");
            let shouldPlaySound = false;

            data.messages.forEach(msg => {
                container.appendChild(createMessageElement(msg));
                lastMessageId = msg.id;
                shouldPlaySound = true;

            });
            if (hasPolledOnce && shouldPlaySound) {
                notificationSound.play().catch(() => { });
            }
            hasPolledOnce = true;
            scrollToBottom();
        })
        .catch(err => console.error("Polling error:", err));
}
//------------------------------------------------------------------------- 

//------------------------------------------------------------------------- Poll Sidebar
function pollSidebar() {
    fetch("/support/poll/conversations/")
        .then(res => res.json())
        .then(data => {
            let shouldPlaySound = false;

            data.conversations.forEach(c => {
                if (String(c.id) === String(activeConversationId)) return;

                const unreadEl = document.getElementById(`unread-${c.id}`);
                if (!unreadEl) return;

                const prev = previousUnreadCounts[c.id] || 0;

                // 🔔 Detect increase
                if (sidebarInitialized && c.unread > prev) {
                    shouldPlaySound = true;
                }

                // Update UI
                if (c.unread > 0) {
                    unreadEl.innerText = c.unread;
                    unreadEl.style.display = "inline-block";
                } else {
                    unreadEl.style.display = "none";
                    unreadEl.innerText = "";
                }

                // Store current state
                previousUnreadCounts[c.id] = c.unread;
            });

            if (shouldPlaySound) {
                notificationSound.play().catch(() => { });
            }

            sidebarInitialized = true;
        })
        .catch(err => console.error("Sidebar poll error:", err));
}
//------------------------------------------------------------------------- 

//------------------------------------------------------------------------- Polling Controls
function startPolling() {
    if (pollingInterval) return;

    pollNewMessages(); // instant fetch
    pollSidebar();

    pollingInterval = setInterval(() => {
        pollNewMessages();
        pollSidebar();
    }, 15000); // 15s
    notificationSound.volume = 0.1;
}

function stopPolling() {
    if (!pollingInterval) return;

    clearInterval(pollingInterval);
    pollingInterval = setInterval(() => {
        pollNewMessages();
        pollSidebar();
    }, 60000); // 15s
    notificationSound.volume = 0.9;
}
//-------------------------------------------------------------------------