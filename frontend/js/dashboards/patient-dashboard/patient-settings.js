/* ============================================================
   ORALAI - PATIENT SETTINGS
   ============================================================ */


/* ============================================================
   API URL
   ============================================================ */

const API_URL = "http://127.0.0.1:5000";


/* ============================================================
   PAGE LOAD
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    /*
     * Get logged-in user's ID.
     */
    const userId = localStorage.getItem("user_id");


    /*
     * If user is not logged in,
     * go to login page.
     */
    if (!userId) {

        window.location.href = "../../login.html";

        return;
    }


    /*
     * Load user information.
     */
    loadUserProfile(userId);


    /*
     * Setup avatar dropdown.
     */
    setupUserMenu();


    /*
     * Setup logout.
     */
    setupLogout();


    /*
     * Setup password form.
     */
    setupPasswordForm(userId);


    /*
     * Setup dark mode.
     */
    setupDarkMode();

});



/* ============================================================
   LOAD USER PROFILE
   ============================================================ */

async function loadUserProfile(userId) {

    try {

        const response = await fetch(
            `${API_URL}/users/${userId}`
        );


        const data = await response.json();


        /*
         * Check backend response.
         */
        if (!response.ok || !data.success) {

            console.error(
                "Failed to load user information."
            );

            return;
        }


        const user = data.user;


        /*
         * Save user information locally.
         */
        localStorage.setItem(
            "user_fullname",
            user.fullname
        );


        localStorage.setItem(
            "user_email",
            user.email
        );


        /*
         * Display account name.
         */
        const accountName =
            document.getElementById("accountName");


        if (accountName) {

            accountName.textContent =
                user.fullname || "-";
        }


        /*
         * Display account email.
         */
        const accountEmail =
            document.getElementById("accountEmail");


        if (accountEmail) {

            accountEmail.textContent =
                user.email || "-";
        }


        /*
         * Update avatar.
         */
        updateAvatar(user);

    }


    catch (error) {

        console.error(
            "Error loading user profile:",
            error
        );

    }

}



/* ============================================================
   UPDATE AVATAR
   ============================================================ */

function updateAvatar(user) {

    const avatarImage =
        document.getElementById("userAvatarImage");


    const avatarInitial =
        document.getElementById("userAvatarInitial");


    /*
     * Stop if elements don't exist.
     */
    if (!avatarImage || !avatarInitial) {

        return;
    }


    /*
     * Get actual user's first letter.
     *
     * Example:
     *
     * Madhusha Udani
     *
     * => M
     */
    const initial =
        getInitial(user.fullname);


    /*
     * Set the initial.
     */
    avatarInitial.textContent = initial;


    /*
     * IMPORTANT:
     *
     * Hide both first.
     *
     * This prevents any wrong/default
     * letter from appearing during loading.
     */
    avatarImage.style.display = "none";

    avatarInitial.style.display = "none";


    /* ========================================================
       PROFILE PHOTO EXISTS
       ======================================================== */

    if (user.profile_photo_url) {


        /*
         * Build profile photo URL.
         *
         * Cache-busting (?t=...)
         * ensures newly uploaded/deleted photo
         * is reflected immediately.
         */
        const photoUrl =
            `${API_URL}${user.profile_photo_url}?t=${Date.now()}`;


        /*
         * Set image source.
         */
        avatarImage.src = photoUrl;


        /*
         * When image loads successfully,
         * show the image.
         */
        avatarImage.onload = function () {

            avatarImage.style.display = "block";

            avatarInitial.style.display = "none";

        };


        /*
         * If image cannot load,
         * use user's initial.
         */
        avatarImage.onerror = function () {

            avatarImage.style.display = "none";

            avatarInitial.style.display = "flex";

        };

    }


    /* ========================================================
       NO PROFILE PHOTO
       ======================================================== */

    else {


        /*
         * Remove old image source.
         */
        avatarImage.removeAttribute("src");


        /*
         * Show user's actual initial.
         */
        avatarInitial.style.display = "flex";

    }

}



/* ============================================================
   GET USER INITIAL
   ============================================================ */

function getInitial(fullName) {

    /*
     * If name is missing,
     * use P as Patient.
     */
    if (!fullName || !fullName.trim()) {

        return "P";
    }


    /*
     * Return first character
     * converted to uppercase.
     */
    return fullName
        .trim()
        .charAt(0)
        .toUpperCase();

}



/* ============================================================
   USER DROPDOWN
   ============================================================ */

function setupUserMenu() {

    const button =
        document.getElementById("userMenuButton");


    const dropdown =
        document.getElementById("userDropdown");


    /*
     * Stop if elements don't exist.
     */
    if (!button || !dropdown) {

        return;
    }


    /*
     * Open / close dropdown.
     */
    button.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();


            const isOpen =
                dropdown.classList.toggle("show");


            button.setAttribute(
                "aria-expanded",
                isOpen ? "true" : "false"
            );

        }
    );


    /*
     * Clicking inside dropdown
     * should not close it immediately.
     */
    dropdown.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

        }
    );


    /*
     * Clicking outside closes dropdown.
     */
    document.addEventListener(
        "click",
        function () {

            dropdown.classList.remove("show");


            button.setAttribute(
                "aria-expanded",
                "false"
            );

        }
    );

}



/* ============================================================
   LOGOUT
   ============================================================ */

function setupLogout() {

    const logoutLink =
        document.getElementById("logoutLink");


    if (!logoutLink) {

        return;
    }


    logoutLink.addEventListener(
        "click",
        function (event) {

            event.preventDefault();


            /*
             * Ask user for confirmation.
             */
            const confirmed =
                confirm(
                    "Are you sure you want to logout?"
                );


            /*
             * If Cancel was selected,
             * do nothing.
             */
            if (!confirmed) {

                return;
            }


            /*
             * Remove login information.
             */
            localStorage.removeItem("user_id");

            localStorage.removeItem("user_fullname");

            localStorage.removeItem("user_email");


            /*
             * Redirect to login page.
             */
            window.location.href =
                "../../login.html";

        }
    );

}



/* ============================================================
   CHANGE PASSWORD
   ============================================================ */

function setupPasswordForm(userId) {

    const form =
        document.getElementById(
            "changePasswordForm"
        );


    const currentPassword =
        document.getElementById(
            "currentPassword"
        );


    const newPassword =
        document.getElementById(
            "newPassword"
        );


    const confirmPassword =
        document.getElementById(
            "confirmPassword"
        );


    const button =
        document.getElementById(
            "changePasswordBtn"
        );


    const message =
        document.getElementById(
            "passwordMessage"
        );


    /*
     * Check required elements.
     */
    if (
        !form ||
        !currentPassword ||
        !newPassword ||
        !confirmPassword ||
        !button ||
        !message
    ) {

        return;
    }


    /*
     * Form submit.
     */
    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            /*
             * Clear previous message.
             */
            message.textContent = "";

            message.className = "message";


            /*
             * Get values.
             */
            const currentValue =
                currentPassword.value.trim();


            const newValue =
                newPassword.value;


            const confirmValue =
                confirmPassword.value;


            /* =================================================
               VALIDATION
               ================================================= */


            /*
             * Current password required.
             */
            if (!currentValue) {

                showPasswordMessage(
                    "Please enter your current password.",
                    "error"
                );

                currentPassword.focus();

                return;
            }


            /*
             * New password minimum length.
             */
            if (newValue.length < 6) {

                showPasswordMessage(
                    "New password must contain at least 6 characters.",
                    "error"
                );

                newPassword.focus();

                return;
            }


            /*
             * Confirm password must match.
             */
            if (newValue !== confirmValue) {

                showPasswordMessage(
                    "New password and confirmation password do not match.",
                    "error"
                );

                confirmPassword.focus();

                return;
            }


            /*
             * New password should not be
             * exactly the same as old password.
             */
            if (currentValue === newValue) {

                showPasswordMessage(
                    "New password must be different from your current password.",
                    "error"
                );

                newPassword.focus();

                return;
            }


            /*
             * Disable button while request
             * is being processed.
             */
            button.disabled = true;

            button.textContent =
                "Changing Password...";


            try {


                /* =============================================
                   SEND REQUEST TO BACKEND
                   ============================================= */

                const response =
                    await fetch(
                        `${API_URL}/users/${userId}/password`,
                        {
                            method: "PUT",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                current_password:
                                    currentValue,

                                new_password:
                                    newValue

                            })
                        }
                    );


                const data =
                    await response.json();


                /* =============================================
                   ERROR RESPONSE
                   ============================================= */

                if (!response.ok || !data.success) {

                    showPasswordMessage(
                        data.message ||
                        "Failed to change password.",
                        "error"
                    );

                    return;
                }


                /* =============================================
                   SUCCESS
                   ============================================= */

                showPasswordMessage(
                    "Password changed successfully.",
                    "success"
                );


                /*
                 * Clear all password fields.
                 */
                form.reset();

            }


            catch (error) {

                console.error(
                    "Password change error:",
                    error
                );


                showPasswordMessage(
                    "Unable to connect to the server. Please try again.",
                    "error"
                );

            }


            finally {

                /*
                 * Enable button again.
                 */
                button.disabled = false;

                button.textContent =
                    "Change Password";

            }

        }
    );

}



/* ============================================================
   PASSWORD MESSAGE
   ============================================================ */

function showPasswordMessage(
    text,
    type
) {

    const message =
        document.getElementById(
            "passwordMessage"
        );


    if (!message) {

        return;
    }


    message.textContent = text;

    message.className =
        `message ${type}`;

}



/* ============================================================
   DARK MODE
   ============================================================ */

function setupDarkMode() {

    const toggle =
        document.getElementById(
            "darkModeToggle"
        );


    if (!toggle) {

        return;
    }


    /*
     * Read previously saved theme.
     */
    const savedTheme =
        localStorage.getItem(
            "oralai_theme"
        );


    /*
     * Dark mode is enabled when
     * localStorage value is "dark".
     */
    const isDark =
        savedTheme === "dark";


    /*
     * Set toggle state.
     */
    toggle.checked = isDark;


    /*
     * Apply current theme.
     */
    applyTheme(isDark);


    /*
     * Listen for changes.
     */
    toggle.addEventListener(
        "change",
        function () {

            const darkMode =
                toggle.checked;


            /*
             * Apply theme immediately.
             */
            applyTheme(darkMode);


            /*
             * Save theme preference.
             */
            localStorage.setItem(
                "oralai_theme",
                darkMode
                    ? "dark"
                    : "light"
            );

        }
    );

}



/* ============================================================
   APPLY THEME
   ============================================================ */

function applyTheme(isDark) {

    document.body.classList.toggle(
        "dark-mode",
        isDark
    );

}
