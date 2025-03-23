// Reuseable function
// -------------------------toggle filters button-----(start)-----------------------------
//Example Usage: <button id="toggle-filters" class="toogle-button" onclick="toggleFilters(this.id, 'filters')">Hide</button>
function toggleFilters(togglebtn, hide_id) {
    const section = document.getElementById(hide_id); // hide_id = section id to be hidden
    const button = document.getElementById(togglebtn); // togglebtn = button id that will perform the action

    if (section.style.display === "flex" || section.style.display === "") {
        section.style.display = "none";
        button.innerText = "Show";
    } else {
        section.style.display = "flex";
        button.innerText = "Hide";
    }
}


// -------------------------toggle filters button-----(end)-----------------------------

function copyToClipboard(button) {
    const url = button.getAttribute('data'); // Get the URL from the data attribute
    navigator.clipboard.writeText(url).then(() => {
        // Change text and color with transition
        button.value = "Copied!";
        button.style.transition = "background-color 0.3s ease, color 0.3s ease";
        button.style.backgroundColor = "#4CAF50"; // Change to green
        button.style.color = "#fff"; // Change text color to white

        // Reset after 5 seconds with transition
        setTimeout(() => {
            button.value = "Copy";
            button.style.transition = "background-color 0.3s ease, color 0.3s ease"; // Ensure transition when resetting
            button.style.backgroundColor = ""; // Reset to original color
            button.style.color = ""; // Reset to original color
        }, 1500); // 5000 milliseconds = 5 seconds
    }).catch(err => {
        alert("Failed to copy URL: " + err);
    });
}