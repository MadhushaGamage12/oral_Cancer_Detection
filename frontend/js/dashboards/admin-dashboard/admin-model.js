/* =============================================================
   ORALAI - ADMIN MODEL INFORMATION
   JavaScript
============================================================= */


/* =============================================================
   API CONFIGURATION
============================================================= */

const API_BASE_URL =
    "http://127.0.0.1:5000";



/* =============================================================
   ADMIN PROFILE
============================================================= */

function setupAdminProfile() {


    /* ---------------------------------------------------------
       Get elements
    ---------------------------------------------------------- */

    const profileButton =
        document.getElementById(
            "adminProfileBtn"
        );


    const profileDropdown =
        document.getElementById(
            "adminProfileDropdown"
        );


    const logoutButton =
        document.getElementById(
            "adminLogoutBtn"
        );


    const sidebarLogoutButton =
        document.getElementById(
            "sidebarLogoutBtn"
        );


    const avatarImage =
        document.getElementById(
            "adminAvatarImage"
        );


    const avatarInitial =
        document.getElementById(
            "adminAvatarInitial"
        );


    const sidebarAvatar =
        document.getElementById(
            "sidebarAdminAvatar"
        );


    /* ---------------------------------------------------------
       Get admin information from localStorage
    ---------------------------------------------------------- */

    const adminId =
        localStorage.getItem(
            "admin_id"
        );


    const adminName =
        localStorage.getItem(
            "admin_fullname"
        ) ||
        "Administrator";


    /* ---------------------------------------------------------
       Set initial
    ---------------------------------------------------------- */

    const initial =
        adminName
            .trim()
            .charAt(0)
            .toUpperCase() ||
        "A";


    if (
        avatarInitial
    ) {

        avatarInitial.textContent =
            initial;

    }


    if (
        sidebarAvatar
    ) {

        sidebarAvatar.textContent =
            initial;

    }



    /* ---------------------------------------------------------
       Load admin profile from backend
    ---------------------------------------------------------- */

    if (
        adminId
    ) {


        fetch(
            `${API_BASE_URL}/admin/profile/${adminId}`
        )

        .then(
            response =>
                response.json()
        )

        .then(
            data => {


                if (
                    data.success &&
                    data.admin
                ) {


                    /* ---------------------------------------
                       Update admin name
                    ---------------------------------------- */

                    if (
                        data.admin.fullname
                    ) {

                        localStorage.setItem(
                            "admin_fullname",
                            data.admin.fullname
                        );

                    }


                    /* ---------------------------------------
                       Update initial
                    ---------------------------------------- */

                    const updatedName =
                        data.admin.fullname ||
                        "Administrator";


                    const updatedInitial =
                        updatedName
                            .trim()
                            .charAt(0)
                            .toUpperCase() ||
                        "A";


                    if (
                        avatarInitial
                    ) {

                        avatarInitial.textContent =
                            updatedInitial;

                    }


                    if (
                        sidebarAvatar
                    ) {

                        sidebarAvatar.textContent =
                            updatedInitial;

                    }



                    /* ---------------------------------------
                       Profile photo
                    ---------------------------------------- */

                    if (
                        data.admin.profile_photo_url
                    ) {


                        avatarImage.src =
                            `${API_BASE_URL}${data.admin.profile_photo_url}?t=${Date.now()}`;


                        avatarImage.onload =
                            function () {


                                avatarImage.style.display =
                                    "block";


                                if (
                                    avatarInitial
                                ) {

                                    avatarInitial.style.display =
                                        "none";

                                }

                            };


                        avatarImage.onerror =
                            function () {


                                avatarImage.style.display =
                                    "none";


                                if (
                                    avatarInitial
                                ) {

                                    avatarInitial.style.display =
                                        "flex";

                                }

                            };

                    }

                }

            }
        )

        .catch(
            error => {

                console.log(
                    "Admin profile could not be loaded:",
                    error
                );

            }
        );

    }



    /* ---------------------------------------------------------
       OPEN PROFILE DROPDOWN
    ---------------------------------------------------------- */

    if (
        profileButton &&
        profileDropdown
    ) {


        profileButton.addEventListener(
            "click",
            function (
                event
            ) {


                event.stopPropagation();


                const isOpen =
                    profileDropdown.classList.toggle(
                        "show"
                    );


                profileButton.setAttribute(
                    "aria-expanded",
                    isOpen
                        ? "true"
                        : "false"
                );

            }
        );

    }



    /* ---------------------------------------------------------
       CLOSE DROPDOWN WHEN CLICKING OUTSIDE
    ---------------------------------------------------------- */

    document.addEventListener(
        "click",
        function (
            event
        ) {


            if (
                !event.target.closest(
                    ".admin-profile-wrapper"
                )
            ) {


                if (
                    profileDropdown
                ) {

                    profileDropdown.classList.remove(
                        "show"
                    );

                }


                if (
                    profileButton
                ) {

                    profileButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }

        }
    );



    /* ---------------------------------------------------------
       LOGOUT FUNCTION
    ---------------------------------------------------------- */

    function logoutAdmin() {


        const confirmLogout =
            confirm(
                "Are you sure you want to logout?"
            );


        if (
            !confirmLogout
        ) {

            return;

        }


        /* Admin */

        localStorage.removeItem(
            "admin_id"
        );

        localStorage.removeItem(
            "admin_fullname"
        );

        localStorage.removeItem(
            "admin_email"
        );


        /* Patient */

        localStorage.removeItem(
            "user_id"
        );

        localStorage.removeItem(
            "user_fullname"
        );

        localStorage.removeItem(
            "user_email"
        );


        /* Screening */

        localStorage.removeItem(
            "last_screening_id"
        );


        /* Return to common login */

        window.location.href =
            "../../login.html";

    }



    /* ---------------------------------------------------------
       DROPDOWN LOGOUT
    ---------------------------------------------------------- */

    if (
        logoutButton
    ) {

        logoutButton.addEventListener(
            "click",
            function (
                event
            ) {

                event.preventDefault();

                logoutAdmin();

            }
        );

    }



    /* ---------------------------------------------------------
       SIDEBAR LOGOUT
    ---------------------------------------------------------- */

    if (
        sidebarLogoutButton
    ) {

        sidebarLogoutButton.addEventListener(
            "click",
            function () {

                logoutAdmin();

            }
        );

    }

}



/* =============================================================
   CHECK ADMIN LOGIN
============================================================= */

function checkAdminLogin() {


    const adminId =
        localStorage.getItem(
            "admin_id"
        );


    /*
       If admin_id does not exist,
       user should not stay on admin page.
    */

    if (
        !adminId
    ) {

        console.warn(
            "No admin session found."
        );


        window.location.href =
            "../../login.html";


        return false;

    }


    return true;

}



/* =============================================================
   INITIALIZE PAGE
============================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {


        console.log(
            "Admin Model Information page loaded."
        );


        /* Check admin session */

        if (
            !checkAdminLogin()
        ) {

            return;

        }


        /* Setup admin profile */

        setupAdminProfile();


    }
);
