//--------------Update task status function------------
// select id must contain the task id. Use the function 
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function update_task_status(taskId) {
    const select = document.getElementById(`update_status_${taskId}`);
    const status = document.getElementById(`update_status_${taskId}`).value;

    fetch(`/Project-Manager/update-status/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        },
        body: JSON.stringify({ task_id: taskId, status: status })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                select.style.backgroundColor = "#6fdfa0";
                setTimeout(() => {
                    select.style.backgroundColor = "";
                }, 1500);
            } else {
                select.style.backgroundColor = "#df916fff";
                setTimeout(() => {
                    select.style.backgroundColor = "";
                }, 1500);
            }

        })
        .catch(err => {
            select.style.backgroundColor = "#df916fff";
            setTimeout(() => select.style.backgroundColor = "");
            console.error("⚡ Error:", err);
        });
}

// -------Update assignment Function------ 
function update_assignment(userId, taskId) {
    const statusSpan = document.getElementById(`assign_status_${userId}_${taskId}`);

    fetch(`/Project-Manager/update-assignment/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        },
        body: JSON.stringify({ user_id: userId, task_id: taskId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.status === "added") {
                    statusSpan.innerHTML = `<i class="bi bi-check-circle-fill text-success"></i>`;
                } else if (data.status === "removed") {
                    statusSpan.innerHTML = `<i class="bi bi-check-circle-fill text-danger"></i>`;
                }
            } else {
                statusSpan.innerHTML = `<i class="bi bi-x-circle-fill text-danger"></i>`;
            }

            // remove the icon after 1 second
            setTimeout(() => statusSpan.innerHTML = "", 1000);
        })
        .catch(err => {
            statusSpan.innerHTML = `<i class="bi bi-x-circle-fill text-danger"></i>`;
            setTimeout(() => statusSpan.innerHTML = "", 1000);
            console.error("⚡ Error:", err);
        });
}

function assignSkiptrace(select, lead_id) {
    const user_id = select.value;

    fetch("/Project-Manager/assign-skiptrace/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            lead_id: lead_id,
            user_id: user_id
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                select.style.backgroundColor = "#6fdfa0";
                setTimeout(() => {
                    select.style.backgroundColor = "";
                }, 1500);
            } else {
                select.style.backgroundColor = "#df916fff";
                setTimeout(() => {
                    select.style.backgroundColor = "";
                }, 1500);
            }
        });
}


// this function will save any fields in Foreclosure model
// use it like...............
// <input type="text" onchange="saveField('{{ i.id }}', 'case_status', this)" value="{{ i.case_status }}">
// <input type="date" onchange="saveField('{{ i.id }}', 'sale_date', this)" value="{{ i.sale_date }}">
// <select onchange="saveField('{{ i.id }}', 'sale_status', this)">
function Upload_CUF(id, action, volume, event, input) {
    event.preventDefault();

    input.style.transition = "background 0.3s";
    input.style.background = "#fdd9b2ff"; // yellow-light
    input.value = "Processing..."

    fetch(`/Project-Manager/Upload-CUF/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ id, action, volume })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                input.style.transition = "background 0.5s";
                input.style.background = "#dfffabff"; // green
                setTimeout(() => {
                    input.style.background = "#17d080ff";
                    input.value = "Completed"
                    input.disabled = true;
                }, 800);
            } else {
                // 4️⃣ Optional: flash red on error
                input.style.background = "#f7a8a8ff"; // red
                input.value = "Failed";
            }
        });
}

function markInstance(el, model, field, source, destination) {
    const label = el.closest(".property-row");
    fetch(`/Project-Manager/mark-Instance/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({ model, field, source, destination })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                label.style.transition = "background 0.5s";
                label.style.background = "#ebe95bff"; // green
                setTimeout(() => {
                    label.style.transition = "background 0.5s";
                    label.style.background = "#dcf8afff"; // green
                }, 800);
            } else {
                // 4️⃣ Optional: flash red on error
                label.style.background = "#f7a8a8ff"; // red
                console.error(data.error);
            }
        });
}