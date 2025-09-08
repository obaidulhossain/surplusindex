// // document.querySelector("#sidebar").classList.toggle("expand");
// const hamburger = document.querySelector("#toggle-btn");
// hamburger.addEventListener("click", function () {
//     document.querySelector("#sidebar").classList.toggle("expand");
// })


document.addEventListener("DOMContentLoaded", function () {
    const toggleBTN = document.querySelector("#toggle-btn");
    const sidebar = document.querySelector("#sidebar");

    toggleBTN.addEventListener("click", function () {
        sidebar.classList.toggle("expand");

        // Save the user's preference via AJAX
        const expanded = sidebar.classList.contains("expand");

        fetch('/AllSettings/save-sidebar-setting/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ expanded })
        });
    });

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});