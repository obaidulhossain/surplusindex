// Reuseable function
// -------------------------toggle filters button-----(start)-----------------------------
//Example Usage: <button id="toggle-filters" class="toogle-button" onclick="toggleFilters(this.id, 'filters')">Hide</button>
function toggleFilters(togglebtn, hide_id, event) {
    event.preventDefault(); // Prevent the form submission
    const section = document.getElementById(hide_id); // hide_id = section id to be hidden
    const button = document.getElementById(togglebtn); // togglebtn = button id that will perform the action

    if (section.style.display === "block" || section.style.display === "") {
        section.style.display = "none";
        button.innerHTML = '<i class="bi bi-eye"></i>';
    } else {
        section.style.display = "block";
        button.innerHTML = '<i class="bi bi-eye-slash"></i>';
    }
}
// -------------------------Toggle_and_Save filters button-----(start)-----------------------------
//Example Usage: <button id="toggle-filters" class="icon-button" data-url="{% url 'update-show-hide-setting' %}" onclick="Toggle_and_Save(this.id, 'filters', 'alldata_show_filter', event)" style="padding: 2px 7px;"><i class="bi bi-eye-slash"></i></button>

function Toggle_and_Save(togglebtn, hide_id, fieldName, event) {
    event.preventDefault(); // Prevent form submission

    const section = document.getElementById(hide_id);
    const button = document.getElementById(togglebtn);
    const url = button.dataset.url; // get URL from data attribute
    let newValue;

    if (section.style.display === "block" || section.style.display === "") {
        section.style.display = "none";
        button.innerHTML = '<i class="bi bi-eye"></i>';
        newValue = false;
    } else {
        section.style.display = "block";
        button.innerHTML = '<i class="bi bi-eye-slash"></i>';
        newValue = true;
    }
    // Send AJAX to Django to update the field
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"), // helper below
        },
        body: JSON.stringify({
            field: fieldName,
            value: newValue
        })
    })
        .then(res => res.json())
        .then(data => console.log("Saved:", data))
        .catch(err => console.error("Error:", err));
}

// CSRF helper for fetch()
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



// -------------------------toggle filters button-----(end)-----------------------------


function copyGlobal(button, buttontxt) {
    const url = button.getAttribute('data'); // Get the URL from the data attribute
    navigator.clipboard.writeText(url).then(() => {
        // Change text and color with transition
        button.value = "Copied!";
        button.style.transition = "background-color 0.3s ease, color 0.3s ease";
        button.style.backgroundColor = "#4CAF50"; // Change to green
        button.style.color = "#fff"; // Change text color to white

        // Reset after 5 seconds with transition
        setTimeout(() => {
            button.value = buttontxt;
            button.style.transition = "background-color 0.3s ease, color 0.3s ease"; // Ensure transition when resetting
            button.style.backgroundColor = ""; // Reset to original color
            button.style.color = ""; // Reset to original color
        }, 1500); // 5000 milliseconds = 5 seconds
    }).catch(err => {
        alert("Failed to copy URL: " + err);
    });
}




// -------------------------Popup info-----(Start)-----------------------------
function togglePopup() {
    const popup = document.getElementById('popup');
    const overlay = document.getElementById('popupOverlay');

    const isVisible = popup.style.display === 'block';

    popup.style.display = isVisible ? 'none' : 'block';
    overlay.style.display = isVisible ? 'none' : 'block';
}

function closePopup() {
    document.getElementById('popup').style.display = 'none';
    document.getElementById('popupOverlay').style.display = 'none';
}

// -------------------------Popup info-----(End)-----------------------------

// -------------------------Popup global info-----(Start)-----------------------------
function displayPopup(popupSection, Overlay) {
    const popup = document.getElementById(popupSection);
    const overlay = document.getElementById(Overlay);

    const isVisible = popup.style.display === 'block';

    popup.style.display = isVisible ? 'none' : 'block';
    overlay.style.display = isVisible ? 'none' : 'block';
}

function exitPopup(popupSection, Overlay) {
    document.getElementById(popupSection).style.display = 'none';
    document.getElementById(Overlay).style.display = 'none';
}

// -------------------------Popup global info-----(End)-----------------------------


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


// Reuseable function
// -------------------------count checkbox checked-----(start)-----------------------------
//Example Usage: <button class="button" id="archive-button" data-requires-selection disabled="disabled" type="submit" onclick="return confirmArchiveLeads()">Archive <span data-selected-count>0</span> Selected</button>

function updateButtonStates() {
    // Get all checkboxes with the class 'checkbox'
    const checkboxes = document.querySelectorAll('.checkbox');
    const selectedCheckboxes = Array.from(checkboxes).filter(checkbox => checkbox.checked);

    // Count the selected checkboxes
    const selectedCount = selectedCheckboxes.length;

    // Update all elements with the 'data-selected-count' attribute
    document.querySelectorAll('[data-selected-count]').forEach(element => {
        element.textContent = selectedCount;
    });

    // Enable or disable buttons based on selection
    document.querySelectorAll('[data-requires-selection]').forEach(button => {
        button.disabled = selectedCount === 0;
    });
}

// Attach event listeners and initialize states
document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('.checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateButtonStates);
    });

    // Attach listener to "Select All"
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function () {
            checkboxes.forEach(cb => cb.checked = this.checked);
            updateButtonStates();
        });
    }

    // Initialize button states on page load
    updateButtonStates();
});

// -------------------------count checkbox checked-----(end)-----------------------------


//<input type="text" id="phone" maxlength="14" placeholder="(123) 456-7890">
const phoneInput = document.getElementById('phone');

phoneInput.addEventListener('input', (e) => {
    let input = e.target.value.replace(/\D/g, ''); // Remove all non-digit characters
    let formatted = '';

    if (input.length > 0) {
        formatted = '(' + input.substring(0, 3);
    }
    if (input.length > 3) {
        formatted += ') ' + input.substring(3, 6);
    }
    if (input.length > 6) {
        formatted += '-' + input.substring(6, 10);
    }

    e.target.value = formatted;
});

function markasNotfound(button) {
    const conId = document.querySelector('.markas_notfound').value;

    // Prepare data for updating
    const updatedData = {
        id: conId,
    };

    // Send data to the server using fetch
    fetch('/markas_notfound/', {
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
                button.innerText = "Marked"
                button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                button.style.backgroundColor = "#fe8420"; // Green background
                button.style.color = "#fff"; // White text

                // Reset the button after a short delay
                setTimeout(() => {
                    button.disabled = disabled
                    button.style.backgroundColor = ""; // Reset to original background
                    button.style.color = ""; // Reset to original text color
                }, 1500); // Reset after 1.5 seconds
            } else {
                // Show error message box
                alert("Failed to mark as not found: " + (data.message || "Unknown error"));
            }


        })
        .catch(error => {
            // Show error message box for unexpected errors
            console.error('Error:', error);
            alert("An error occurred while saving. Please try again.");
        });
}


function saveCasesearchstatus(select) {
    const row = select.closest('tr');
    const rowId = row.getAttribute('data-id');
    const selectedStatus = row.querySelector('.casesearchStatus').value;


    // Prepare data for updating
    const updatedData = {
        id: rowId,
        selected_Status: selectedStatus,
    };

    // Send data to the server using fetch
    fetch('/updatecaseSearchStatus/', {
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

                // Reset the button after a short delay
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





function saveData(button) {
    const row = button.closest('tr');
    const rowId = row.getAttribute('data-id');
    const publishStatus = row.querySelector('.publishStatus').value;


    // Prepare data for updating
    const updatedData = {
        id: rowId,
        publish_Status: publishStatus,
    };

    // Send data to the server using fetch
    fetch('/publish/', {
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
                if (publishStatus === 'False') {
                    // Change button style to indicate success
                    button.innerHTML = "Published";
                    button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                    button.style.backgroundColor = "#4CAF50"; // Green background
                    button.style.color = "#fff"; // White text

                    // Reset the button after a short delay
                    setTimeout(() => {
                        button.innerHTML = "Unpublish";
                        button.style.backgroundColor = ""; // Reset to original background
                        button.style.color = ""; // Reset to original text color
                    }, 1500); // Reset after 1.5 seconds
                } else {
                    // Change button style to indicate success
                    button.innerHTML = "Unpublished";
                    button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                    button.style.backgroundColor = "#4CAF50"; // Green background
                    button.style.color = "#fff"; // White text

                    // Reset the button after a short delay
                    setTimeout(() => {
                        button.innerHTML = "Publish";
                        button.style.backgroundColor = ""; // Reset to original background
                        button.style.color = ""; // Reset to original text color
                    }, 1500); // Reset after 1.5 seconds
                }
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

function VerifyPublishStatus(button) {
    const row = button.closest('tr');
    const rowId = row.getAttribute('data-id');
    const publishStatus = row.querySelector('.VerifyPublishStatus').value;


    // Prepare data for updating
    const updatedData = {
        id: rowId,
        publish_Status: publishStatus,
    };

    // Send data to the server using fetch
    fetch('/publish/', {
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
                if (publishStatus === 'False') {
                    // Change button style to indicate success
                    button.innerHTML = "Published";
                    button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                    button.style.backgroundColor = "#4CAF50"; // Green background
                    button.style.color = "#fff"; // White text

                    // Reset the button after a short delay
                    setTimeout(() => {
                        button.innerHTML = "Unpublish";
                        button.style.backgroundColor = ""; // Reset to original background
                        button.style.color = ""; // Reset to original text color
                    }, 1500); // Reset after 1.5 seconds
                } else {
                    // Change button style to indicate success
                    button.innerHTML = "Unpublished";
                    button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                    button.style.backgroundColor = "#4CAF50"; // Green background
                    button.style.color = "#fff"; // White text

                    // Reset the button after a short delay
                    setTimeout(() => {
                        button.innerHTML = "Publish";
                        button.style.backgroundColor = ""; // Reset to original background
                        button.style.color = ""; // Reset to original text color
                    }, 1500); // Reset after 1.5 seconds
                }
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


function AssignSKP(select) {
    const row = select.closest('tr');
    const rowId = row.getAttribute('data-id');
    const assigntoUser = row.querySelector('.assigntoUser').value;


    // Prepare data for updating
    const updatedData = {
        id: rowId,
        assignto_User: assigntoUser,
    };

    // Send data to the server using fetch
    fetch('/assignSKP/', {
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
                if (!assigntoUser) {
                    // Change button style to indicate success

                    select.style.transition = "background-color 0.3s ease, color 0.3s ease";
                    select.style.backgroundColor = "#f66"; // Green background
                    select.style.color = "#fff"; // White text

                    // Reset the button after a short delay
                    setTimeout(() => {

                        select.style.backgroundColor = ""; // Reset to original background
                        select.style.color = ""; // Reset to original text color
                    }, 1500); // Reset after 1.5 seconds
                } else {
                    // Change select style to indicate success

                    select.style.transition = "background-color 0.3s ease, color 0.3s ease";
                    select.style.backgroundColor = "#4CAF50"; // Green background
                    select.style.color = "#fff"; // White text

                    // Reset the select after a short delay
                    setTimeout(() => {

                        select.style.backgroundColor = ""; // Reset to original background
                        select.style.color = ""; // Reset to original text color
                    }, 1500); // Reset after 1.5 seconds
                }
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
