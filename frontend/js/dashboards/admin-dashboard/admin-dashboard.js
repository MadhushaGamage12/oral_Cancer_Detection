/* ============================================================
   OralAI - Admin Dashboard
============================================================ */


/* ============================================================
   API CONFIGURATION
============================================================ */

const API_BASE_URL = "http://127.0.0.1:5000";


/* ============================================================
   CHART VARIABLES
============================================================ */

let screeningResultChart = null;
let registrationChart = null;
let screeningActivityChart = null;


/* ============================================================
   PAGE INITIALIZATION
============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    console.log("======================================");
    console.log("OralAI Admin Dashboard");
    console.log("======================================");


    /* --------------------------------------------------------
       LOAD DASHBOARD INFORMATION
    -------------------------------------------------------- */

    loadDashboardData();

    loadRecentUsers();

    loadRegistrationChart();

    updateLastUpdated();


    /* --------------------------------------------------------
       UI SETUP
    -------------------------------------------------------- */

    setupMobileMenu();

    setupLogout();

    setupAdminProfileDropdown();

});


/* ============================================================
   LOAD MAIN DASHBOARD DATA
============================================================ */

async function loadDashboardData() {

    try {

        console.log("Loading dashboard statistics...");


        const response = await fetch(
            `${API_BASE_URL}/admin/dashboard`
        );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data = await response.json();


        console.log(
            "Dashboard API response:",
            data
        );


        if (!data.success) {

            throw new Error(
                "Dashboard API returned success=false"
            );

        }


        /* ----------------------------------------------------
           UPDATE STATISTICS
        ---------------------------------------------------- */

        updateStatistics(
            data.statistics
        );


        /* ----------------------------------------------------
           CREATE SCREENING RESULT CHART
        ---------------------------------------------------- */

        createScreeningResultChart(
            data.statistics
        );


        console.log(
            "Recent screenings:",
            data.recent_screenings
        );


    } catch (error) {

        console.error(
            "Failed to load dashboard data:",
            error
        );


        showDashboardError();

    }

}


/* ============================================================
   UPDATE STATISTICS
============================================================ */

function updateStatistics(statistics) {

    if (!statistics) {

        return;

    }


    /* --------------------------------------------------------
       TOTAL USERS
    -------------------------------------------------------- */

    const totalUsers =
        document.getElementById("totalUsers");


    if (totalUsers) {

        totalUsers.textContent =
            statistics.total_users ?? 0;

    }


    /* --------------------------------------------------------
       TOTAL SCREENINGS
    -------------------------------------------------------- */

    const totalScreenings =
        document.getElementById("totalScreenings");


    if (totalScreenings) {

        totalScreenings.textContent =
            statistics.total_screenings ?? 0;

    }


    /* --------------------------------------------------------
       POTENTIAL POSITIVE
    -------------------------------------------------------- */

    const potentialPositive =
        document.getElementById("potentialPositive");


    if (potentialPositive) {

        potentialPositive.textContent =
            statistics.cancer_screenings ?? 0;

    }


    /* --------------------------------------------------------
       NEGATIVE RESULTS
    -------------------------------------------------------- */

    const negativeResults =
        document.getElementById("negativeResults");


    if (negativeResults) {

        negativeResults.textContent =
            statistics.not_cancer_screenings ?? 0;

    }


    console.log(
        "Pending screenings:",
        statistics.pending_screenings ?? 0
    );

}


/* ============================================================
   SCREENING RESULT CHART
============================================================ */

function createScreeningResultChart(statistics) {

    const canvas =
        document.getElementById(
            "screeningResultChart"
        );


    if (!canvas || !statistics) {

        return;

    }


    const positive =
        Number(
            statistics.cancer_screenings ?? 0
        );


    const negative =
        Number(
            statistics.not_cancer_screenings ?? 0
        );


    const total =
        Number(
            statistics.total_screenings ?? 0
        );


    /* --------------------------------------------------------
       UPDATE CENTER TOTAL
    -------------------------------------------------------- */

    const chartTotal =
        document.getElementById(
            "chartTotal"
        );


    if (chartTotal) {

        chartTotal.textContent =
            total;

    }


    /* --------------------------------------------------------
       CALCULATE PERCENTAGES
    -------------------------------------------------------- */

    let positivePercentage = 0;
    let negativePercentage = 0;


    if (total > 0) {

        positivePercentage =
            Math.round(
                (positive / total) * 100
            );


        negativePercentage =
            Math.round(
                (negative / total) * 100
            );

    }


    /* --------------------------------------------------------
       UPDATE POSITIVE PERCENTAGE
    -------------------------------------------------------- */

    const positivePercentageElement =
        document.getElementById(
            "positivePercentage"
        );


    if (positivePercentageElement) {

        positivePercentageElement.textContent =
            `${positivePercentage}%`;

    }


    /* --------------------------------------------------------
       UPDATE NEGATIVE PERCENTAGE
    -------------------------------------------------------- */

    const negativePercentageElement =
        document.getElementById(
            "negativePercentage"
        );


    if (negativePercentageElement) {

        negativePercentageElement.textContent =
            `${negativePercentage}%`;

    }


    /* --------------------------------------------------------
       DESTROY OLD CHART
    -------------------------------------------------------- */

    if (screeningResultChart) {

        screeningResultChart.destroy();

    }


    /* --------------------------------------------------------
       CREATE DOUGHNUT CHART
    -------------------------------------------------------- */

    screeningResultChart =
        new Chart(
            canvas,
            {

                type: "doughnut",

                data: {

                    labels: [
                        "Potential Positive",
                        "Negative"
                    ],

                    datasets: [

                        {

                            data: [
                                positive,
                                negative
                            ],

                            borderWidth: 0

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    cutout: "68%",

                    plugins: {

                        legend: {

                            display: false

                        },

                        tooltip: {

                            callbacks: {

                                label: function (context) {

                                    const value =
                                        Number(
                                            context.raw ?? 0
                                        );


                                    let percentage = 0;


                                    if (total > 0) {

                                        percentage =
                                            (
                                                value /
                                                total
                                            ) * 100;

                                    }


                                    return (
                                        `${context.label}: ` +
                                        `${value} ` +
                                        `(${percentage.toFixed(1)}%)`
                                    );

                                }

                            }

                        }

                    }

                }

            }
        );

}


/* ============================================================
   LOAD RECENT USERS
============================================================ */

async function loadRecentUsers() {

    const tableBody =
        document.getElementById(
            "recentUsersTable"
        );


    if (!tableBody) {

        return;

    }


    try {

        console.log(
            "Loading recent users..."
        );


        const response =
            await fetch(
                `${API_BASE_URL}/admin/users`
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Users API response:",
            data
        );


        if (!data.success) {

            throw new Error(
                "Users API returned success=false"
            );

        }


        /* ----------------------------------------------------
           UPDATE TOTAL USER COUNT
        ---------------------------------------------------- */

        const totalUsers =
            document.getElementById(
                "totalUsers"
            );


        if (totalUsers) {

            totalUsers.textContent =
                data.count ?? 0;

        }


        /* ----------------------------------------------------
           CLEAR TABLE
        ---------------------------------------------------- */

        tableBody.innerHTML = "";


        /* ----------------------------------------------------
           GET FIRST 5 USERS
        ---------------------------------------------------- */

        const recentUsers =
            Array.isArray(data.users)
                ? data.users.slice(0, 5)
                : [];


        /* ----------------------------------------------------
           NO USERS
        ---------------------------------------------------- */

        if (recentUsers.length === 0) {

            tableBody.innerHTML = `

                <tr>

                    <td colspan="5">

                        <div class="loading-state">

                            No registered users found.

                        </div>

                    </td>

                </tr>

            `;

            return;

        }


        /* ----------------------------------------------------
           CREATE USER ROWS
        ---------------------------------------------------- */

        recentUsers.forEach(function (user) {

            const row =
                document.createElement("tr");


            /* ------------------------------------------------
               DATE
            ------------------------------------------------ */

            const date =
                new Date(
                    user.created_at
                );


            let registeredDate = "--";
            let registeredTime = "--";


            if (!isNaN(date.getTime())) {

                registeredDate =
                    date.toLocaleDateString(
                        "en-GB",
                        {
                            day: "2-digit",
                            month: "short",
                            year: "numeric"
                        }
                    );


                registeredTime =
                    date.toLocaleTimeString(
                        "en-US",
                        {
                            hour: "2-digit",
                            minute: "2-digit"
                        }
                    );

            }


            /* ------------------------------------------------
               CREATE ROW HTML
            ------------------------------------------------ */

            row.innerHTML = `

                <td>

                    <div class="user-table-info">

                        <div class="user-table-avatar">

                            ${getInitial(
                                user.fullname
                            )}

                        </div>

                        <strong>
                            ${escapeHTML(
                                user.fullname
                            )}
                        </strong>

                    </div>

                </td>


                <td>

                    ${escapeHTML(
                        user.email
                    )}

                </td>


                <td>

                    ${registeredDate}

                </td>


                <td>

                    ${registeredTime}

                </td>


                <td>

                    <span class="status negative">

                        Active

                    </span>

                </td>

            `;


            tableBody.appendChild(row);

        });


    } catch (error) {

        console.error(
            "Failed to load recent users:",
            error
        );


        tableBody.innerHTML = `

            <tr>

                <td colspan="5">

                    <div
                        class="loading-state"
                        style="color: #dc2626;"
                    >

                        Failed to load registered users.

                    </div>

                </td>

            </tr>

        `;

    }

}


/* ============================================================
   LOAD ANALYTICS
============================================================ */

async function loadRegistrationChart() {

    try {

        console.log(
            "Loading admin analytics..."
        );


        const response =
            await fetch(
                `${API_BASE_URL}/admin/analytics`
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Analytics API:",
            data
        );


        if (!data.success) {

            console.warn(
                "Analytics API returned success=false."
            );

            return;

        }


        /* ----------------------------------------------------
           REGISTRATION CHART
        ---------------------------------------------------- */

        createRegistrationChart(
            data.registrations
        );


        /* ----------------------------------------------------
           SCREENING ACTIVITY CHART
        ---------------------------------------------------- */

        createScreeningActivityChart(
            data.screenings
        );


    } catch (error) {

        console.warn(
            "Analytics endpoint is not available:",
            error
        );

    }

}


/* ============================================================
   REGISTRATION BAR CHART
============================================================ */

function createRegistrationChart(registrations) {

    const canvas =
        document.getElementById(
            "registrationChart"
        );


    if (!canvas || !Array.isArray(registrations)) {

        return;

    }


    const labels =
        registrations.map(
            item =>
                formatChartDate(
                    item.date
                )
        );


    const values =
        registrations.map(
            item =>
                Number(
                    item.count ?? 0
                )
        );


    /* --------------------------------------------------------
       DESTROY OLD CHART
    -------------------------------------------------------- */

    if (registrationChart) {

        registrationChart.destroy();

    }


    /* --------------------------------------------------------
       CREATE BAR CHART
    -------------------------------------------------------- */

    registrationChart =
        new Chart(
            canvas,
            {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "New Registrations",

                            data: values,

                            borderWidth: 1

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            display: false

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                precision: 0

                            }

                        }

                    }

                }

            }
        );

}


/* ============================================================
   SCREENING ACTIVITY CHART
============================================================ */

function createScreeningActivityChart(screenings) {

    const canvas =
        document.getElementById(
            "screeningActivityChart"
        );


    if (!canvas || !Array.isArray(screenings)) {

        return;

    }


    const labels =
        screenings.map(
            item =>
                formatChartDate(
                    item.date
                )
        );


    const values =
        screenings.map(
            item =>
                Number(
                    item.count ?? 0
                )
        );


    /* --------------------------------------------------------
       DESTROY OLD CHART
    -------------------------------------------------------- */

    if (screeningActivityChart) {

        screeningActivityChart.destroy();

    }


    /* --------------------------------------------------------
       CREATE BAR CHART
    -------------------------------------------------------- */

    screeningActivityChart =
        new Chart(
            canvas,
            {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Screenings",

                            data: values,

                            borderWidth: 1

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            display: false

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                precision: 0

                            }

                        }

                    }

                }

            }
        );

}


/* ============================================================
   FORMAT CHART DATE
============================================================ */

function formatChartDate(dateString) {

    if (!dateString) {

        return "--";

    }


    const date =
        new Date(
            dateString
        );


    if (isNaN(date.getTime())) {

        return dateString;

    }


    return date.toLocaleDateString(
        "en-GB",
        {
            day: "2-digit",
            month: "short"
        }
    );

}


/* ============================================================
   UPDATE LAST UPDATED
============================================================ */

function updateLastUpdated() {

    const element =
        document.getElementById(
            "lastUpdated"
        );


    if (!element) {

        return;

    }


    const now =
        new Date();


    element.textContent =
        now.toLocaleString(
            "en-GB",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            }
        );

}


/* ============================================================
   MOBILE MENU
============================================================ */

function setupMobileMenu() {

    const menuButton =
        document.getElementById(
            "mobileMenuBtn"
        );


    const sidebar =
        document.querySelector(
            ".sidebar"
        );


    if (!menuButton || !sidebar) {

        return;

    }


    menuButton.addEventListener(
        "click",
        function () {

            sidebar.classList.toggle(
                "mobile-open"
            );

        }
    );

}


/* ============================================================
   ADMIN PROFILE DROPDOWN
============================================================ */

function setupAdminProfileDropdown() {

    const profileButton =
        document.getElementById(
            "adminProfileBtn"
        );


    const dropdown =
        document.getElementById(
            "adminProfileDropdown"
        );


    if (!profileButton || !dropdown) {

        return;

    }


    /* --------------------------------------------------------
       OPEN / CLOSE DROPDOWN
    -------------------------------------------------------- */

    profileButton.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();


            const isOpen =
                dropdown.classList.contains(
                    "show"
                );


            if (isOpen) {

                closeProfileDropdown();

            } else {

                dropdown.classList.add(
                    "show"
                );


                profileButton.classList.add(
                    "active"
                );


                profileButton.setAttribute(
                    "aria-expanded",
                    "true"
                );

            }

        }
    );


    /* --------------------------------------------------------
       CLOSE WHEN CLICKING OUTSIDE
    -------------------------------------------------------- */

    document.addEventListener(
        "click",
        function (event) {

            if (
                !event.target.closest(
                    ".admin-profile-wrapper"
                )
            ) {

                closeProfileDropdown();

            }

        }
    );


    /* --------------------------------------------------------
       MY PROFILE
       
       IMPORTANT:
       Do NOT show an alert here.
       The HTML href points to admin-profile.html.
    -------------------------------------------------------- */

    const myProfileBtn =
        document.getElementById(
            "myProfileBtn"
        );


    if (myProfileBtn) {

        myProfileBtn.addEventListener(
            "click",
            function () {

                closeProfileDropdown();

                /* Let the HTML href navigate normally. */

            }
        );

    }


    /* --------------------------------------------------------
       PROFILE SETTINGS
       
       IMPORTANT:
       Do NOT preventDefault().
       The HTML href points to admin-settings.html.
    -------------------------------------------------------- */

    const profileSettingsBtn =
        document.getElementById(
            "profileSettingsBtn"
        );


    if (profileSettingsBtn) {

        profileSettingsBtn.addEventListener(
            "click",
            function () {

                closeProfileDropdown();

                /* Let the HTML href navigate normally. */

            }
        );

    }


    /* --------------------------------------------------------
       PROFILE LOGOUT
    -------------------------------------------------------- */

    const profileLogoutBtn =
        document.getElementById(
            "profileLogoutBtn"
        );


    if (profileLogoutBtn) {

        profileLogoutBtn.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                logoutAdmin();

            }
        );

    }

}


/* ============================================================
   CLOSE PROFILE DROPDOWN
============================================================ */

function closeProfileDropdown() {

    const profileButton =
        document.getElementById(
            "adminProfileBtn"
        );


    const dropdown =
        document.getElementById(
            "adminProfileDropdown"
        );


    if (dropdown) {

        dropdown.classList.remove(
            "show"
        );

    }


    if (profileButton) {

        profileButton.classList.remove(
            "active"
        );


        profileButton.setAttribute(
            "aria-expanded",
            "false"
        );

    }

}


/* ============================================================
   LOGOUT
============================================================ */

function logoutAdmin() {

    const confirmed =
        confirm(
            "Are you sure you want to logout?"
        );


    if (!confirmed) {

        return;

    }


    /* --------------------------------------------------------
       CLEAR LOGIN DATA
    -------------------------------------------------------- */

    localStorage.removeItem(
        "user_id"
    );


    localStorage.removeItem(
        "user"
    );


    localStorage.removeItem(
        "fullname"
    );


    localStorage.removeItem(
        "email"
    );


    localStorage.removeItem(
        "last_screening_id"
    );


    /* --------------------------------------------------------
       REDIRECT TO LOGIN
    -------------------------------------------------------- */

    window.location.href =
        "../../login.html";

}


/* ============================================================
   SIDEBAR LOGOUT
============================================================ */

function setupLogout() {

    const logoutButton =
        document.getElementById(
            "logoutBtn"
        );


    if (!logoutButton) {

        return;

    }


    logoutButton.addEventListener(
        "click",
        function () {

            logoutAdmin();

        }
    );

}


/* ============================================================
   GET USER INITIAL
============================================================ */

function getInitial(name) {

    if (!name) {

        return "U";

    }


    return name
        .trim()
        .charAt(0)
        .toUpperCase();

}


/* ============================================================
   ESCAPE HTML
============================================================ */

function escapeHTML(value) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value ?? "";


    return div.innerHTML;

}


/* ============================================================
   SHOW DASHBOARD ERROR
============================================================ */

function showDashboardError() {

    const elements = [

        "totalUsers",

        "totalScreenings",

        "potentialPositive",

        "negativeResults"

    ];


    elements.forEach(
        function (id) {

            const element =
                document.getElementById(
                    id
                );


            if (element) {

                element.textContent =
                    "—";

            }

        }
    );

}
