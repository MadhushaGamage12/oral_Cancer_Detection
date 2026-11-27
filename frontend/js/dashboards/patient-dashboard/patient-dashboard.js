const API_URL = "http://127.0.0.1:5000";


document.addEventListener("DOMContentLoaded", function () {

    // Get logged-in user's ID
    const userId = localStorage.getItem("user_id");


    // If no user is logged in,
    // send the user back to login page
    if (!userId) {

        window.location.href = "../../login.html";

        return;
    }


    // Load patient information
    loadPatientInfo(userId);


    // Load screening statistics
    loadScreeningStatistics(userId);


    // Setup top-right user menu
    setupUserMenu();


    // Setup logout
    setupLogout();

});



/* =========================================
   LOAD PATIENT INFORMATION
   ========================================= */

async function loadPatientInfo(userId) {

    try {

        const response = await fetch(
            `${API_URL}/users/${userId}`
        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            console.error(
                "Failed to load patient information"
            );

            return;
        }


        const user = data.user;


        // Save user information locally
        localStorage.setItem(
            "user_fullname",
            user.fullname
        );


        localStorage.setItem(
            "user_email",
            user.email
        );


        // Get first name
        const firstName = getFirstName(user.fullname);


        // Update top-right welcome text
        const userWelcome =
            document.getElementById("userWelcome");


        if (userWelcome) {

            userWelcome.textContent =
                `Welcome, ${firstName}`;

        }


        // Update dashboard heading
        const welcomeHeading =
            document.getElementById("welcomeHeading");


        if (welcomeHeading) {

            welcomeHeading.textContent =
                `👋 Welcome Back, ${firstName}!`;

        }

    }

    catch (error) {

        console.error(
            "Error loading patient information:",
            error
        );

    }

}



/* =========================================
   LOAD SCREENING STATISTICS
   ========================================= */

async function loadScreeningStatistics(userId) {

    try {

        const response = await fetch(
            `${API_URL}/screenings/${userId}`
        );


        const data = await response.json();


        if (!response.ok || !data.success) {

            console.error(
                "Failed to load screening history"
            );

            return;
        }


        const screenings = data.screenings || [];


        // Total number of screenings
        const totalScreenings =
            document.getElementById("totalScreenings");


        if (totalScreenings) {

            totalScreenings.textContent =
                screenings.length;

        }


        // If there are screenings,
        // show the latest result
        if (screenings.length > 0) {

            const latest = screenings[0];


            const lastResult =
                document.getElementById("lastResult");


            const riskStatus =
                document.getElementById("riskStatus");


            if (lastResult) {

                lastResult.textContent =
                    latest.prediction || "-";

            }


            if (riskStatus) {

                riskStatus.textContent =
                    latest.risk_status || "-";

            }

        }

    }

    catch (error) {

        console.error(
            "Error loading screening statistics:",
            error
        );

    }

}



/* =========================================
   USER DROPDOWN MENU
   ========================================= */

function setupUserMenu() {

    const button =
        document.getElementById("userMenuButton");


    const dropdown =
        document.getElementById("userDropdown");


    if (!button || !dropdown) {

        return;
    }


    // Open / close dropdown
    button.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            dropdown.classList.toggle("show");

        }
    );


    // Close dropdown when clicking elsewhere
    document.addEventListener(
        "click",
        function () {

            dropdown.classList.remove("show");

        }
    );


    // Prevent dropdown click from closing
    // before the selected link works
    dropdown.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

        }
    );

}



/* =========================================
   LOGOUT
   ========================================= */

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


            // Remove logged-in user data
            localStorage.removeItem("user_id");
            localStorage.removeItem("user_fullname");
            localStorage.removeItem("user_email");


            // Go back to login page
            window.location.href =
                "../../login.html";

        }
    );

}



/* =========================================
   GET FIRST NAME
   ========================================= */

function getFirstName(fullName) {

    if (!fullName) {

        return "Patient";

    }


    return fullName
        .trim()
        .split(" ")[0];

}
