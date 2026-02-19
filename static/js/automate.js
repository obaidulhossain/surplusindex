function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie("csrftoken");
function updateAutomationField(field, value) {
    const id = document.querySelector(".automate-section").dataset.id;

    fetch(`/Automation/update/${id}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
            field: field,
            value: value
        })
    })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                console.error(data.error);
            }
        });
}
function updateSubscription(sub_id, checked) {
    const id = document.querySelector(".automate-section").dataset.id;
    const button = document.getElementById("pay-btn");

    fetch(`/Automation/update-subscription/${id}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
            sub_id: sub_id,
            checked: checked
        })
    })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                console.error(data.error);
            }
        });
}

function toggleState(input) {
    const id = document.querySelector(".automate-section").dataset.id;

    fetch(`/Automation/update-state/${id}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: JSON.stringify({
            state: input.value,
            checked: input.checked
        })
    });
}

const startBtn = document.getElementById('startAutomationBtn');
const confirmDiv = document.getElementById('confirmDiv');
const confirmMessage = document.getElementById('confirmMessage');
const confirmYes = document.getElementById('confirmYes');
const confirmNo = document.getElementById('confirmNo');
const messageDiv = document.getElementById('message');

function showMessage(msg, duration = 10000) {
    messageDiv.innerText = msg;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
        location.reload();
    }, duration);
}
startBtn.addEventListener('click', () => {
    confirmMessage.innerText = `Are you sure you want to automate your lead generation for current settings?\nAutomation fee will be charged from Your default payment method.`;
    confirmDiv.style.display = 'block';
});

confirmNo.addEventListener('click', () => {
    confirmDiv.style.display = 'none';
});

confirmYes.addEventListener('click', async () => {
    confirmDiv.style.display = 'none';
    showMessage("Payment Processing...");
    const id = document.querySelector(".automate-section").dataset.id;
    try {
        const response = await fetch('/Automation/pay/2/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        });
        const data = await response.json();
        if (!data.success) {
            showMessage(data.error, 5000);
        }
    } catch (err) {
        console.error(err);
        showMessage('Server error. Try again.', 5000);
    }
});

function payAndAutomate() {
    const id = document.querySelector(".automate-section").dataset.id;
    // Show confirmation
    const confirmed = confirm(`Are you sure you want to automate with the following settings?\nThe respective subscription price will be billed to your default payment method.`);
    if (!confirmed) return;
    fetch(`/Automation/pay/${id}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        }
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("Payment Processing...");
            } else {
                alert(data.error);
            }
        });
}

