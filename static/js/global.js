// ============================================================
// Global Table Search Utility
// ============================================================
// Usage Example:
// enableTableSearch('leadSearch', 'leadsTable');
//
// 'leadSearch' → ID of input box
// 'leadsTable' → ID of table element (<table>)

function enableTableSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!input || !table) {
        console.warn("enableTableSearch: Input or table not found.");
        return;
    }

    const rows = table.querySelectorAll("tbody tr");

    input.addEventListener("keyup", function () {
        const query = this.value.trim().toLowerCase();

        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(query) ? "" : "none";
        });
    });
}

// ============================================================
// ============================================================