



function openCity(evt, cityName) {
    console.log("Tab clicked:", cityName);
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    var targetTab = document.getElementById(cityName);
    if (targetTab) {
        targetTab.style.display = "block";
        evt.currentTarget.className += " active";
    } else {
        console.error("Target tab not found:", cityName);
    }
}
// document.getElementById(cityName).style.display = "block";
// evt.currentTarget.className += " active";


// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();


document.getElementById('statusSelect').addEventListener('change', function () {
    // Hide all sections
    document.querySelectorAll('.cd_status').forEach(section => {
        section.style.display = 'none';
    });

    // Get the selected value
    const selectedValue = this.value;

    // Show the corresponding section if a valid value is selected
    if (selectedValue) {
        const section = document.getElementById(selectedValue);
        if (section) {
            section.style.display = 'inline-block';
        }
    }
    //save status
    const StatusID = document.getElementById('statusID').value;
    const updateStatus = {
        status_id: StatusID,
        status: selectedValue,
    };
    fetch('/updateCLStatus/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // Include if using Django
        },
        body: JSON.stringify(updateStatus)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                this.style.transition = "background-color 0.3s ease, color 0.3s ease";
                this.style.backgroundColor = "#6fdfa0"; // Green background
                this.style.color = "#1b1b1b"; // White text
                // Reset the select after a short delay
                setTimeout(() => {
                    this.style.backgroundColor = ""; // Reset to original background
                    this.style.color = ""; // Reset to original text color

                }, 1500); // Reset after 1.5 seconds
            } else {
                // Show error message box
                alert("Failed to save row: " + (data.message || "Unknown error"));
            }
        })
        .catch(error => {
            alert("An error occurred: " + error.message);
        });

});