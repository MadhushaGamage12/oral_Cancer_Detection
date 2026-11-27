const API_BASE_URL = "http://127.0.0.1:5000"; /* API CONFIGURATION*/

/* LOAD USERS */

async function loadUsers() {
    /* Get HTML elements */
    const tableBody = document.getElementById( "usersTableBody" );
    const totalUsers = document.getElementById("totalUsers" );
    try {
        console.log( "Loading users from backend..." );

        /*  Call Flask API */
        const response =  await fetch( `${API_BASE_URL}/admin/users` );
        /* Check HTTP response */

        if (!response.ok) {
            throw new Error( `Server returned HTTP ${response.status}` );
        }

        /*  Convert response to JSON*/
        const data =
            await response.json();
        console.log(
            "Users received from backend:",
            data
        );
        /*  Check API success */

        if (!data.success) {
            throw new Error( "Backend returned success=false");
        }

        /*  Update total users */
        totalUsers.textContent = data.count;

        /* Remove loading message */
        tableBody.innerHTML = "";

        /*  Check users */
        if ( !data.users || data.users.length === 0 ) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="empty-cell">
                        No registered users found.
                    </td>
                </tr>
            `;
            return;
        }

        /*  Create table rows */

        data.users.forEach(
            user => {

                /* Create row */
                const row = document.createElement("tr");
                /* Format user ID */
                const formattedUserId =  `#USR${String(user.id).padStart(3, "0")}`;
                /* Format date */
                const formattedDate = formatDate( user.created_at);
                /* Create row HTML */
                row.innerHTML = `
                    <td> ${formattedUserId} </td>
                    <td>${escapeHTML(user.fullname)} </td>
                    <td> ${escapeHTML(user.email)} </td>
                    <td> ${formattedDate} </td>
                    <td> ${user.screening_count} </td>
                    <td> <span class="status negative"> Active </span> </td>
                    <td> <a href="admin-user-details.html?id=${user.id}"class="table-action"> View </a> </td>
                `;

                /* Add row */
                tableBody.appendChild( row );
            }
        );

        /* Enable search */
        setupSearch();
    }
    catch (error) {
        console.error(  "Failed to load users:", error );
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="error-cell">
                    Failed to load registered users.
                    <br><br>
                    <small>
                        Please make sure the OralAI Flask backend is running.
                    </small>
                </td>
            </tr>
        `;
    }
}

/* FORMAT DATE */
function formatDate(dateString) {
    const date = new Date(dateString);
    if ( isNaN( date.getTime() )) {
        return dateString;
    }
    return date.toLocaleString("en-GB",{
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}

/* ESCAPE HTML */

function escapeHTML( value) {
    const div = document.createElement("div" );
    div.textContent = value ?? "";
    return div.innerHTML;
}

/* SEARCH USERS */
function setupSearch() {
    const searchInput = document.getElementById("userSearch" );
    const tableBody = document.getElementById("usersTableBody");
    /*  Prevent adding multiple input listeners */

    if (  searchInput.dataset.searchReady === "true") {
        return;
    }
    searchInput.dataset.searchReady = "true";
    searchInput.addEventListener("input",
        function () {
            const searchValue = this.value .toLowerCase() .trim();
            const rows = tableBody.querySelectorAll( "tr" );
            rows.forEach(
                row => {
                    const rowText = row.textContent .toLowerCase();
                    if ( rowText.includes(searchValue )) {
                        row.style.display = "";
                    }
                    else {
                        row.style.display = "none";
                    }
                }
            );
        }
   );
}

/* ADMIN PROFILE MENU */
function setupAdminProfile() {
    /* Get elements */
    const profileButton = document.getElementById( "adminProfileBtn"  );
    const profileDropdown = document.getElementById( "adminProfileDropdown" );
    const logoutButton = document.getElementById( "adminLogoutBtn" );
    const sidebarLogoutButton = document.getElementById( "sidebarLogoutBtn");
    const avatarImage = document.getElementById("adminAvatarImage" );
    const avatarInitial = document.getElementById( "adminAvatarInitial");
    const sidebarAvatar = document.getElementById(  "sidebarAdminAvatar");
    /*  Get admin information */
    const adminId = localStorage.getItem( "admin_id"  );
    const adminName =localStorage.getItem( "admin_fullname") || "Administrator";
    /* Set initial */

    const initial =
        adminName
            .trim()
            .charAt(0)
            .toUpperCase() || "A";
    if (avatarInitial) {
        avatarInitial.textContent = initial;
    }

    if (sidebarAvatar) {
        sidebarAvatar.textContent =  initial;
    }

    /* Load admin profile photo */
    if (adminId) {
        fetch( `${API_BASE_URL}/admin/profile/${adminId}`)
        .then( response => response.json()        )
        .then(data => {
                if (data.success && data.admin ) {
                    /* Update name */
                    if ( data.admin.fullname
                    ) {
                        localStorage.setItem(
                            "admin_fullname",
                            data.admin.fullname
                        );
                    }
                    /* Update initial */
                    const adminInitial =
                        (
                            data.admin.fullname ||
                            "Administrator"
                        )
                            .trim()
                            .charAt(0)
                            .toUpperCase();
                    if (avatarInitial) {
                        avatarInitial.textContent = adminInitial;
                    }
                    if (sidebarAvatar) {
                        sidebarAvatar.textContent = adminInitial;
                    }
                    /* Profile photo */
                    if ( data.admin.profile_photo_url ) {
                        avatarImage.src =
                            `${API_BASE_URL}${data.admin.profile_photo_url}?t=${Date.now()}`;
                        avatarImage.onload =
                            function () {
                                avatarImage.style.display = "block";
                                if (avatarInitial) {
                                    avatarInitial.style.display = "none";
                                }
                            };
                        avatarImage.onerror =
                            function () {
                                avatarImage.style.display = "none";
                                if (avatarInitial) {
                                    avatarInitial.style.display = "flex";
                                }
                            };
                    }
                }
            }
        )
        .catch(
            error => {
                console.log(
                    "Admin profile could not be loaded:", error
                );
            }
        );
    }

    /* OPEN / CLOSE PROFILE DROPDOWN */
    if ( profileButton && profileDropdown
    ) {
        profileButton.addEventListener(
            "click",
            function (event) {
                event.stopPropagation();
                const isOpen = profileDropdown.classList.toggle("show" );
                profileButton.setAttribute( "aria-expanded",
                    isOpen
                        ? "true"
                        : "false"
                );
            }
        );
    }

    /* CLOSE DROPDOWN OUTSIDE */

    document.addEventListener( "click",
        function (event) {
            if (
                !event.target.closest( ".admin-profile-wrapper")
            ) {
                if (profileDropdown) {
                    profileDropdown.classList.remove(  "show" );
                }

                if (profileButton) {
                    profileButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );
                }
            }
        }
    );

    /* LOGOUT FUNCTION */
    function logoutAdmin() {
        const confirmLogout =
            confirm("Are you sure you want to logout?");
        if (!confirmLogout) {
             return;
        }

        /* Remove admin session */
        localStorage.removeItem( "admin_id" );
        localStorage.removeItem("admin_fullname" );
        localStorage.removeItem( "admin_email" );
        /* Remove patient session */
        localStorage.removeItem( "user_id" );
        localStorage.removeItem( "user_fullname");
        localStorage.removeItem( "user_email");
        localStorage.removeItem("last_screening_id");
        /* Redirect to common login */
        window.location.href = "../../login.html";
    }

    /* TOP DROPDOWN LOGOUT */

    if (logoutButton) {
        logoutButton.addEventListener(
            "click",
            function (event) {
                event.preventDefault();
                logoutAdmin();
            }
        );
    }

    /* SIDEBAR LOGOUT */

    if (sidebarLogoutButton) {
        sidebarLogoutButton.addEventListener("click",
            function () {
                logoutAdmin();
            }
        );
    }
}

/*  MOBILE MENU */

function setupMobileMenu() {
    const mobileMenuButton =
        document.getElementById("mobileMenuBtn"  );
    const sidebar =
        document.querySelector( ".sidebar");
    if (!mobileMenuButton ||!sidebar
    ) {
        return;
    }

    mobileMenuButton.addEventListener(
        "click",
        function () {
            sidebar.classList.toggle( "open"
            );
        }
    );
}

/* START PAGE */
document.addEventListener(
    "DOMContentLoaded",
    function () {
        console.log( "Admin User Management page loaded.");
        /* Load real users */
        loadUsers();
        /* Setup admin profile */
        setupAdminProfile();
        /* Setup mobile menu */
        setupMobileMenu();
    }
)
