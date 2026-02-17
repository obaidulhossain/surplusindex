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



document.querySelectorAll(".enroll-btn").forEach(button => {
    button.addEventListener("click", function () {
        const automationId = this.dataset.automationId;
        const url = this.dataset.url;
        if (confirm("Confirm enrollment and charge your saved payment method?")) {
            const csrftoken = getCookie('csrftoken');
            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({
                    automation_id: automationId
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.status === "success") {
                        alert("Successfully enrolled!");
                        location.reload();
                    } else if (data.status === "redirect_checkout") {
                        window.location.href = data.checkout_url;
                    } else {
                        alert("Payment failed.");
                    }
                });
        }
    });
});
