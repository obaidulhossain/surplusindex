function copyToClipboard(button) {
    const url = button.getAttribute('data-url'); // Get the URL from the data attribute
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


function saveRow(button) {
    const row = button.closest('tr');
    const rowId = row.getAttribute('data-id');


    // Prepare data for updating
    const updatedData = {
        id: rowId,
        event_next: row.querySelector('.event_next').value,
        event_updated_from: row.querySelector('.event_updated_from').value,
        event_updated_to: row.querySelector('.event_updated_to').value,

        post_event_next: row.querySelector('.post_event_next').value,
        post_event_updated_from: row.querySelector('.post_event_updated_from').value,
        post_event_updated_to: row.querySelector('.post_event_updated_to').value
    };

    // Send data to the server using fetch
    fetch('/update-row/', {
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
                // Change button style to indicate success
                button.innerHTML = "Saved!";
                button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                button.style.backgroundColor = "#4CAF50"; // Green background
                button.style.color = "#fff"; // White text

                // Reset the button after a short delay
                setTimeout(() => {
                    button.innerHTML = "Save";
                    button.style.backgroundColor = ""; // Reset to original background
                    button.style.color = ""; // Reset to original text color
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

document.getElementById('select-state').addEventListener('click', function () {
    this.value = '';
});


function saveRowEvent(button) {
    const row = button.closest('tr');
    const rowId = row.getAttribute('data-id');



    // Prepare data for updating
    const updatedData = {
        id: rowId,
        event_next: row.querySelector('.event_next').value,
        event_updated_from: row.querySelector('.event_updated_from').value,
        event_updated_to: row.querySelector('.event_updated_to').value,
    };

    // Send data to the server using fetch
    fetch('/update-row-event/', {
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
                // Change button style to indicate success
                button.innerHTML = "Saved!";
                button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                button.style.backgroundColor = "#4CAF50"; // Green background
                button.style.color = "#fff"; // White text

                // Reset the button after a short delay
                setTimeout(() => {
                    button.innerHTML = "Save";
                    button.style.backgroundColor = ""; // Reset to original background
                    button.style.color = ""; // Reset to original text color
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
















function saveRowPostEvent(button) {
    const row = button.closest('tr');
    const rowId = row.getAttribute('data-id');
    const eventNext = row.querySelector('.post_event_next').value;
    const eventUpdatedFrom = row.querySelector('.post_event_updated_from').value;
    const eventUpdatedTo = row.querySelector('.post_event_updated_to').value;

    // Prepare data for updating
    const updatedData = {
        id: rowId,
        event_next: eventNext,
        event_updated_from: eventUpdatedFrom,
        event_updated_to: eventUpdatedTo
    };

    // Send data to the server using fetch
    fetch('/update-row-post/', {
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
                // Change button style to indicate success
                button.innerHTML = "Saved!";
                button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                button.style.backgroundColor = "#4CAF50"; // Green background
                button.style.color = "#fff"; // White text

                // Reset the button after a short delay
                setTimeout(() => {
                    button.innerHTML = "Save";
                    button.style.backgroundColor = ""; // Reset to original background
                    button.style.color = ""; // Reset to original text color
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

document.getElementById('select-state').addEventListener('click', function () {
    this.value = '';
});


function deleteEvent(EventID) {
    if (confirm("Are you sure you want to delete this Event?")) {
        fetch('/delete-event/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}' // Function to get CSRF token
            },
            body: JSON.stringify({ Event_ID: EventID })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Remove the row from the DOM
                    const row = document.getElementById(EventID);
                    if (row) {
                        // Add the transition style first
                        row.style.transition = "border 0.2s ease, color 0.2s ease";
                        row.style.border = "3px solid #a92e10"; // Change color after transition is set
                        // Use a small delay to ensure the transition is applied

                        setTimeout(() => {
                            row.remove();
                        }, 1000);
                    }
                } else {
                    alert("Failed to delete action: " + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred while deleting the action.");
            });
    }
}