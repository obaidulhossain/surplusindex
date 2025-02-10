// function copyToClipboard(url) {
//     navigator.clipboard.writeText(url).then(() => {
//         // Get the button element by ID
//         const button = document.getElementById('copyButton');

//         // Change the text and color of the button
//         button.value = "Copied!";
//         button.style.backgroundColor = "#4CAF50"; // Change to green for 'Copied'
//         button.style.transition = "background-color 0.5s ease, color 0.3s ease";
//         // Reset the button back to original text and color after 5 seconds
//         setTimeout(() => {
//             button.value = "Copy";
//             button.style.backgroundColor = ""; // Reset to original color
//             button.style.transition = "background-color 0.5s ease, color 0.3s ease"; // Ensure transition when resetting
//         }, 2000); // 5000 milliseconds = 5 seconds
//     }).catch(err => {
//         alert("Failed to copy URL: " + err);
//     });
// }

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
    const taxSaleNext = row.querySelector('.tax-sale-next').value;
    const taxSaleUpdatedTo = row.querySelector('.tax-sale-updated-to').value;

    // Prepare data for updating
    const updatedData = {
        id: rowId,
        tax_sale_next: taxSaleNext,
        tax_sale_updated_to: taxSaleUpdatedTo
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


//start new code



// end new code













//         .then(response => {

//             return response.json();
//         })
//         .then(data => {

//             if (data.status === 'success') {
//                 alert('Row updated successfully!');
//             } else {
//                 alert('Failed to update row: ' + data.message);
//             }
//         })
//         .catch(error => {
//             console.error('Fetch Error:', error);
//             alert('An error occurred. Please try again.');
//         });
// }