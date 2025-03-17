$(document).ready(function () {
    // Activate tooltip
    $('[data-toggle="tooltip"]').tooltip();


    //----------------------------------------------------------------------------------------------------
    // -------------------------Select Deselect and Select All Checkboxes---------------------------------
    // -------------------------Select Deselect and Select All Checkboxes---------------------------------
    // var checkbox = $('table tbody tr:visible input[type="checkbox"]');
    // $("#selectAll").click(function () {
    //     if (this.checked) {
    //         checkbox.each(function () {
    //             this.checked = true;
    //         });
    //     } else {
    //         checkbox.each(function () {
    //             this.checked = false;
    //         });
    //     }
    // });
    // checkbox.click(function () {
    //     if (!this.checked) {
    //         $("#selectAll").prop("checked", false);
    //     }
    // });






    var visibleCheckboxes = $('table tbody tr:visible input[type="checkbox"]');
    $("#selectAll").click(function () {

        if (this.checked) {
            visibleCheckboxes.each(function () {
                this.checked = true;
            });
        } else {
            visibleCheckboxes.each(function () {
                this.checked = false;
            });
        }
    });
    visibleCheckboxes.click(function () {
        if (!this.checked) {
            $("#selectAll").prop("checked", false);
        }
    });
});
// -------------------------Select Deselect and Select All Checkboxes---------------------------------
// -------------------------Select Deselect and Select All Checkboxes---------------------------------

//----------------------------------------------------------------------------------------------------

// -------------------------Enable and Disable Add to my list button----------------------------------
// -------------------------Enable and Disable Add to my list button----------------------------------

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
    selectAll.addEventListener("change", function () {
        checkboxes.forEach((checkbox) => {
            checkbox.checked = this.checked;
        });
        updateButtonState();
    });

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

// -------------------------Enable and Disable Add to my list button-----(end)-----------------------------
// -------------------------Enable and Disable Add to my list button-----(end)-----------------------------


// -------------------------Update filters and table-----(start)-----------------------------
// -------------------------Update filters and table-----(start)-----------------------------

document.addEventListener("DOMContentLoaded", function () {
    const stateFilter = document.getElementById("state-filter");
    const countyFilter = document.getElementById("county-filter");
    const saletypeFilter = document.getElementById("saletype-filter");
    const rows = document.querySelectorAll("#leads-table tbody tr");

    const rangeSlider = document.getElementById("range-slider");
    const rangeMin = document.getElementById("range-min");
    const rangeMax = document.getElementById("range-max");

    const possiblerangeSlider = document.getElementById("possible-range-slider");
    const possiblerangeMin = document.getElementById("possible-min");
    const possiblerangeMax = document.getElementById("possible-max");

    const verifiedrangeSlider = document.getElementById("verified-range-slider");
    const verifiedrangeMin = document.getElementById("verified-min");
    const verifiedrangeMax = document.getElementById("verified-max");


    // Initialize the range slider
    noUiSlider.create(rangeSlider, {
        start: [1000, 1000000],
        connect: true,
        range: {
            min: 1000,
            max: 1000000,
        },
        step: 1000,
    });
    // Initialize the possible range slider
    noUiSlider.create(possiblerangeSlider, {
        start: [1000, 1000000],
        connect: true,
        range: {
            min: 1000,
            max: 1000000,
        },
        step: 1000,
    });
    // Initialize the verified range slider
    noUiSlider.create(verifiedrangeSlider, {
        start: [1000, 1000000],
        connect: true,
        range: {
            min: 1000,
            max: 1000000,
        },
        step: 1000,
    });
    // Populate the state and county filters based on table data
    function populateFilters() {
        const states = new Set();
        const counties = {};
        const saletypes = {};

        rows.forEach((row) => {
            const state = row.querySelector(".state").textContent.trim();
            const county = row.querySelector(".county").textContent.trim();
            const saletype = row.querySelector(".saletype").textContent.trim();

            states.add(state);

            if (!counties[state]) {
                counties[state] = new Set();
            }
            counties[state].add(county);

            if (!saletypes[county]) {
                saletypes[county] = new Set();
            }
            saletypes[county].add(saletype);
        });

        // Populate state dropdown
        states.forEach((state) => {
            const option = document.createElement("option");
            option.value = state;
            option.textContent = state;
            stateFilter.appendChild(option);
        });

        // Update county filter when a state is selected
        stateFilter.addEventListener("change", function () {
            countyFilter.innerHTML = '<option value="">All</option>';
            countyFilter.disabled = stateFilter.value === "";

            if (stateFilter.value && counties[stateFilter.value]) {
                counties[stateFilter.value].forEach((county) => {
                    const option = document.createElement("option");
                    option.value = county;
                    option.textContent = county;
                    countyFilter.appendChild(option);
                });
            }
            filterTable();
        });
        // Update saletype filter when a county is selected
        countyFilter.addEventListener("change", function () {
            saletypeFilter.innerHTML = 'option value="">All</option>';
            saletypeFilter.disabled = countyFilter.value === "";

            if (countyFilter.value && saletypes[countyFilter.value]) {
                saletypes[countyFilter.value].forEach((saletype) => {
                    const option = document.createElement("option");
                    option.value = saletype;
                    option.textContent = saletype;
                    saletypeFilter.appendChild(option);
                });
            }
            filterTable();
        });



    }

    // Filter the table rows based on selected state and county
    function filterTable() {
        const stateValue = stateFilter.value.toLowerCase();
        const countyValue = countyFilter.value.toLowerCase();
        const saletypeValue = saletypeFilter.value.toLowerCase();
        const [minAmount, maxAmount] = rangeSlider.noUiSlider.get().map(parseFloat);
        const [possibleminAmount, possiblemaxAmount] = possiblerangeSlider.noUiSlider.get().map(parseFloat);
        const [verifiedminAmount, verifiedmaxAmount] = verifiedrangeSlider.noUiSlider.get().map(parseFloat);

        rows.forEach((row) => {
            const stateCell = row.querySelector(".state").textContent.toLowerCase();
            const countyCell = row.querySelector(".county").textContent.toLowerCase();
            const saletypeCell = row.querySelector(".saletype").textContent.toLowerCase();
            const amountCell = parseFloat(row.querySelector(".amount").textContent) || 0;
            const possibleamountCell = parseFloat(row.querySelector(".possible-surplus").textContent) || 0;
            const verifiedamountCell = parseFloat(row.querySelector(".verified-surplus").textContent) || 0;

            const matchesState = stateValue === "" || stateCell === stateValue;
            const matchesCounty = countyValue === "" || countyCell === countyValue;
            const matchesSaletype = saletypeValue === "" || saletypeCell === saletypeValue;
            const matchesAmount = amountCell >= minAmount && amountCell <= maxAmount;
            const possiblematchesAmount = possibleamountCell >= possibleminAmount && possibleamountCell <= possiblemaxAmount;
            const verifiedmatchesAmount = verifiedamountCell >= verifiedminAmount && verifiedamountCell <= verifiedmaxAmount;

            row.style.display = matchesState && matchesCounty && matchesSaletype && matchesAmount && possiblematchesAmount && verifiedmatchesAmount ? "" : "none";
        });
    }
    // Update saleprice slider values in the UI and filter the table
    rangeSlider.noUiSlider.on("update", function (values) {
        rangeMin.textContent = Math.round(values[0]);
        rangeMax.textContent = Math.round(values[1]);
        filterTable();
    });
    // Update possible surplus slider values in the UI and filter the table
    possiblerangeSlider.noUiSlider.on("update", function (values) {
        possiblerangeMin.textContent = Math.round(values[0]);
        possiblerangeMax.textContent = Math.round(values[1]);
        filterTable();
    });
    // Update possible surplus slider values in the UI and filter the table
    verifiedrangeSlider.noUiSlider.on("update", function (values) {
        verifiedrangeMin.textContent = Math.round(values[0]);
        verifiedrangeMax.textContent = Math.round(values[1]);
        filterTable();
    });

    // Initialize filters and table
    populateFilters();
    stateFilter.addEventListener("change", filterTable);
    countyFilter.addEventListener("change", filterTable);
    saletypeFilter.addEventListener("change", filterTable);
});

// -------------------------Update filters and table-----(end)-----------------------------
// -------------------------Update filters and table-----(end)-----------------------------

// -------------------------toggle filters button-----(start)-----------------------------


// Reuseable function (copied to surplusindex.js)
// -------------------------toggle filters button-----(start)-----------------------------

function toggleFilters(togglebtn, hide_id) {
    const x = document.getElementById(hide_id); // hide_id = section id to be hidden
    const y = document.getElementById(togglebtn); // togglebtn = button id that will perform the action

    if (x.style.display === "flex") {
        x.style.display = "none";
        y.innerText = "Show Filters";
    } else {
        x.style.display = "flex";
        y.innerText = "Hide Filters";
    }
}


// -------------------------toggle filters button-----(end)-----------------------------
// -------------------------toggle filters button-----(end)-----------------------------

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