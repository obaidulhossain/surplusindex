function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie("csrftoken");
function updateAutomationField(field, value) {
    const id = document.querySelector(".automate-section").dataset.id;

    fetch(`/Automation/update/${id}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
            field: field,
            value: value
        })
    })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                console.error(data.error);
            }
        });
}
function updateSubscription(sub_id, checked) {
    const id = document.querySelector(".automate-section").dataset.id;
    const button = document.getElementById("pay-btn");

    fetch(`/Automation/update-subscription/${id}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        body: JSON.stringify({
            sub_id: sub_id,
            checked: checked
        })
    })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                console.error(data.error);
            }
        });
}

function toggleState(input) {
    const id = document.querySelector(".automate-section").dataset.id;

    fetch(`/Automation/update-state/${id}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}"
        },
        body: JSON.stringify({
            state: input.value,
            checked: input.checked
        })
    });
}

// const startBtn = document.getElementById('startAutomationBtn');
// const confirmDiv = document.getElementById('confirmDiv');
// const confirmMessage = document.getElementById('confirmMessage');
// const confirmYes = document.getElementById('confirmYes');
// const confirmNo = document.getElementById('confirmNo');
// const messageDiv = document.getElementById('message');

// function showMessage(msg, duration = 10000) {
//     messageDiv.innerText = msg;
//     messageDiv.style.display = 'block';

//     setTimeout(() => {
//         messageDiv.style.display = 'none';
//         location.reload();
//     }, duration);
// }
// startBtn.addEventListener('click', () => {
//     confirmMessage.innerText = `Are you sure you want to automate your lead generation for current settings?\nAutomation fee will be charged from Your default payment method.`;
//     confirmDiv.style.display = 'block';
// });

// confirmNo.addEventListener('click', () => {
//     confirmDiv.style.display = 'none';
// });

// confirmYes.addEventListener('click', async () => {
//     confirmDiv.style.display = 'none';
//     showMessage("Payment Processing...");
//     const id = document.querySelector(".automate-section").dataset.id;
//     try {
//         const response = await fetch('/Automation/pay/2/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': csrftoken
//             }
//         });
//         const data = await response.json();
//         if (!data.success) {
//             showMessage(data.error, 5000);
//         }
//     } catch (err) {
//         console.error(err);
//         showMessage('Server error. Try again.', 5000);
//     }
// });

// function payAndAutomate() {
//     const id = document.querySelector(".automate-section").dataset.id;
//     // Show confirmation
//     const confirmed = confirm(`Are you sure you want to automate with the following settings?\nThe respective subscription price will be billed to your default payment method.`);
//     if (!confirmed) return;
//     fetch(`/Automation/pay/${id}/`, {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//             "X-CSRFToken": csrftoken
//         }
//     })
//         .then(res => res.json())
//         .then(data => {
//             if (data.success) {
//                 alert("Payment Processing...");
//             } else {
//                 alert(data.error);
//             }
//         });
// }



// const stripe = Stripe("YOUR_STRIPE_PUBLISHABLE_KEY");
// const elements = stripe.elements();
// const cardElement = elements.create("card");
// cardElement.mount("#card-element");

// const startBtn = document.getElementById('startAutomationBtn');
// const paymentModal = document.getElementById('paymentModal');
// const paymentSummary = document.getElementById('paymentSummary');
// const savedMethodsDiv = document.getElementById('savedPaymentMethods');
// const modalCancel = document.getElementById('modalCancel');
// const modalConfirm = document.getElementById('modalConfirm');
// const newCardContainer = document.getElementById('newCardContainer');
// const messageDiv = document.getElementById('message');

// let selectedPaymentMethod = null;

// function showMessage(msg, duration = 10000) {
//     messageDiv.innerText = msg;
//     messageDiv.style.display = 'block';

//     setTimeout(() => {
//         messageDiv.style.display = 'none';
//         location.reload();
//     }, duration);
// }

// const processingOverlay = document.getElementById("processingOverlay");
// const processingText = document.getElementById("processingText");

// function showMessage(message, duration = 3000, reload = true) {
//     processingText.innerText = message;
//     processingOverlay.style.display = "flex";

//     setTimeout(() => {
//         processingOverlay.style.display = "none";
//         if (reload) {
//             location.reload();
//         }
//     }, duration);
// }

// function showProcessing(message = "Processing payment...") {
//     processingText.innerText = message;
//     processingOverlay.style.display = "flex";
// }

// function hideProcessing() {
//     processingOverlay.style.display = "none";
// }

// // Open modal
// startBtn.addEventListener('click', async () => {
//     paymentSummary.innerText =
//         "You are about to activate automation with the selected subscription. Please choose a payment method.";

//     paymentModal.style.display = "flex";

//     await loadPaymentMethods();
// });

// // Load saved Stripe cards
// async function loadPaymentMethods() {
//     savedMethodsDiv.innerHTML = "Loading saved payment methods...";

//     const response = await fetch("/Automation/billing/payment-methods/");
//     const data = await response.json();

//     savedMethodsDiv.innerHTML = "";

//     if (data.methods.length === 0) {
//         savedMethodsDiv.innerHTML = "<p>No saved cards found.</p>";
//         document.querySelector('input[value="new"]').checked = true;
//         newCardContainer.style.display = "block";
//         return;
//     }

//     data.methods.forEach(pm => {
//         const div = document.createElement("div");
//         div.innerHTML = `
//             <label>
//                 <input type="radio" name="payment_choice" value="${pm.id}">
//                 ${pm.brand.toUpperCase()} **** ${pm.last4}
//                 (Exp: ${pm.exp_month}/${pm.exp_year})
//                 ${pm.is_default ? "<strong> - Default</strong>" : ""}
//             </label>
//         `;
//         savedMethodsDiv.appendChild(div);
//     });
// }

// // Toggle new card form
// document.addEventListener("change", function (e) {
//     if (e.target.name === "payment_choice") {
//         if (e.target.value === "new") {
//             newCardContainer.style.display = "block";
//             selectedPaymentMethod = "new";
//         } else {
//             newCardContainer.style.display = "none";
//             selectedPaymentMethod = e.target.value;
//         }
//     }
// });

// // Cancel modal
// modalCancel.addEventListener("click", () => {
//     paymentModal.style.display = "none";
// });

// // Confirm & Pay
// modalConfirm.addEventListener("click", async () => {

//     const id = document.querySelector(".automate-section").dataset.id;

//     let paymentMethodId = selectedPaymentMethod;

//     if (!paymentMethodId) {
//         alert("Please select a payment method.");
//         return;
//     }

//     // If new card selected
//     if (paymentMethodId === "new") {
//         const { paymentMethod, error } = await stripe.createPaymentMethod({
//             type: "card",
//             card: cardElement
//         });

//         if (error) {
//             document.getElementById("card-errors").innerText = error.message;
//             return;
//         }

//         paymentMethodId = paymentMethod.id;
//     }

//     paymentModal.style.display = "none";
//     showProcessing("Processing payment securely...");
//     modalConfirm.disabled = true;

//     try {
//         const response = await fetch(`/Automation/pay/${id}/`, {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": csrftoken
//             },
//             body: JSON.stringify({
//                 payment_method_id: paymentMethodId
//             })
//         });

//         const data = await response.json();

//         /* -------------------------------
//         If Stripe requires authentication
//         ---------------------------------*/
//         if (data.requires_action) {

//             const { error, paymentIntent } = await stripe.confirmCardPayment(
//                 data.client_secret
//             );

//             if (error) {
//                 // showMessage(error.message, 6000);
//                 hideProcessing();
//                 modalConfirm.disabled = false;
//                 showMessage(error.message, 5000, false);
//                 return;
//             }

//             if (paymentIntent.status === "succeeded") {
//                 showMessage("Payment successful. Activating automation...");
//                 return;
//             }
//         }

//         /* -------------------------------
//         Normal success
//         ---------------------------------*/
//         if (data.success) {
//             showMessage("Payment successful. Activating automation...");
//             return;
//         }

//         /* -------------------------------
//         Error fallback
//         ---------------------------------*/
//         showMessage(data.error || "Payment failed.", 6000);

//     } catch (err) {
//         console.error(err);
//         showMessage("Server error. Try again.", 5000);
//     }
// });

// const stripe = Stripe("{{ STRIPE_PUBLIC_KEY }}");
// let elements = stripe.elements();
// let cardElement = elements.create("card");
// cardElement.mount("#card-element");

// const startBtn = document.getElementById('startAutomationBtn');
// const paymentModal = document.getElementById('paymentModal');
// const paymentSummary = document.getElementById('paymentSummary');
// const savedMethodsDiv = document.getElementById('savedPaymentMethods');
// const modalCancel = document.getElementById('modalCancel');
// const modalConfirm = document.getElementById('modalConfirm');
// const newCardContainer = document.getElementById('newCardContainer');
// const messageDiv = document.getElementById('message');

// let selectedPaymentMethod = null;

// // -------------------------------
// // Messages & Overlay
// // -------------------------------
// function showMessage(msg, duration = 3000, reload = true) {
//     messageDiv.innerText = msg;
//     messageDiv.style.display = "block";

//     setTimeout(() => {
//         messageDiv.style.display = "none";
//         if (reload) location.reload();
//     }, duration);
// }

// function showProcessing(msg = "Processing payment...") {
//     messageDiv.innerText = msg;
//     messageDiv.style.display = "block";
// }

// function hideProcessing() {
//     messageDiv.style.display = "none";
// }

// // -------------------------------
// // Open Modal
// // -------------------------------
// startBtn.addEventListener('click', async () => {
//     paymentSummary.innerText =
//         "You are about to activate automation. Please choose a payment method.";

//     paymentModal.style.display = "flex";
//     await loadPaymentMethods();
// });

// // -------------------------------
// // Load Saved Stripe Cards
// // -------------------------------
// async function loadPaymentMethods() {
//     savedMethodsDiv.innerHTML = "Loading saved payment methods...";
//     const response = await fetch("/Automation/billing/payment-methods/");
//     const data = await response.json();
//     savedMethodsDiv.innerHTML = "";

//     if (!data.methods.length) {
//         savedMethodsDiv.innerHTML = `<label>
//             <input type="radio" name="payment_choice" value="new" checked>
//             Add New Card
//         </label>`;
//         newCardContainer.style.display = "block";
//         selectedPaymentMethod = "new";
//         return;
//     }

//     data.methods.forEach(pm => {
//         const div = document.createElement("div");
//         div.innerHTML = `
//             <label>
//                 <input type="radio" name="payment_choice" value="${pm.id}" ${pm.is_default ? "checked" : ""}>
//                 ${pm.brand.toUpperCase()} **** ${pm.last4}
//                 (Exp: ${pm.exp_month}/${pm.exp_year})
//                 ${pm.is_default ? "<strong>- Default</strong>" : ""}
//             </label>
//         `;
//         savedMethodsDiv.appendChild(div);
//         if (pm.is_default) selectedPaymentMethod = pm.id;
//     });

//     // Always include option for new card
//     const newDiv = document.createElement("div");
//     newDiv.innerHTML = `<label>
//         <input type="radio" name="payment_choice" value="new"> Add New Card
//     </label>`;
//     savedMethodsDiv.appendChild(newDiv);
// }

// // -------------------------------
// // Toggle New Card Form
// // -------------------------------
// document.addEventListener("change", function (e) {
//     if (e.target.name === "payment_choice") {
//         if (e.target.value === "new") {
//             newCardContainer.style.display = "block";
//             selectedPaymentMethod = "new";
//         } else {
//             newCardContainer.style.display = "none";
//             selectedPaymentMethod = e.target.value;
//         }
//     }
// });

// // -------------------------------
// // Cancel Modal
// // -------------------------------
// modalCancel.addEventListener("click", () => {
//     paymentModal.style.display = "none";
// });

// // -------------------------------
// // Confirm & Pay
// // -------------------------------
// modalConfirm.addEventListener("click", async () => {
//     const id = document.querySelector(".automate-section").dataset.id;

//     if (!selectedPaymentMethod) {
//         showMessage("Please select a payment method.", 5000, false);
//         return;
//     }

//     modalConfirm.disabled = true;
//     showProcessing("Processing payment securely...");
//     let paymentMethodId = selectedPaymentMethod;

//     // If new card selected
//     if (paymentMethodId === "new") {
//         const { paymentMethod, error } = await stripe.createPaymentMethod({
//             type: "card",
//             card: cardElement
//         });

//         if (error) {
//             document.getElementById("card-errors").innerText = error.message;
//             hideProcessing();
//             modalConfirm.disabled = false;
//             return;
//         }

//         paymentMethodId = paymentMethod.id;
//     }

//     try {
//         const response = await fetch(`/Automation/pay/${id}/`, {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json",
//                 "X-CSRFToken": csrftoken
//             },
//             body: JSON.stringify({ payment_method_id: paymentMethodId })
//         });
//         const data = await response.json();

//         // If Stripe requires 3DS authentication
//         if (data.requires_action) {
//             const { error, paymentIntent } = await stripe.confirmCardPayment(data.client_secret);

//             if (error) {
//                 hideProcessing();
//                 modalConfirm.disabled = false;
//                 showMessage(error.message, 5000, false);
//                 return;
//             }

//             if (paymentIntent.status === "succeeded") {
//                 showMessage("Payment successful. Activating automation...");
//                 return;
//             }
//         }

//         // Normal success
//         if (data.success) {
//             showMessage("Payment successful. Activating automation...");
//             return;
//         }

//         // Fallback error
//         showMessage(data.error || "Payment failed.", 5000, false);

//     } catch (err) {
//         console.error(err);
//         showMessage("Server error. Try again.", 5000, false);
//     } finally {
//         modalConfirm.disabled = false;
//     }
// });

