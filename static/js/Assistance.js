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

            data.messages.forEach(msg => {
                container.appendChild(createMessageElement(msg));
                lastMessageId = msg.id;
            });

            scrollToBottom();
        })
        .catch(err => console.error("Polling error:", err));
}

function pollSidebar() {
    fetch("/support/poll/conversations/")
        .then(res => res.json())
        .then(data => {
            data.conversations.forEach(c => {
                // Skip active conversation
                if (String(c.id) === String(activeConversationId)) return;

                const unreadEl = document.getElementById(`unread-${c.id}`);
                if (!unreadEl) return;

                if (c.unread > 0) {
                    unreadEl.innerText = c.unread;
                    unreadEl.style.display = "inline-block";
                } else {
                    unreadEl.style.display = "none";
                }
            });
        })
        .catch(err => console.error("Sidebar poll error:", err));
}




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
}

function stopPolling() {
    if (!pollingInterval) return;

    clearInterval(pollingInterval);
    pollingInterval = null;
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
