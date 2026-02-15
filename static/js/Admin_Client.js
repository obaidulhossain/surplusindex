function saveDeliverystatus(select) {
    const row = select.closest('tr');
    const rowId = row.getAttribute('data-id');
    const selectedStatus = row.querySelector('.delivery_status').value;


    // Prepare data for updating
    const updatedData = {
        id: rowId,
        selected_Status: selectedStatus,
    };

    // Send data to the server using fetch
    fetch('/updateDeliveryStatus/', {
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


function updateOrderStatus(select) {
    const row = select.closest('div');
    const rowId = row.getAttribute('data-id');
    const selectedOrderStatus = row.querySelector('.order_status').value;


    // Prepare data for updating
    const updatedData = {
        id: rowId,
        selected_Status: selectedOrderStatus,
    };

    // Send data to the server using fetch
    fetch('/updateOrderStatus/', {
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

// use the function like
// <button class="btn btn-sm btn-warning resend-btn"
//     data-user-id="{{ client.user.id }}"
//     data-attempt="{{ client.activation_attempt }}">
//     Resend ({{ client.activation_attempt }})
// </button>
