
function UpdateStatus(select) {
    // const row = select.closest('div');
    // const rowId = row.getAttribute('data-id');
    const StatusID = document.getElementById('statusID').value;
    const SelectedStatus = document.getElementById('Pros_Status').value;


    // Prepare data for updating
    const updatedData = {
        Status_id: StatusID,
        selected_status: SelectedStatus,
    };

    // Send data to the server using fetch
    fetch('/updateStatus_ajax/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // Include if using Django
        },
        body: JSON.stringify(updatedData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                select.style.transition = "background-color 0.3s ease, color 0.3s ease";
                select.style.backgroundColor = "#4CAF50"; // Green background
                select.style.color = "#fff"; // White text

                // Reset the select after a short delay
                setTimeout(() => {

                    select.style.backgroundColor = ""; // Reset to original background
                    select.style.color = ""; // Reset to original text color
                }, 1500); // Reset after 1.5 seconds
            } else {
                // Show error message box
                alert("Failed to save row: " + (data.message || "Unknown error"));
            }
        })
        .catch(error => {
            // Show error message box for unexpected errors
            console.error('Error:', error);
            alert("An error occurred while saving the row. Please try again.");
        });
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

function confirmExport() {
    // Get the count of selected checkboxes
    const selectedLeads = document.querySelectorAll('input[name="selected_items"]:checked').length;

    // If no leads are selected, show a different alert and prevent action
    if (selectedLeads === 0) {
        alert('Please select at least one lead to Export');
        return false;
    }

    // Show the confirmation dialog with the count of selected leads
    const message = `Are you sure you want to Export ${selectedLeads} selected leads?`;
    return confirm(message); // Returns true if OK is clicked, false otherwise
}