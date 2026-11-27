/* =============================================================
   ORALAI - ADMIN SCREENING RECORDS
   JavaScript
============================================================= */


/* =============================================================
   API CONFIGURATION
============================================================= */

const API_BASE_URL =
    "http://127.0.0.1:5000";



/* =============================================================
   GLOBAL SCREENING DATA
============================================================= */

let allScreenings = [];



/* =============================================================
   LOAD SCREENING RECORDS
============================================================= */

async function loadScreenings() {


    const tableBody =
        document.getElementById(
            "screeningTableBody"
        );


    try {


        console.log(
            "Loading screening records..."
        );


        /* -----------------------------------------------------
           Request screening records from Flask
        ------------------------------------------------------ */

        const response =
            await fetch(
                `${API_BASE_URL}/admin/screenings`
            );


        console.log(
            "Screenings API status:",
            response.status
        );


        /* -----------------------------------------------------
           Check HTTP response
        ------------------------------------------------------ */

        if (!response.ok) {

            throw new Error(
                `Server returned HTTP ${response.status}`
            );

        }


        /* -----------------------------------------------------
           Convert to JSON
        ------------------------------------------------------ */

        const data =
            await response.json();


        console.log(
            "Screenings received:",
            data
        );


        /* -----------------------------------------------------
           Check success
        ------------------------------------------------------ */

        if (!data.success) {

            throw new Error(
                data.message ||
                "Unable to load screening records."
            );

        }


        /* -----------------------------------------------------
           Store records globally
        ------------------------------------------------------ */

        allScreenings =
            Array.isArray(data.screenings)
                ? data.screenings
                : [];


        /* -----------------------------------------------------
           Update summary
        ------------------------------------------------------ */

        updateSummary(
            allScreenings
        );


        /* -----------------------------------------------------
           Display table
        ------------------------------------------------------ */

        renderScreenings(
            allScreenings
        );


    }

    catch (error) {


        console.error(
            "Error loading screenings:",
            error
        );


        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="6"
                    class="error-cell"
                >

                    <i class="fa-solid fa-circle-exclamation"></i>

                    Failed to load screening records.

                    <br>

                    <small>
                        Please make sure the OralAI Flask backend is running.
                    </small>

                </td>

            </tr>

        `;


        /*
           Keep summary at zero if API fails
        */

        updateSummary([]);

    }

}



/* =============================================================
   UPDATE SUMMARY CARDS
============================================================= */

function updateSummary(
    screenings
) {


    /* ---------------------------------------------------------
       Total
    ---------------------------------------------------------- */

    const total =
        screenings.length;


    /* ---------------------------------------------------------
       Potential Positive
    ---------------------------------------------------------- */

    const positive =
        screenings.filter(
            screening =>
                isPositiveResult(
                    screening
                )
        ).length;


    /* ---------------------------------------------------------
       Negative
    ---------------------------------------------------------- */

    const negative =
        screenings.filter(
            screening =>
                isNegativeResult(
                    screening
                )
        ).length;


    /* ---------------------------------------------------------
       Today
    ---------------------------------------------------------- */

    const today =
        screenings.filter(
            screening =>
                isToday(
                    getScreeningDate(
                        screening
                    )
                )
        ).length;


    /* ---------------------------------------------------------
       Update HTML
    ---------------------------------------------------------- */

    setText(
        "totalScreenings",
        total
    );


    setText(
        "potentialPositive",
        positive
    );


    setText(
        "negativeResults",
        negative
    );


    setText(
        "todayScreenings",
        today
    );

}



/* =============================================================
   RENDER SCREENINGS
============================================================= */

function renderScreenings(
    screenings
) {


    const tableBody =
        document.getElementById(
            "screeningTableBody"
        );


    /* Clear existing rows */

    tableBody.innerHTML = "";


    /* ---------------------------------------------------------
       Empty state
    ---------------------------------------------------------- */

    if (
        !screenings ||
        screenings.length === 0
    ) {


        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="6"
                    class="empty-cell"
                >

                    <i class="fa-regular fa-folder-open"></i>

                    <br>

                    No screening records found.

                </td>

            </tr>

        `;


        return;

    }



    /* ---------------------------------------------------------
       Create rows
    ---------------------------------------------------------- */

    screenings.forEach(
        screening => {


            const row =
                document.createElement(
                    "tr"
                );


            /* -----------------------------------------------
               Screening ID
            ------------------------------------------------ */

            const screeningId =
                screening.id ??
                screening.screening_id ??
                "";


            const formattedScreeningId =
                formatScreeningId(
                    screeningId
                );


            /* -----------------------------------------------
               Patient
            ------------------------------------------------ */

            const patientName =
                screening.fullname ??
                screening.patient_name ??
                screening.user_name ??
                screening.name ??
                `Patient ${screening.user_id ?? ""}`;


            const userId =
                screening.user_id ??
                screening.patient_id ??
                "";


            /* -----------------------------------------------
               Date
            ------------------------------------------------ */

            const date =
                getScreeningDate(
                    screening
                );


            const formattedDate =
                formatDate(
                    date
                );


            /* -----------------------------------------------
               Result
            ------------------------------------------------ */

            const resultInfo =
                getResultInfo(
                    screening
                );


            /* -----------------------------------------------
               Confidence
            ------------------------------------------------ */

            const confidence =
                getConfidence(
                    screening
                );


            /* -----------------------------------------------
               Detail URL
            ------------------------------------------------ */

            const detailUrl =
                `admin-screening-details.html?id=${screeningId}`;


            /* -----------------------------------------------
               Build row
            ------------------------------------------------ */

            row.innerHTML = `

                <td>

                    <span class="screening-id">

                        ${escapeHTML(
                            formattedScreeningId
                        )}

                    </span>

                </td>


                <td>

                    <span class="patient-name">

                        ${escapeHTML(
                            patientName
                        )}

                    </span>

                    ${
                        userId
                            ? `
                                <span class="patient-id">

                                    User ID:
                                    ${escapeHTML(
                                        String(userId)
                                    )}

                                </span>
                              `
                            : ""
                    }

                </td>


                <td>

                    <span class="screening-date">

                        ${escapeHTML(
                            formattedDate
                        )}

                    </span>

                </td>


                <td>

                    <span class="status ${resultInfo.className}">

                        ${escapeHTML(
                            resultInfo.label
                        )}

                    </span>

                </td>


                <td>

                    <span class="confidence-value">

                        ${escapeHTML(
                            confidence
                        )}

                    </span>

                </td>


                <td>

                    <a
                        href="${detailUrl}"
                        class="table-action"
                    >

                        View Result

                        <i class="fa-solid fa-arrow-right"></i>

                    </a>

                </td>

            `;


            tableBody.appendChild(
                row
            );

        }
    );

}



/* =============================================================
   GET RESULT INFORMATION
============================================================= */

function getResultInfo(
    screening
) {


    /*
       Backend can return prediction,
       risk_status, result, etc.
    */

    const prediction =
        String(
            screening.prediction ??
            screening.result ??
            screening.risk_status ??
            ""
        )
            .trim()
            .toLowerCase();


    /* ---------------------------------------------------------
       Positive / Cancer
    ---------------------------------------------------------- */

    if (

        prediction.includes("cancer") ||

        prediction.includes("positive") ||

        prediction.includes("suspicious") ||

        prediction.includes("potential")

    ) {

        return {

            label:
                "Potential Positive",

            className:
                "positive"

        };

    }


    /* ---------------------------------------------------------
       Negative / Not Cancer
    ---------------------------------------------------------- */

    if (

        prediction.includes("not cancer") ||

        prediction.includes("negative") ||

        prediction.includes("normal")

    ) {

        return {

            label:
                "Negative",

            className:
                "negative"

        };

    }


    /* ---------------------------------------------------------
       Pending
    ---------------------------------------------------------- */

    return {

        label:
            "Pending",

        className:
            "pending"

    };

}



/* =============================================================
   CHECK POSITIVE
============================================================= */

function isPositiveResult(
    screening
) {


    const result =
        getResultInfo(
            screening
        );


    return (
        result.className ===
        "positive"
    );

}



/* =============================================================
   CHECK NEGATIVE
============================================================= */

function isNegativeResult(
    screening
) {


    const result =
        getResultInfo(
            screening
        );


    return (
        result.className ===
        "negative"
    );

}



/* =============================================================
   GET CONFIDENCE
============================================================= */

function getConfidence(
    screening
) {


    let confidence =
        screening.confidence;


    if (
        confidence === null ||
        confidence === undefined ||
        confidence === ""
    ) {

        return "-";

    }


    confidence =
        Number(
            confidence
        );


    if (
        Number.isNaN(
            confidence
        )
    ) {

        return String(
            screening.confidence
        );

    }


    /*
       Backend may return:
       0.945 OR 94.5
    */

    if (
        confidence <= 1
    ) {

        confidence =
            confidence * 100;

    }


    return (
        confidence.toFixed(1) +
        "%"
    );

}



/* =============================================================
   GET SCREENING DATE
============================================================= */

function getScreeningDate(
    screening
) {


    return (
        screening.created_at ??
        screening.screening_date ??
        screening.date ??
        null
    );

}



/* =============================================================
   FORMAT SCREENING ID
============================================================= */

function formatScreeningId(
    id
) {


    if (
        id === null ||
        id === undefined ||
        id === ""
    ) {

        return "-";

    }


    return (
        "#SCR-" +
        String(id).padStart(
            4,
            "0"
        )
    );

}



/* =============================================================
   FORMAT DATE
============================================================= */

function formatDate(
    dateString
) {


    if (
        !dateString
    ) {

        return "-";

    }


    const date =
        new Date(
            dateString
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return String(
            dateString
        );

    }


    return date.toLocaleString(
        "en-GB",
        {

            day:
                "2-digit",

            month:
                "short",

            year:
                "numeric",

            hour:
                "2-digit",

            minute:
                "2-digit"

        }
    );

}



/* =============================================================
   CHECK TODAY
============================================================= */

function isToday(
    dateString
) {


    if (
        !dateString
    ) {

        return false;

    }


    const date =
        new Date(
            dateString
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return false;

    }


    const today =
        new Date();


    return (

        date.getFullYear() ===
        today.getFullYear()

        &&

        date.getMonth() ===
        today.getMonth()

        &&

        date.getDate() ===
        today.getDate()

    );

}



/* =============================================================
   SEARCH + FILTER
============================================================= */

function setupFilters() {


    const searchInput =
        document.getElementById(
            "screeningSearch"
        );


    const resultFilter =
        document.getElementById(
            "resultFilter"
        );


    /* ---------------------------------------------------------
       Search
    ---------------------------------------------------------- */

    searchInput.addEventListener(
        "input",
        applyFilters
    );


    /* ---------------------------------------------------------
       Result filter
    ---------------------------------------------------------- */

    resultFilter.addEventListener(
        "change",
        applyFilters
    );

}



/* =============================================================
   APPLY FILTERS
============================================================= */

function applyFilters() {


    const searchValue =
        document.getElementById(
            "screeningSearch"
        )
            .value
            .toLowerCase()
            .trim();


    const selectedFilter =
        document.getElementById(
            "resultFilter"
        )
            .value;


    const filtered =
        allScreenings.filter(
            screening => {


                /* -------------------------------------------
                   Search text
                -------------------------------------------- */

                const screeningId =
                    String(
                        screening.id ??
                        screening.screening_id ??
                        ""
                    )
                        .toLowerCase();


                const patientName =
                    String(
                        screening.fullname ??
                        screening.patient_name ??
                        screening.user_name ??
                        screening.name ??
                        ""
                    )
                        .toLowerCase();


                const userId =
                    String(
                        screening.user_id ??
                        screening.patient_id ??
                        ""
                    )
                        .toLowerCase();


                const matchesSearch =

                    screeningId.includes(
                        searchValue
                    )

                    ||

                    patientName.includes(
                        searchValue
                    )

                    ||

                    userId.includes(
                        searchValue
                    );



                /* -------------------------------------------
                   Result filter
                -------------------------------------------- */

                const result =
                    getResultInfo(
                        screening
                    );


                let matchesFilter =
                    true;


                if (
                    selectedFilter ===
                    "positive"
                ) {

                    matchesFilter =
                        result.className ===
                        "positive";

                }


                if (
                    selectedFilter ===
                    "negative"
                ) {

                    matchesFilter =
                        result.className ===
                        "negative";

                }


                return (
                    matchesSearch &&
                    matchesFilter
                );

            }
        );


    renderScreenings(
        filtered
    );

}



/* =============================================================
   ADMIN PROFILE
============================================================= */

function setupAdminProfile() {


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
       Get admin localStorage information
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
       Load admin profile photo
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
                       Update fullname
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
                       Load profile image
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
       CLOSE DROPDOWN
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
       LOGOUT
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


        /* Remove admin information */

        localStorage.removeItem(
            "admin_id"
        );

        localStorage.removeItem(
            "admin_fullname"
        );

        localStorage.removeItem(
            "admin_email"
        );


        /* Remove patient information */

        localStorage.removeItem(
            "user_id"
        );

        localStorage.removeItem(
            "user_fullname"
        );

        localStorage.removeItem(
            "user_email"
        );


        /* Remove screening session */

        localStorage.removeItem(
            "last_screening_id"
        );


        /* Go to common login */

        window.location.href =
            "../../login.html";

    }



    /* ---------------------------------------------------------
       Dropdown logout
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
       Sidebar logout
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
   SET TEXT HELPER
============================================================= */

function setText(
    elementId,
    value
) {


    const element =
        document.getElementById(
            elementId
        );


    if (
        element
    ) {

        element.textContent =
            value;

    }

}



/* =============================================================
   ESCAPE HTML
============================================================= */

function escapeHTML(
    value
) {


    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value === null ||
        value === undefined
            ? ""
            : String(value);


    return div.innerHTML;

}



/* =============================================================
   START PAGE
============================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {


        console.log(
            "Admin Screening Records page loaded."
        );


        /* Load real DB records */

        loadScreenings();


        /* Search + filter */

        setupFilters();


        /* Admin profile */

        setupAdminProfile();

    }
);
