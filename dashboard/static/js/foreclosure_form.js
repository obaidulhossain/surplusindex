//static/js/foreclosure_form.js

// Case Number Suggestions
const caseNumberInput = document.getElementById('case_number');
const caseNumberList = document.getElementById('case_number_list');

caseNumberInput.addEventListener('input', function () {
    const searchTerm = this.value;
    if (searchTerm.length >= 3) { // Start searching after 3 characters
        fetch(`/foreclosure/case_number_suggestions/?term=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                caseNumberList.innerHTML = ''; // Clear previous suggestions
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = `${item.case_number} - ${item.county}, ${item.state}`;
                    option.dataset.id = item.id; // Store the ID
                    option.dataset.caseNumber = item.case_number;
                    option.dataset.county = item.county;
                    option.dataset.state = item.state;
                    caseNumberList.appendChild(option);
                });
            });
    } else {
        caseNumberList.innerHTML = ''; // Clear suggestions if search term is too short
    }
});

caseNumberInput.addEventListener('change', function () {
    const selectedOption = caseNumberList.querySelector(`option[value="${this.value}"]`);

    if (selectedOption) {
        const foreclosureId = selectedOption.dataset.id;
        //Fetch complete foreclosure detail and populate the form here
    }
})



//Property Search and Creation

const propertySearchInput = document.getElementById('property_search');
const propertySuggestionsList = document.getElementById('property_suggestions');
const propertyList = document.getElementById('property_list');
const addPropertyButton = document.getElementById('add_property_button');
const newPropertyButton = document.getElementById('new_property_button');
const propertyModal = document.getElementById('property_modal');
const savePropertyButton = document.getElementById('save_property');
const closePropertyModal = propertyModal.querySelector('.close'); // Assuming your close button has a class 'close'
const propertyHiddenField = document.querySelector('select[name="property"]'); // Select the correct property hidden field.



function addPropertyToList(property) {
    const listItem = document.createElement('li');
    listItem.textContent = `${property.parcel} - ${property.address}`;
    listItem.dataset.id = property.id;

    const removeButton = document.createElement('button');
    removeButton.textContent = 'Remove';
    removeButton.addEventListener('click', function () {
        listItem.remove();
        updateHiddenPropertyField();
    });

    listItem.appendChild(removeButton);
    propertyList.appendChild(listItem);
    updateHiddenPropertyField();

}

function updateHiddenPropertyField() {
    const selectedPropertyIds = Array.from(propertyList.querySelectorAll('li')).map(li => li.dataset.id);
    //set value of the hidden field
    propertyHiddenField.value = selectedPropertyIds.join(',');
}
//Event listeners for the property functionality
propertySearchInput.addEventListener('input', function () {
    const searchTerm = this.value;
    if (searchTerm.length >= 3) { // Adjust the minimum length as needed
        fetch(`/foreclosure/property_search_create/?term=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                propertySuggestionsList.innerHTML = '';
                data.forEach(property => {
                    const option = document.createElement('option');
                    option.value = `${property.parcel} - ${property.address}`;
                    option.dataset.id = property.id;
                    propertySuggestionsList.appendChild(option);
                });
            });
    } else {
        propertySuggestionsList.innerHTML = '';
    }
});

addPropertyButton.addEventListener('click', function () {
    const selectedOption = propertySuggestionsList.querySelector(`option[value="${propertySearchInput.value}"]`);
    if (selectedOption) {
        const propertyId = selectedOption.dataset.id;
        const propertyText = selectedOption.value;
        addPropertyToList({ id: propertyId, text: propertyText }); //Append the property in the list
        propertySearchInput.value = '';
        propertySuggestionsList.innerHTML = '';
    }
});

// New Property Modal
newPropertyButton.addEventListener('click', function () {
    propertyModal.style.display = 'block';
});

closePropertyModal.addEventListener('click', function () {
    propertyModal.style.display = 'none';
});

window.addEventListener('click', function (event) {
    if (event.target === propertyModal) {
        propertyModal.style.display = 'none';
    }
});

savePropertyButton.addEventListener('click', function () {
    const form = document.getElementById('new_property_form');
    const formData = new FormData(form);

    fetch('/foreclosure/property_search_create/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value  // Get the CSRF token
        }
    })
        .then(response => response.json())
        .then(property => {
            // Append a property on property_list and the associated hidden field
            addPropertyToList(property);
            propertyModal.style.display = 'none';

            // Clear the form or give a success message
            form.reset();
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle errors (display error messages, etc.)
        });
});


//Call this function on load if you have existing properties to show
// updateHiddenPropertyField();

// Repeat above steps for Contact and ForeclosingEntity