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