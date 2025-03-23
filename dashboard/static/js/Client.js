// $(document).ready(function () {
//     var checkbox = $('table tbody tr input[type="checkbox"]');
//     $("#selectAll").click(function () {
//         if (this.checked) {
//             checkbox.each(function () {
//                 this.checked = true;
//             });
//         } else {
//             checkbox.each(function () {
//                 this.checked = false;
//             });
//         }
//     });
//     checkbox.click(function () {
//         if (!this.checked) {
//             $("#selectAll").prop("checked", false);
//         }
//     });
// })

// function updateDatabase() {
//     const checkboxes = document.querySelectorAll('.checkbox:checked');
//     const selectedIds = Array.from(checkboxes).map(checkbox => checkbox.value);

//     if (selectedIds.length === 0) {
//         alert('No rows selected.');
//         return;
//     }

//     fetch("{% url 'update-leads' %}", {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': '{{ csrf_token }}'
//         },
//         body: JSON.stringify({ selected_ids: selectedIds })
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert('Database updated successfully.');
//                 location.reload();
//             } else {
//                 alert('Error updating database.');
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             alert('An error occurred.');
//         });
// }









function updateButtonStates() {
    // Get all checkboxes within the table
    const checkboxes = document.querySelectorAll('.checkbox');
    const selectedCheckboxes = Array.from(checkboxes).filter(checkbox => checkbox.checked);

    // Update the count of selected checkboxes
    const selectedCount = selectedCheckboxes.length;
    document.getElementById('selected-count').textContent = selectedCount;
    document.getElementById('selected-count-hide').textContent = selectedCount;

    // Enable or disable buttons based on selection
    document.getElementById('add-button').disabled = selectedCount === 0;
    document.getElementById('hide-button').disabled = selectedCount === 0;
}

// Attach event listeners to checkboxes
document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('.checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateButtonStates);
    });

    // Also initialize button states on page load
    updateButtonStates();
});

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

