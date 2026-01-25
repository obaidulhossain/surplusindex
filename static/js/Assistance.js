const notificationSound = new Audio("/media/uploads/2026/01/25/surplusindex-notification.mp3");
notificationSound.volume = 0.6;
let hasPolledOnce = false;
// CSRF helper
function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

let activeConversationId = document.getElementById("selectedchat").value || null; // set this when conversation is clicked

document.addEventListener("DOMContentLoaded", function () {
    scrollToBottom();
});



function createMessageElement(msg) {
    const div = document.createElement("div");
    div.className = `message ${msg.sender_type === "user" ? "sent" : "received"}`;

    div.innerHTML = `
        <div class="msg-text">${msg.text}</div>
        <div class="msg-time">${msg.message_time}</div>
    `;
    return div;
}

function scrollToBottom() {
    const container = document.getElementById("chatMessages");
    if (!container) return;

    requestAnimationFrame(() => {
        container.scrollTop = container.scrollHeight;
    });
}

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

                //                const div = document.createElement("div");

                //                div.classList.add("message");
                //                div.classList.add(
                //                    msg.sender_type === "user" ? "sent" : "received"
                //                );

                //                div.innerText = msg.text;
                //                container.appendChild(div);
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

// function appendMessage(text, type) {
//     const container = document.getElementById("chatMessages");
//     const div = document.createElement("div");
//     div.className = `message ${type}`;
//     div.innerText = text;
//     container.appendChild(div);
//     container.scrollTop = container.scrollHeight;
// }



// Enter key support
document.getElementById("chatInput").addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendMessage();
});



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
// let previousUnreadCounts = {};

// function pollSidebar() {
//     fetch("/support/poll/conversations/")
//         .then(res => res.json())
//         .then(data => {
//             data.conversations.forEach(c => {
//                 const prev = previousUnreadCounts[c.id] || 0;

//                 if (
//                     c.unread > prev &&
//                     String(c.id) !== String(activeConversationId)
//                 ) {
//                     notificationSound.play().catch(() => { });
//                 }

//                 previousUnreadCounts[c.id] = c.unread;

//                 const badge = document.getElementById(`unread-${c.id}`);
//                 if (!badge) return;

//                 badge.style.display = c.unread > 0 ? "inline-block" : "none";
//                 badge.innerText = c.unread || "";
//             });
//         });
// }

let previousUnreadCounts = {};
let sidebarInitialized = false;

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


// function pollSidebar() {
//     fetch("/support/poll/conversations/")
//         .then(res => res.json())
//         .then(data => {
//             data.conversations.forEach(c => {
//                 // Skip active conversation
//                 if (String(c.id) === String(activeConversationId)) return;

//                 const unreadEl = document.getElementById(`unread-${c.id}`);
//                 if (!unreadEl) return;

//                 if (c.unread > 0) {
//                     unreadEl.innerText = c.unread;
//                     unreadEl.style.display = "inline-block";
//                 } else {
//                     unreadEl.style.display = "none";
//                 }
//             });
//         })
//         .catch(err => console.error("Sidebar poll error:", err));
// }




let lastMessageId = null;
let pollingInterval = null;
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

document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") {
        startPolling();
    } else {
        stopPolling();
    }
});

document.addEventListener("DOMContentLoaded", function () {
    if (document.visibilityState === "visible") {
        startPolling();
    }
});
// setInterval(pollNewMessages, 60000); // 1 minute


//---------------------------------- Functions for Admin -------------------------------
function createMessageAdmin(msg) {
    const div = document.createElement("div");
    div.className = `message ${msg.sender_type === "admin" ? "sent" : "received"}`;

    div.innerHTML = `
        <div class="msg-text">${msg.text}</div>
        <div class="msg-time">${msg.sender} - ${msg.message_time}</div>
    `;

    return div;
}



function loadConversationAdmin(el) {
    activeConversationId = el.dataset.convId;
    const convId = el.dataset.convId;
    // 🔹 Remove 'selected' class from all conversations
    document.querySelectorAll('.conversation.selected').forEach(item => {
        item.classList.remove('selected');
    });
    // 🔹 Add 'selected' class to the clicked conversation
    el.classList.add('selected');

    fetch(`/conversation/${convId}/`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("chatMessages");
            container.innerHTML = "";

            data.messages.forEach(msg => {
                container.appendChild(createMessageAdmin(msg));
            });
            scrollToBottom();
        });
}


function sendMessageAdmin() {
    const input = document.getElementById("chatInput");
    const text = input.value.trim();

    if (!text || !activeConversationId) return;

    fetch("/conversation/send/", {
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
                createMessageAdmin({
                    text: data.text,
                    sender: data.sender,
                    sender_type: "admin",
                    message_time: data.message_time,

                })
            );
            //        appendMessage(data.text, "sent");
            input.value = "";
            scrollToBottom();
        });
}
