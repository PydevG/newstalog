document.addEventListener("DOMContentLoaded", function () {
    const toggleLinks = document.querySelectorAll(".toggle");
    const loginForm = document.querySelector(".form.login");
    const signupForm = document.querySelector(".form.signup");
    const passwordToggles = document.querySelectorAll(".eye-icon");

    // Toggle between login and signup forms
    toggleLinks.forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            loginForm.classList.toggle("active");
            signupForm.classList.toggle("active");
        });
    });

    // Toggle password visibility
    passwordToggles.forEach(icon => {
        icon.addEventListener("click", function () {
            const passwordInput = this.previousElementSibling;
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                this.classList.replace("bx-hide", "bx-show");
            } else {
                passwordInput.type = "password";
                this.classList.replace("bx-show", "bx-hide");
            }
        });
    });
});
