
// ============================================================
// OralAI - Login JavaScript
// Professional Notification System
// ============================================================

console.log("OralAI login.js loaded");

// Wait until HTML is fully loaded
document.addEventListener("DOMContentLoaded", function () {

    const loginForm = document.getElementById("loginForm");

    if (!loginForm) {
        console.error("Login form was not found.");
        return;
    }

    console.log("Login form found.");

    // ========================================================
    // NOTIFICATION MESSAGE FUNCTION
    // ========================================================

    function showMessage(message, type = "success") {

        let container = document.getElementById("toastContainer");

        // Create notification container if missing
        if (!container) {
            container = document.createElement("div");
            container.id = "toastContainer";
            container.className = "toast-container";

            container.setAttribute("role", "status");
            container.setAttribute("aria-live", "polite");

            document.body.appendChild(container);
        }

        // Remove previous notification
        container.replaceChildren();

        const toast = document.createElement("div");

        toast.className =
            "toast-message " +
            (type === "error" ? "error" : "success");

        // textContent safely displays the message as text
        toast.textContent = message;

        container.appendChild(toast);

        // Remove message automatically after 3 seconds
        setTimeout(function () {
            if (toast.parentElement === container) {
                toast.remove();
            }
        }, 3000);
    }

    // ========================================================
    // LOGIN FORM SUBMIT
    // ========================================================

    loginForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        console.log("Login submitted.");

        const emailInput = document.getElementById("email");
        const passwordInput = document.getElementById("password");

        // Check HTML inputs
        if (!emailInput || !passwordInput) {

            console.error("Email or password input was not found.");

            showMessage(
                "Login form error. Please check the form fields.",
                "error"
            );

            return;
        }

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        // ====================================================
        // VALIDATION
        // ====================================================

        if (!email || !password) {

            showMessage(
                "Please enter your email and password.",
                "error"
            );

            return;
        }

        // ====================================================
        // DISABLE LOGIN BUTTON
        // ====================================================

        const loginButton = loginForm.querySelector(
            'button[type="submit"]'
        );

        const originalButtonText = loginButton
            ? loginButton.textContent
            : "Login";

        if (loginButton) {
            loginButton.disabled = true;
            loginButton.textContent = "Logging in...";
        }

        try {

            console.log("Sending login request...");

            // =================================================
            // SEND LOGIN REQUEST TO FLASK
            // =================================================

            const response = await fetch(
                "http://127.0.0.1:5000/login",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );

            console.log("Server status:", response.status);

            // Read server response safely
            let data;

            try {
                data = await response.json();
            } catch (parseError) {
                data = {};
            }

            console.log("Login response:", data);

            // =================================================
            // LOGIN FAILED
            // =================================================

            if (!response.ok || !data.success) {

                showMessage(
                    data.message || "Login failed.",
                    "error"
                );

                return;
            }

            // =================================================
            // ADMIN LOGIN
            // =================================================

            if (data.role === "admin") {

                console.log("Admin login successful.");

                if (!data.admin) {

                    console.error("Admin data is missing:", data);

                    showMessage(
                        "Admin login response is incomplete.",
                        "error"
                    );

                    return;
                }

                // Save admin details
                localStorage.setItem(
                    "admin_id",
                    data.admin.id
                );

                localStorage.setItem(
                    "admin_fullname",
                    data.admin.fullname
                );

                localStorage.setItem(
                    "admin_email",
                    data.admin.email
                );

                // Remove old patient session
                localStorage.removeItem("user_id");
                localStorage.removeItem("user_fullname");
                localStorage.removeItem("user_email");

                // Show success message
                showMessage(
                    "Login successful!",
                    "success"
                );

                // Redirect to admin dashboard
                console.log("Redirecting to admin dashboard...");

                window.location.href =
                    "dashboards/admin/admin-dashboard.html";

                return;
            }

            // =================================================
            // PATIENT LOGIN
            // =================================================

            if (data.role === "patient" || data.user) {

                console.log("Patient login successful.");

                if (!data.user) {

                    console.error("Patient data is missing:", data);

                    showMessage(
                        "Patient login response is incomplete.",
                        "error"
                    );

                    return;
                }

                // Save patient details
                localStorage.setItem(
                    "user_id",
                    data.user.id
                );

                localStorage.setItem(
                    "user_fullname",
                    data.user.fullname
                );

                localStorage.setItem(
                    "user_email",
                    data.user.email
                );

                // Remove old admin session
                localStorage.removeItem("admin_id");
                localStorage.removeItem("admin_fullname");
                localStorage.removeItem("admin_email");

                // Show success message
                showMessage(
                    "Login successful!",
                    "success"
                );

                // Redirect to patient dashboard
                console.log("Redirecting to patient dashboard...");

                window.location.href =
                    "dashboards/patient/patient-dashborad.html";

                return;
            }

            // =================================================
            // UNKNOWN ROLE
            // =================================================

            console.error("Unknown login response:", data);

            showMessage(
                "Account role was not recognized.",
                "error"
            );

        } catch (error) {

            // =================================================
            // CONNECTION / JAVASCRIPT ERROR
            // =================================================

            console.error("Login error:", error);

            showMessage(
                "Unable to connect to the server. Please check your connection.",
                "error"
            );

        } finally {

            // Re-enable button if the page has not redirected
            if (loginButton && loginButton.isConnected) {
                loginButton.disabled = false;
                loginButton.textContent = originalButtonText;
            }
        }

    });

});
