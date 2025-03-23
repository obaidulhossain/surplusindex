$(document).ready(function () {
    var checkbox = $('table tbody tr:visible input[type="checkbox"]');
    $("#selectAll").click(function () {
        if (this.checked) {
            checkbox.each(function () {
                this.checked = true;
            });
        } else {
            checkbox.each(function () {
                this.checked = false;
            });
        }
    });
    checkbox.click(function () {
        if (!this.checked) {
            $("#selectAll").prop("checked", false);
        }
    });




})

document.addEventListener("DOMContentLoaded", function () {
    const selectAll = document.getElementById("selectAll");
    const checkboxes = document.querySelectorAll("#checkbox1");
    const addButton = document.getElementById("add-button");
    const hideButton = document.getElementById("hide-button");
    const selectedCount = document.getElementById("selected-count");
    const selectedCounthide = document.getElementById("selected-count-hide");

    // Function to update button state and count
    function updateButtonState() {
        const checkedCount = document.querySelectorAll("#checkbox1:checked").length;
        addButton.disabled = checkedCount === 0;
        hideButton.disabled = checkedCount === 0;
        selectedCount.textContent = checkedCount;
        selectedCounthide.textContent = checkedCount;
    }

    // Event listener for "Select All" checkbox
    // selectAll.addEventListener("change", function () {
    //     checkboxes.forEach((checkbox) => {
    //         checkbox.checked = this.checked;
    //     });
    //     updateButtonState();
    // });

    // Event listeners for individual checkboxes
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", function () {
            // If not all checkboxes are checked, uncheck "Select All"
            selectAll.checked = checkboxes.length === document.querySelectorAll("#checkbox1:checked").length;
            updateButtonState();
        });
    });

    // Initialize the button state on page load
    updateButtonState();
});

function confirmHideLeads() {
    // Get the count of selected checkboxes
    const selectedLeads = document.querySelectorAll('input[name="selected_items"]:checked').length;

    // If no leads are selected, show a different alert and prevent action
    if (selectedLeads === 0) {
        alert('Please select at least one lead to hide');
        return false;
    }

    // Show the confirmation dialog with the count of selected leads
    const message = `Are you sure you want to hide ${selectedLeads} selected leads?`;
    return confirm(message); // Returns true if OK is clicked, false otherwise
}

function confirmAddToMyLeads() {
    // Get the count of selected checkboxes
    const selectedLeads = document.querySelectorAll('input[name="selected_items"]:checked').length;

    // If no leads are selected, show a different alert and prevent action
    if (selectedLeads === 0) {
        alert('Please select at least one lead to ' + action + '.');
        return false;
    }

    // Show the confirmation dialog with the count of selected leads
    const message = `Are you sure you want to move ${selectedLeads} selected leads to My Leads Section for ${selectedLeads} credits?`;
    return confirm(message); // Returns true if OK is clicked, false otherwise
}


function confirmUnhideLeads() {
    const selectedLeads = document.querySelectorAll('input[name="selected_items"]:checked').length;

    // If no leads are selected, show a different alert and prevent action
    if (selectedLeads === 0) {
        alert('Please select at least one lead to hide');
        return false;
    }

    // Show the confirmation dialog with the count of selected leads
    const message = `Are you sure you want to unhide ${selectedLeads} selected leads?`;
    return confirm(message); // Returns true if OK is clicked, false otherwise
}

function confirmArchive() {
    const selectedLeads = document.querySelectorAll('input[name="selected_items"]:checked').length;
    // If no leads are selected, show a different alert and prevent action
    if (selectedLeads === 0) {
        alert('Please select at least one lead to hide');
        return false;
    }

    // Show the confirmation dialog with the count of selected leads
    const message = `Are you sure you want to Archive ${selectedLeads} selected leads? These leads can be found and unarchived from Archived Leads Section.`;
    return confirm(message); // Returns true if OK is clicked, false otherwise
}

function confirmUnarchive() {
    const selectedLeads = document.querySelectorAll('input[name="selected_items"]:checked').length;
    // If no leads are selected, show a different alert and prevent action
    if (selectedLeads === 0) {
        alert('Please select at least one lead to hide');
        return false;
    }

    // Show the confirmation dialog with the count of selected leads
    const message = `Are you sure you want to Unarchive ${selectedLeads} selected leads? These leads can be found in My Leads Section.`;
    return confirm(message); // Returns true if OK is clicked, false otherwise
}