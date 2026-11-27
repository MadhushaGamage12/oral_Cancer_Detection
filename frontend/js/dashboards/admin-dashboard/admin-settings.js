/* ============================================================
   ORALAI - ADMIN SETTINGS JAVASCRIPT
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    const API_URL = "http://127.0.0.1:5000";


    /* ========================================================
       GET LOGGED-IN ADMIN
       ======================================================== */

    const adminId = localStorage.getItem("admin_id");


    /*
       IMPORTANT:
       Admin uses admin_id.
       Patient uses user_id.
    */

    if (!adminId) {

        window.location.href = "../../login.html";

        return;
    }


    /* ========================================================
       ELEMENTS
       ======================================================== */

    const userMenuButton =
        document.getElementById("userMenuButton");

    const userDropdown =
        document.getElementById("userDropdown");

    const logoutLink =
        document.getElementById("logoutLink");

    const userAvatarImage =
        document.getElementById("userAvatarImage");

    const userAvatarInitial =
        document.getElementById("userAvatarInitial");

    const accountName =
        document.getElementById("accountName");

    const accountEmail =
        document.getElementById("accountEmail");

    const changePasswordForm =
        document.getElementById("changePasswordForm");

    const passwordMessage =
        document.getElementById("passwordMessage");

    const changePasswordBtn =
        document.getElementById("changePasswordBtn");

    const darkModeToggle =
        document.getElementById("darkModeToggle");


    /* ========================================================
       GET INITIAL
       ======================================================== */

    function getInitial(fullname) {

        if (!fullname) {
            return "A";
        }

        return fullname
            .trim()
            .charAt(0)
            .toUpperCase();
    }


    /* ========================================================
       UPDATE ADMIN AVATAR
       ======================================================== */

    function updateAvatar(admin) {

        const initial =
            getInitial(admin.fullname);


        /* Hide both first */

        userAvatarImage.style.display = "none";

        userAvatarInitial.style.display = "none";


        /* Profile photo exists */

        if (admin.profile_photo_url) {

            userAvatarImage.src =
                `${API_URL}${admin.profile_photo_url}?t=${Date.now()}`;


            userAvatarImage.onload = function () {

                userAvatarImage.style.display = "block";

                userAvatarInitial.style.display = "none";
            };


            userAvatarImage.onerror = function () {

                userAvatarImage.style.display = "none";

                userAvatarInitial.textContent = initial;

                userAvatarInitial.style.display = "flex";
            };


            return;
        }


        /* No profile photo */

        userAvatarInitial.textContent = initial;

        userAvatarInitial.style.display = "flex";
    }


    /* ========================================================
       LOAD ADMIN PROFILE
       ======================================================== */

    async function loadAdminProfile() {

        try {

            /*
               IMPORTANT:
               Admin profile must use /admin/profile/
               NOT /users/
            */

            const response =
                await fetch(
                    `${API_URL}/admin/profile/${adminId}`
                );


            if (!response.ok) {

                throw new Error(
                    "Failed to load admin account information."
                );
            }


            const data =
                await response.json();


            if (!data.success || !data.admin) {

                throw new Error(
                    data.message ||
                    "Admin profile data not found."
                );
            }


            const admin =
                data.admin;


            /* Save latest admin details */

            localStorage.setItem(
                "admin_fullname",
                admin.fullname || ""
            );

            localStorage.setItem(
                "admin_email",
                admin.email || ""
            );


            /* Display account information */

            accountName.textContent =
                admin.fullname || "-";

            accountEmail.textContent =
                admin.email || "-";


            /* Update avatar */

            updateAvatar(admin);

        }

        catch (error) {

            console.error(
                "Error loading admin profile:",
                error
            );


            /* Fallback to localStorage */

            const fullname =
                localStorage.getItem(
                    "admin_fullname"
                );

            const email =
                localStorage.getItem(
                    "admin_email"
                );


            accountName.textContent =
                fullname || "-";

            accountEmail.textContent =
                email || "-";


            userAvatarInitial.textContent =
                getInitial(fullname);

            userAvatarInitial.style.display =
                "flex";
        }
    }


    /* ========================================================
       USER DROPDOWN
       ======================================================== */

    if (userMenuButton && userDropdown) {

        userMenuButton.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                const isOpen =
                    userDropdown.classList.toggle("show");


                userMenuButton.setAttribute(
                    "aria-expanded",
                    isOpen ? "true" : "false"
                );
            }
        );
    }


    /* ========================================================
       CLOSE DROPDOWN WHEN CLICKING OUTSIDE
       ======================================================== */

    document.addEventListener(
        "click",
        function (event) {

            if (
                !event.target.closest(".user-menu")
            ) {

                if (userDropdown) {

                    userDropdown.classList.remove("show");
                }

                if (userMenuButton) {

                    userMenuButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );
                }
            }
        }
    );


    /* ========================================================
       LOGOUT
       ======================================================== */

    if (logoutLink) {

        logoutLink.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                const confirmLogout =
                    confirm(
                        "Are you sure you want to logout?"
                    );


                if (!confirmLogout) {
                    return;
                }


                /*
                   Clear ADMIN session data
                */

                localStorage.removeItem("admin_id");
                localStorage.removeItem("admin_fullname");
                localStorage.removeItem("admin_email");

                localStorage.removeItem("last_screening_id");


                /*
                   Also remove patient session keys
                   in case an old session exists.
                */

                localStorage.removeItem("user_id");
                localStorage.removeItem("user_fullname");
                localStorage.removeItem("user_email");


                /* Redirect to common login */

                window.location.href =
                    "../../login.html";
            }
        );
    }


    /* ========================================================
       CHANGE PASSWORD
       ======================================================== */

    /*
       IMPORTANT:
       At the moment your backend has a patient password
       route only:

           /users/<user_id>/password

       Therefore we should NOT send the admin password
       request to the patient endpoint.

       We leave the form safely disabled until an
       admin password endpoint is intentionally added.
    */

    if (changePasswordForm) {

        changePasswordForm.addEventListener(
            "submit",
            function (event) {

                event.preventDefault();

                showPasswordMessage(
                    "Admin password change is not available yet.",
                    "error"
                );
            }
        );
    }


    /* ========================================================
       PASSWORD MESSAGE
       ======================================================== */

    function showPasswordMessage(
        message,
        type
    ) {

        if (!passwordMessage) {
            return;
        }

        passwordMessage.textContent =
            message;

        passwordMessage.className =
            `message ${type}`;
    }


    /* ========================================================
       DARK MODE
       ======================================================== */

    function loadTheme() {

        const savedTheme =
            localStorage.getItem("oralai_theme");


        if (savedTheme === "dark") {

            document.body.classList.add(
                "dark-mode"
            );

            if (darkModeToggle) {
                darkModeToggle.checked = true;
            }

        }
        else {

            document.body.classList.remove(
                "dark-mode"
            );

            if (darkModeToggle) {
                darkModeToggle.checked = false;
            }
        }
    }


    /* ========================================================
       DARK MODE TOGGLE
       ======================================================== */

    if (darkModeToggle) {

        darkModeToggle.addEventListener(
            "change",
            function () {

                if (darkModeToggle.checked) {

                    document.body.classList.add(
                        "dark-mode"
                    );

                    localStorage.setItem(
                        "oralai_theme",
                        "dark"
                    );

                }
                else {

                    document.body.classList.remove(
                        "dark-mode"
                    );

                    localStorage.setItem(
                        "oralai_theme",
                        "light"
                    );
                }
            }
        );
    }


    /* ========================================================
       INITIAL LOAD
       ======================================================== */

    loadAdminProfile();

    loadTheme();

});
