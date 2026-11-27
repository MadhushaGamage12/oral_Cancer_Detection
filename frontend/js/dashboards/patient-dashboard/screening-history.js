document.addEventListener("DOMContentLoaded", function () {


    // =====================================================
    // API URL
    // =====================================================

    const API_URL =
        "http://127.0.0.1:5000";


    // =====================================================
    // GET LOGGED-IN USER
    // =====================================================

    const userId =
        localStorage.getItem("user_id");


    // =====================================================
    // GET HTML ELEMENTS
    // =====================================================

    const searchInput =
        document.getElementById("searchInput");


    const resultFilter =
        document.getElementById("resultFilter");


    const historyTable =
        document.getElementById("historyTable");


    const emptyMessage =
        document.getElementById("emptyMessage");


    // =====================================================
    // USER MENU ELEMENTS
    // =====================================================

    const userMenuButton =
        document.getElementById("userMenuButton");


    const userDropdown =
        document.getElementById("userDropdown");


    const userAvatarImage =
        document.getElementById("userAvatarImage");


    const userAvatarInitial =
        document.getElementById("userAvatarInitial");


    const logoutLink =
        document.getElementById("logoutLink");


    // =====================================================
    // CHECK USER LOGIN
    // =====================================================

    if (!userId) {

        alert(
            "User session not found. Please login again."
        );

        window.location.href =
            "../../login.html";

        return;
    }


    // =====================================================
    // SETUP USER PROFILE MENU
    // =====================================================

    setupUserMenu();


    // =====================================================
    // LOAD USER PROFILE
    // =====================================================

    loadUserProfile();


    // =====================================================
    // STORE ALL SCREENINGS
    // =====================================================

    let allScreenings = [];


    // =====================================================
    // FORMAT DATE AND TIME
    // =====================================================

    function formatDateTime(dateValue) {


        if (!dateValue) {

            return {
                date: "-",
                time: "-"
            };

        }


        let day;
        let month;
        let year;

        let hours;
        let minutes;
        let seconds;


        // =================================================
        // FLASK HTTP DATE FORMAT
        // =================================================

        if (
            dateValue.includes(",") &&
            dateValue.includes("GMT")
        ) {


            const parts =
                dateValue
                    .replace(" GMT", "")
                    .split(" ");


            day =
                parts[1];


            month =
                parts[2];


            year =
                parts[3];


            const timeParts =
                parts[4].split(":");


            hours =
                parseInt(
                    timeParts[0]
                );


            minutes =
                timeParts[1];


            seconds =
                timeParts[2];

        }


        // =================================================
        // MYSQL DATETIME FORMAT
        // =================================================

        else {


            const dateParts =
                dateValue.split(" ");


            const date =
                dateParts[0];


            const time =
                dateParts[1];


            const dateValues =
                date.split("-");


            year =
                dateValues[0];


            month =
                dateValues[1];


            day =
                dateValues[2];


            const timeParts =
                time.split(":");


            hours =
                parseInt(
                    timeParts[0]
                );


            minutes =
                timeParts[1];


            seconds =
                timeParts[2];

        }


        // =================================================
        // MONTH NAME → NUMBER
        // =================================================

        const monthNames = {

            Jan: "01",
            Feb: "02",
            Mar: "03",
            Apr: "04",
            May: "05",
            Jun: "06",
            Jul: "07",
            Aug: "08",
            Sep: "09",
            Oct: "10",
            Nov: "11",
            Dec: "12"

        };


        if (monthNames[month]) {

            month =
                monthNames[month];

        }


        // =================================================
        // AM / PM
        // =================================================

        const period =
            hours >= 12
                ? "PM"
                : "AM";


        let displayHours =
            hours % 12;


        if (displayHours === 0) {

            displayHours = 12;

        }


        displayHours =
            String(displayHours)
                .padStart(2, "0");


        // =================================================
        // RETURN
        // =================================================

        return {

            date:
                `${day}/${month}/${year}`,

            time:
                `${displayHours}:${minutes}:${seconds} ${period}`

        };

    }



    // =====================================================
    // LOAD USER PROFILE
    // =====================================================

    async function loadUserProfile() {


        try {


            const response =
                await fetch(
                    `${API_URL}/users/${userId}`
                );


            const data =
                await response.json();


            if (
                !response.ok ||
                !data.success
            ) {

                console.error(
                    "Failed to load user profile."
                );

                return;

            }


            const user =
                data.user;


            // =================================================
            // SAVE USER INFORMATION
            // =================================================

            if (user.fullname) {

                localStorage.setItem(
                    "user_fullname",
                    user.fullname
                );

            }


            if (user.email) {

                localStorage.setItem(
                    "user_email",
                    user.email
                );

            }


            // =================================================
            // GET FIRST LETTER OF NAME
            // =================================================

            let initial = "P";


            if (user.fullname) {

                const trimmedName =
                    user.fullname.trim();


                if (trimmedName.length > 0) {

                    initial =
                        trimmedName
                            .charAt(0)
                            .toUpperCase();

                }

            }


            // =================================================
            // DISPLAY INITIAL
            // =================================================

            if (userAvatarInitial) {

                userAvatarInitial.textContent =
                    initial;

            }


            // =================================================
            // PROFILE PHOTO
            // =================================================

            if (
                user.profile_photo_url &&
                userAvatarImage
            ) {


                userAvatarImage.src =
                    `${API_URL}${user.profile_photo_url}?t=${Date.now()}`;


                userAvatarImage.style.display =
                    "block";


                if (userAvatarInitial) {

                    userAvatarInitial.style.display =
                        "none";

                }


                // =============================================
                // IF IMAGE FAILS
                // =============================================

                userAvatarImage.onerror =
                    function () {

                        userAvatarImage.style.display =
                            "none";


                        if (userAvatarInitial) {

                            userAvatarInitial.style.display =
                                "flex";

                        }

                    };

            }


        }


        catch (error) {


            console.error(
                "Error loading user profile:",
                error
            );


        }

    }



    // =====================================================
    // USER MENU
    // =====================================================

    function setupUserMenu() {


        if (
            !userMenuButton ||
            !userDropdown
        ) {

            return;

        }


        // =================================================
        // OPEN / CLOSE DROPDOWN
        // =================================================

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


        // =================================================
        // CLICK OUTSIDE
        // =================================================

        document.addEventListener(
            "click",
            function () {


                userDropdown.classList.remove(
                    "show"
                );


                userMenuButton.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }
        );


        // =================================================
        // PREVENT DROPDOWN FROM CLOSING
        // =================================================

        userDropdown.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

            }
        );


        // =================================================
        // LOGOUT
        // =================================================

        if (logoutLink) {


            logoutLink.addEventListener(
                "click",
                function (event) {


                    event.preventDefault();


                    // =========================================
                    // CLEAR LOGIN DATA
                    // =========================================

                    localStorage.removeItem(
                        "user_id"
                    );


                    localStorage.removeItem(
                        "user_fullname"
                    );


                    localStorage.removeItem(
                        "user_email"
                    );


                    localStorage.removeItem(
                        "last_screening_id"
                    );


                    localStorage.removeItem(
                        "screening_id"
                    );


                    // =========================================
                    // GO TO LOGIN
                    // =========================================

                    window.location.href =
                        "../../login.html";

                }
            );

        }

    }



    // =====================================================
    // LOAD SCREENING HISTORY FROM BACKEND
    // =====================================================

    async function loadScreeningHistory() {


        try {


            console.log(
                "Loading screenings for user:",
                userId
            );


            const response =
                await fetch(
                    `${API_URL}/screenings/${userId}`
                );


            const data =
                await response.json();


            console.log(
                "Screening history:",
                data
            );


            // =================================================
            // CHECK RESPONSE
            // =================================================

            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.message ||
                    "Failed to load screening history."
                );

            }


            // =================================================
            // SAVE DATA
            // =================================================

            allScreenings =
                data.screenings || [];


            // =================================================
            // DISPLAY DATA
            // =================================================

            displayScreenings(
                allScreenings
            );


        }


        catch (error) {


            console.error(
                "History error:",
                error
            );


            historyTable.innerHTML = `

                <tr>

                    <td
                        colspan="5"
                        style="text-align:center;"
                    >

                        Unable to load screening history.

                    </td>

                </tr>

            `;

        }

    }



    // =====================================================
    // DISPLAY SCREENINGS
    // =====================================================

    function displayScreenings(
        screenings
    ) {


        // =================================================
        // NO RESULTS
        // =================================================

        if (
            !screenings ||
            screenings.length === 0
        ) {


            historyTable.innerHTML = "";


            emptyMessage.style.display =
                "block";


            return;

        }


        // =================================================
        // HIDE EMPTY MESSAGE
        // =================================================

        emptyMessage.style.display =
            "none";


        // =================================================
        // CLEAR TABLE
        // =================================================

        historyTable.innerHTML = "";


        // =================================================
        // CREATE TABLE ROW FOR EACH SCREENING
        // =================================================

        screenings.forEach(
            function (screening) {


                // =================================================
                // DATE + TIME
                // =================================================

                const dateTime =
                    formatDateTime(
                        screening.created_at
                    );


                // =================================================
                // PREDICTION
                // =================================================

                const prediction =
                    screening.prediction ||
                    "Pending";


                // =================================================
                // CONFIDENCE
                // =================================================

                let confidence =
                    screening.confidence;


                if (
                    confidence !== null &&
                    confidence !== undefined
                ) {


                    confidence =
                        Number(
                            confidence
                        ).toFixed(2) + "%";

                }


                else {

                    confidence =
                        "-";

                }


                // =================================================
                // RISK
                // =================================================

                const risk =
                    screening.risk_status ||
                    "Pending";


                // =================================================
                // PREDICTION CSS CLASS
                // =================================================

                let predictionClass =
                    "pending";


                if (
                    prediction.toLowerCase() ===
                    "cancer"
                ) {

                    predictionClass =
                        "suspicious";

                }


                else if (
                    prediction.toLowerCase() ===
                    "not cancer"
                ) {

                    predictionClass =
                        "normal";

                }


                // =================================================
                // CREATE TABLE ROW
                // =================================================

                const row =
                    document.createElement("tr");


                row.innerHTML = `

                    <td>

                        ${dateTime.date}

                        <br>

                        <small>
                            ${dateTime.time}
                        </small>

                    </td>


                    <td>

                        <span
                            class="result ${predictionClass}"
                        >

                            ${prediction}

                        </span>

                    </td>


                    <td>

                        ${confidence}

                    </td>


                    <td>

                        ${risk}

                    </td>


                    <td>

                        <button
                            class="view-btn"
                            data-id="${screening.id}"
                        >

                            View Result

                        </button>

                    </td>

                `;


                // =================================================
                // ADD ROW
                // =================================================

                historyTable.appendChild(
                    row
                );

            }
        );


        // =================================================
        // VIEW RESULT BUTTONS
        // =================================================

        const viewButtons =
            document.querySelectorAll(
                ".view-btn"
            );


        viewButtons.forEach(
            function (button) {


                button.addEventListener(
                    "click",
                    function () {


                        const screeningId =
                            this.getAttribute(
                                "data-id"
                            );


                        console.log(
                            "Opening screening:",
                            screeningId
                        );


                        // =========================================
                        // OPEN RESULT PAGE
                        // =========================================

                        window.location.href =
                            `screening-result.html?id=${screeningId}`;

                    }
                );

            }
        );

    }



    // =====================================================
    // SEARCH + FILTER
    // =====================================================

    function filterResults() {


        const searchValue =
            searchInput.value
                .toLowerCase()
                .trim();


        const filterValue =
            resultFilter.value;


        // =================================================
        // FILTER DATABASE RESULTS
        // =================================================

        const filtered =
            allScreenings.filter(
                function (screening) {


                    const prediction =
                        (
                            screening.prediction ||
                            "pending"
                        ).toLowerCase();


                    const risk =
                        (
                            screening.risk_status ||
                            "pending"
                        ).toLowerCase();


                    // =============================================
                    // SEARCH
                    // =============================================

                    const searchableText =
                        `
                        ${prediction}
                        ${risk}
                        ${screening.created_at || ""}
                        ${screening.confidence || ""}
                        `.toLowerCase();


                    const matchesSearch =
                        searchableText.includes(
                            searchValue
                        );


                    // =============================================
                    // FILTER
                    // =============================================

                    let matchesFilter = true;


                    if (
                        filterValue !== "all"
                    ) {


                        matchesFilter =
                            prediction ===
                            filterValue;

                    }


                    return (
                        matchesSearch &&
                        matchesFilter
                    );

                }
            );


        // =================================================
        // DISPLAY FILTERED RESULTS
        // =================================================

        displayScreenings(
            filtered
        );

    }



    // =====================================================
    // SEARCH EVENT
    // =====================================================

    searchInput.addEventListener(
        "input",
        filterResults
    );



    // =====================================================
    // FILTER EVENT
    // =====================================================

    resultFilter.addEventListener(
        "change",
        filterResults
    );



    // =====================================================
    // LOAD SCREENINGS
    // =====================================================

    loadScreeningHistory();


});
