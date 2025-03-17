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