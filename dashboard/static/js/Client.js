
// function UpdateStatus(select) {
//     // const row = select.closest('div');
//     // const rowId = row.getAttribute('data-id');

//     const StatusID = document.getElementById('statusID').value;


//     const SelectedStatus = document.getElementById('Pros_Status').value; //old
//     const StatusFor = document.getElementById('Pros_Status').getAttribute('for'); //old


//     // Prepare data for updating
//     const updatedData = {
//         Status_id: StatusID,
//         selected_status: SelectedStatus,
//         status_for: StatusFor,
//     };

//     // Send data to the server using fetch
//     fetch('/updateStatus_ajax/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': '{{ csrf_token }}' // Include if using Django
//         },
//         body: JSON.stringify(updatedData)
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 select.style.transition = "background-color 0.3s ease, color 0.3s ease";
//                 select.style.backgroundColor = "#4CAF50"; // Green background
//                 select.style.color = "#fff"; // White text

//                 // Reset the select after a short delay
//                 setTimeout(() => {

//                     select.style.backgroundColor = ""; // Reset to original background
//                     select.style.color = ""; // Reset to original text color
//                 }, 1500); // Reset after 1.5 seconds
//             } else {
//                 // Show error message box
//                 alert("Failed to save row: " + (data.message || "Unknown error"));
//             }
//         })
//         .catch(error => {
//             // Show error message box for unexpected errors
//             console.error('Error:', error);
//             alert("An error occurred while saving the row. Please try again.");
//         });
// }






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
function Archive(button) {
    const StatusID = document.getElementById('statusID').value;
    const buttonInnerText = document.getElementById('archivebtn').innerText
    const StatusId = {
        Status_id: StatusID,
    };
    fetch('/updateArchived/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // Include if using Django
        },
        body: JSON.stringify(StatusId)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                button.style.backgroundColor = "#6fdfa0"; // Green background

                if (buttonInnerText === 'Archive Case') {
                    button.innerText = "Archived";
                } else {
                    button.innerText = "Unarchived";
                }

                // Reset the button after a short delay
                setTimeout(() => {
                    if (buttonInnerText === 'Archive Case') {
                        button.innerText = "Unarchive Case";
                    } else {
                        button.innerText = "Archive Case";
                    }
                    button.style.backgroundColor = ""; // Reset to original background
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

function FCreate(event) {
    event.preventDefault();
    const button = event.target;
    const StatusID = document.getElementById('statusID').value;
    const FDate = document.getElementById('set_fdate').value;
    const FTask = document.getElementById('set_ftask');
    const FHContainer = document.getElementById('f_history');

    // Validate mandatory inputs
    if (!FDate) {
        alert("Please select a date for the follow-up.");
        return;
    }

    const updatedData = {
        status_id: StatusID,
        f_date: FDate,
        f_task: FTask.value || "",
    };
    fetch('/createFollowup/', {
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
                button.innerText = "Follow Up Instance Created!";
                button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                button.style.backgroundColor = "#6fdfa0"; // Green background

                // Add new follow-up instance dynamically
                const newFollowUpHTML = `
                    <div class="client-sec-header">
                        <h4>${FDate}</h4>
                        <select class="status-select" data-id="${data.new_id}">
                            <option value="pending" selected>Pending</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                    <div class="section-body-full">
                        <input type="text" class="notes-input" placeholder="Notes to assist follow-up operation" style="width:44%;" value="${FTask.value || ""}">
                        <input type="text" class="response-input" placeholder="Write follow-up response here" style="width:44%;" value="">
                        <button class="save-button client-button" data-id="${data.new_id}" style="width:10%; padding:2px!important;">Save</button>
                    </div>
                `;

                FHContainer.insertAdjacentHTML('afterbegin', newFollowUpHTML);

                // Reset the select after a short delay
                setTimeout(() => {
                    button.innerText = "Add Follow Up Instance";
                    button.style.backgroundColor = ""; // Reset to original background
                    FTask.value = "";
                }, 1500); // Reset after 1.5 seconds
            } else {
                // Show error message box
                alert("Failed to save row: " + (data.message || "Unknown error"));
            }
        })
        .catch(error => {
            alert("An error occurred: " + error.message);
        });

}

document.querySelectorAll('.save-button').forEach(button => {
    button.addEventListener('click', function (event) {
        event.preventDefault();
        const followupId = this.getAttribute('data-id');
        const notesInput = this.closest('.section-body-full').querySelector('.notes-input').value;
        const responseInput = this.closest('.section-body-full').querySelector('.response-input').value;

        // Make an AJAX call to save the inputs to the server
        fetch('/save-followup-details/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': '{{ csrf_token }}' // Include CSRF token for security if needed
            },
            body: JSON.stringify({
                id: followupId,
                notes: notesInput,
                response: responseInput
            })
        })

            // .then(response => {
            //     if (response.ok) {
            //         button.style.transition = "background-color 0.3s ease, color 0.3s ease";
            //         button.style.backgroundColor = "#6fdfa0";
            //         button.innerText = "Saved!"

            //         alert(`Follow-up details saved successfully for ID ${followupId}`);
            //     }
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    button.style.transition = "background-color 0.3s ease, color 0.3s ease";
                    button.style.backgroundColor = "#6fdfa0"; // Green background
                    button.innerHTML = "Saved!"

                    // Reset the button after a short delay
                    setTimeout(() => {
                        button.style.backgroundColor = ""; // Reset to original background
                    }, 1500); // Reset after 1.5 seconds
                }

                else {
                    alert('Failed to save follow-up details.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while saving follow-up details.');
            });
    });
});



document.querySelectorAll('.status-select').forEach(select => {
    select.addEventListener('change', function () {
        const followupId = this.getAttribute('data-id');
        const newStatus = this.value;

        // Make an AJAX call to update the status on the server
        fetch('/update-followup-status/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': '{{ csrf_token }}' // Include CSRF token for security if needed
            },
            body: JSON.stringify({ id: followupId, f_status: newStatus })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    select.style.transition = "background-color 0.3s ease, color 0.3s ease";
                    select.style.backgroundColor = "#6fdfa0"; // Green background

                    // Reset the select after a short delay
                    setTimeout(() => {
                        select.style.backgroundColor = ""; // Reset to original background
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
    });
});

function PostStatus(select, field, status, section) {
    const statusSelected = document.getElementById(status).value;
    const update_field = field;
    const StatusID = document.getElementById('statusID').value;
    const Section = section


    // Prepare data for updating
    const updatedData = {
        Status_id: StatusID,
        selected_status: statusSelected,
        status_for: update_field,
        ActionSection: Section,
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
                select.style.backgroundColor = "#6fdfa0"; // Green background

                // Reset the select after a short delay
                setTimeout(() => {

                    select.style.backgroundColor = ""; // Reset to original background
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
//save text area dynamically -------------------start-----------
// let typingTimeout;
// function handleTyping(textarea, field, section, name) {
//     // Clear the previous timer
//     clearTimeout(typingTimeout);

//     // Start a new timer
//     typingTimeout = setTimeout(() => {
//         const StatusID = document.getElementById('statusID').value;
//         const textArea = textarea;
//         const text = textArea.value;
//         const Field = field;
//         const Name = name;
//         const Section = section;

//         const updatedData = {
//             Status_id: StatusID,
//             Text: text,
//             status_for: Field,
//             Action: Name,
//             section: Section,
//         };
//         // Perform an AJAX POST request to save the data
//         fetch('/updateText/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': '{{ csrf_token }}' // Include if using Django
//             },
//             body: JSON.stringify(updatedData)
//         })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.status === 'success') {
//                     textarea.style.transition = "background-color 0.3s ease, color 0.3s ease";
//                     textarea.style.backgroundColor = "#4CAF50"; // Green background
//                     textarea.style.color = "#fff"; // White text

//                     // Reset the select after a short delay
//                     setTimeout(() => {

//                         textarea.style.backgroundColor = ""; // Reset to original background
//                         textarea.style.color = ""; // Reset to original text color
//                     }, 1500); // Reset after 1.5 seconds
//                 } else {
//                     // Show error message box
//                     alert("Failed to save row: " + (data.message || "Unknown error"));
//                 }
//             })
//             .catch(error => {
//                 // Show error message box for unexpected errors
//                 console.error('Error:', error);
//                 alert("An error occurred while saving the row. Please try again.");
//             });
//         // UpdateTextarea();
//     }, 1000); // Wait 1 seconds after the last input
// }

let updateQueue = [];
let isProcessingQueue = false;

function handleTyping(textarea, field, section, name) {
    // Clear the previous timer if it's for the same textarea, or just add to queue
    // For simplicity, we'll just add to the queue. The queue will handle the debouncing.

    const StatusID = document.getElementById('statusID').value;
    const text = textarea.value;

    const updatedData = {
        Status_id: StatusID,
        Text: text,
        status_for: field,
        Action: name,
        section: section,
        textarea: textarea // Keep a reference to the textarea for UI updates
    };

    // Add or update the item in the queue.
    // If an item for the same field/section/name is already in the queue, update its text.
    const existingIndex = updateQueue.findIndex(item =>
        item.status_for === field &&
        item.Action === name &&
        item.section === section
    );

    if (existingIndex > -1) {
        updateQueue[existingIndex] = updatedData;
    } else {
        updateQueue.push(updatedData);
    }

    startQueueProcessing();
}

function startQueueProcessing() {
    if (isProcessingQueue) {
        return; // Already processing
    }

    isProcessingQueue = true;
    processNextInQueue();
}

function processNextInQueue() {
    if (updateQueue.length === 0) {
        isProcessingQueue = false;
        return; // Queue is empty
    }

    const dataToProcess = updateQueue.shift(); // Get the first item from the queue
    const textarea = dataToProcess.textarea; // Get the textarea reference

    // Remove the textarea property before sending to backend
    delete dataToProcess.textarea;

    fetch('/updateText/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // Include if using Django
        },
        body: JSON.stringify(dataToProcess)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                textarea.style.transition = "background-color 0.3s ease, color 0.3s ease";
                textarea.style.border = "4px solid #6fdfa0"; // Green Border


                setTimeout(() => {
                    textarea.style.border = ""; // Reset to original background

                }, 5000);
            } else {
                alert("Failed to save row: " + (data.message || "Unknown error"));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("An error occurred while saving the row. Please try again.");
        })
        .finally(() => {
            // After this request is complete (success or failure), wait 5 seconds
            // and then process the next item in the queue.
            setTimeout(processNextInQueue, 5000); // 5-second interval between requests
        });
}


function deleteAction(actionId) {
    if (confirm("Are you sure you want to delete this action?")) {
        fetch('/delete-action/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}' // Function to get CSRF token
            },
            body: JSON.stringify({ action_id: actionId })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Remove the row from the DOM
                    const row = document.getElementById(actionId);
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
