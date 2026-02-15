const nextBtn = document.getElementById('nextBtn');
let valid_username = false;
let valid_email = false;
let valid_password = false;
function buttonstate() {
    if (valid_username && valid_password && valid_email) {
        nextBtn.removeAttribute('disabled');
    } else {
        nextBtn.disabled = true;
    }
}

const usernameField = document.getElementById('username');
const feedBackAreaUsername = document.getElementById("invalid_user");
usernameField.addEventListener("keyup", (e) => {

    const usernameVal = e.target.value;
    // usernameField.classList.remove("is-invalid");
    // feedBackArea.style.display = "none";

    if (usernameVal.length > 0) {
        fetch("/validate-username", {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.username_error) {
                    usernameField.classList.add("is-invalid");
                    // feedBackAreaUsername.style.display = "block";
                    feedBackAreaUsername.classList.add("show");
                    feedBackAreaUsername.innerHTML = `<p>${data.username_error}</p>`;
                    valid_username = false;
                } else {
                    valid_username = true;
                    feedBackAreaUsername.classList.remove("show");
                    usernameField.classList.remove("is-invalid");
                }
                buttonstate();
            });
    }
});

const emailField = document.getElementById('email');
const feedBackAreaEmail = document.getElementById("invalid_email");

emailField.addEventListener("keyup", (e) => {

    const emailVal = e.target.value;

    // emailField.classList.remove("is-invalid");
    // emailFeedBackArea.style.display = "none";

    if (emailVal.length > 0) {
        fetch("/validate-email", {
            body: JSON.stringify({ email: emailVal }),
            method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("data", data);
                if (data.email_error) {
                    valid_email = false;
                    emailField.classList.add("is-invalid");
                    feedBackAreaEmail.classList.add("show");
                    feedBackAreaEmail.innerHTML = `<p>${data.email_error}</p>`;
                } else {
                    valid_email = true;
                    emailField.classList.remove("is-invalid");
                    feedBackAreaEmail.classList.remove("show");
                }
                buttonstate();
            });
    }
})

const passwordField = document.getElementById("password");
const feedBackAreaPassword = document.getElementById("invalid_password")
passwordField.addEventListener("keyup", (e) => {
    const password = e.target.value;
    if (password.length < 8) {
        passwordField.classList.add("is-invalid");
        feedBackAreaPassword.classList.add("show");
        valid_password = false;
        feedBackAreaPassword.innerHTML = `<p>Password Must be at least 8 characters long</p>`;
    } else {
        valid_password = true;
        passwordField.classList.remove("is-invalid");
        feedBackAreaPassword.classList.remove("show");
    }
    buttonstate();
})