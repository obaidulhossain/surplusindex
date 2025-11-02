
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie("csrftoken");

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


// ============================================================
// Global Remove m2m from CustomDeliveryClients
// ============================================================
// Add below button 
//<button data-remove-client data-client-id="{{ client_instance.id }}" data-field="old_leads" data-related-id="{{ lead.id }}" class="button"> Remove</button>
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-remove-client]").forEach((btn) => {
        btn.addEventListener("click", function () {
            const clientId = this.dataset.clientId;
            const field = this.dataset.field;
            const relatedId = this.dataset.relatedId;
            const row = this.closest("tr");
            const tableBody = row.closest("tbody");

            if (!clientId || !field || !relatedId) {
                alert("Missing required data attributes!");
                return;
            }

            if (!confirm("Remove this item?")) return;

            fetch("/remove-client-m2m/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrftoken,
                },
                body: new URLSearchParams({
                    client_id: clientId,
                    field: field,
                    related_id: relatedId,
                }),
            })
                .then((res) => res.json())
                .then((data) => {
                    if (data.success) {
                        // Fade out and remove the row
                        row.style.transition = "opacity 0.4s ease";
                        row.style.opacity = "0";
                        setTimeout(() => {
                            row.remove();

                            // If no rows left, show “No items found”
                            if (tableBody.querySelectorAll("tr").length === 0) {
                                const tr = document.createElement("tr");
                                const td = document.createElement("td");
                                td.colSpan = 10;
                                td.style.textAlign = "center";
                                td.style.padding = "10px";
                                td.textContent = "No items found.";
                                tr.appendChild(td);
                                tableBody.appendChild(tr);
                            }
                        }, 400);
                    } else {
                        alert("Error: " + (data.error || "Failed to remove."));
                    }
                })
                .catch((err) => alert("Request failed: " + err));
        });
    });
});

// ============================================================
// ============================================================