// ============================================================
// OralAI - Screening Result Page

// BACKEND API URL

const API_URL =
    "http://127.0.0.1:5000";

// GET SCREENING ID FROM URL

// Example:
//
// screening-result.html?id=6

const urlParams =
    new URLSearchParams(
        window.location.search
    );

const screeningId =
    urlParams.get("id");


// ============================================================
// GET HTML ELEMENTS
// ============================================================

const predictionResult =
    document.getElementById(
        "predictionResult"
    );

const confidence =
    document.getElementById(
        "confidence"
    );

const riskStatus =
    document.getElementById(
        "riskStatus"
    );

const resultImage =
    document.getElementById(
        "resultImage"
    );

const gradcamImage =
    document.getElementById(
        "gradcamImage"
    );

const gradcamMessage =
    document.getElementById(
        "gradcamMessage"
    );

const nlpExplanation =
    document.getElementById(
        "nlpExplanation"
    );

const statusIcon =
    document.getElementById(
        "statusIcon"
    );

const screeningDate =
    document.getElementById(
        "screeningDate"
    );

const screeningTime =
    document.getElementById(
        "screeningTime"
    );


// ============================================================
// USER ACCOUNT MENU ELEMENTS
// ============================================================

const userMenuButton =
    document.getElementById(
        "userMenuButton"
    );

const userDropdown =
    document.getElementById(
        "userDropdown"
    );

const userAvatarImage =
    document.getElementById(
        "userAvatarImage"
    );

const userAvatarInitial =
    document.getElementById(
        "userAvatarInitial"
    );

const logoutLink =
    document.getElementById(
        "logoutLink"
    );


// ============================================================
// GET LOGGED-IN USER ID
// ============================================================

const userId =
    localStorage.getItem(
        "user_id"
    );


// ============================================================
// CHECK USER SESSION
// ============================================================

if (!userId) {

    alert(
        "User session not found. Please login again."
    );

    window.location.href =
        "../../login.html";

} else {

    // Load patient avatar
    loadUserAvatar(userId);

    // Setup account dropdown
    setupUserMenu();

}


// ============================================================
// FUNCTION: LOAD USER AVATAR
// ============================================================

async function loadUserAvatar(userId) {

    try {

        console.log(
            "Loading user profile:",
            userId
        );


        // ----------------------------------------------------
        // GET USER INFORMATION
        // ----------------------------------------------------

        const response =
            await fetch(
                `${API_URL}/users/${userId}`
            );


        // ----------------------------------------------------
        // CONVERT RESPONSE TO JSON
        // ----------------------------------------------------

        const data =
            await response.json();


        console.log(
            "User profile response:",
            data
        );


        // ----------------------------------------------------
        // CHECK RESPONSE
        // ----------------------------------------------------

        if (
            !response.ok ||
            !data.success ||
            !data.user
        ) {

            console.error(
                "Unable to load user profile."
            );

            return;
        }


        const user =
            data.user;


        // ====================================================
        // SAVE USER INFORMATION
        // ====================================================

        localStorage.setItem(
            "user_fullname",
            user.fullname || ""
        );

        localStorage.setItem(
            "user_email",
            user.email || ""
        );


        // ====================================================
        // GET FIRST LETTER OF FULL NAME
        // ====================================================

        const fullName =
            (
                user.fullname ||
                "Patient"
            ).trim();


        const initial =
            fullName
                .charAt(0)
                .toUpperCase();


        // ====================================================
        // DISPLAY INITIAL
        // ====================================================

        if (userAvatarInitial) {

            userAvatarInitial.textContent =
                initial;

            userAvatarInitial.style.display =
                "flex";
        }


        // ====================================================
        // DISPLAY PROFILE PHOTO
        // ====================================================

        if (
            user.profile_photo_url &&
            userAvatarImage
        ) {

            const profilePhotoUrl =
                `${API_URL}${user.profile_photo_url}?t=${Date.now()}`;


            console.log(
                "Profile photo URL:",
                profilePhotoUrl
            );


            userAvatarImage.src =
                profilePhotoUrl;


            userAvatarImage.style.display =
                "block";


            // Hide initial when image loads
            userAvatarImage.onload =
                function () {

                    if (userAvatarInitial) {

                        userAvatarInitial.style.display =
                            "none";
                    }

                };


            // If image fails,
            // show initial again
            userAvatarImage.onerror =
                function () {

                    console.error(
                        "Profile photo could not be loaded."
                    );


                    userAvatarImage.style.display =
                        "none";


                    if (userAvatarInitial) {

                        userAvatarInitial.style.display =
                            "flex";
                    }

                };

        }

    } catch (error) {

        console.error(
            "Error loading user profile:",
            error
        );

    }

}


// ============================================================
// FUNCTION: SETUP USER MENU
// ============================================================

function setupUserMenu() {

    // --------------------------------------------------------
    // Check required elements
    // --------------------------------------------------------

    if (
        !userMenuButton ||
        !userDropdown
    ) {

        return;
    }


    // ========================================================
    // OPEN / CLOSE DROPDOWN
    // ========================================================

    userMenuButton.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();


            const isOpen =
                userDropdown.classList.toggle(
                    "show"
                );


            // Update accessibility attribute

            userMenuButton.setAttribute(
                "aria-expanded",
                isOpen
                    ? "true"
                    : "false"
            );

        }
    );


    // ========================================================
    // PREVENT DROPDOWN CLICK FROM CLOSING IT
    // ========================================================

    userDropdown.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

        }
    );


    // ========================================================
    // CLOSE WHEN CLICKING OUTSIDE
    // ========================================================

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

}


// ============================================================
// LOGOUT
// ============================================================

if (logoutLink) {

    logoutLink.addEventListener(
        "click",
        function (event) {

            event.preventDefault();


            // ------------------------------------------------
            // Logout confirmation is intentionally NOT added
            // yet.
            // ------------------------------------------------

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


            // ------------------------------------------------
            // GO TO LOGIN PAGE
            // ------------------------------------------------

            window.location.href =
                "../../login.html";

        }
    );

}


// ============================================================
// CHECK SCREENING ID
// ============================================================

if (!screeningId) {

    console.error(
        "No screening ID found in URL."
    );


    alert(
        "Screening result could not be loaded."
    );

} else {

    loadScreeningResult();

}


// ============================================================
// FUNCTION: LOAD SCREENING RESULT
// ============================================================

async function loadScreeningResult() {

    try {

        console.log(
            "Requesting screening result:",
            screeningId
        );


        // ----------------------------------------------------
        // GET RESULT FROM BACKEND
        // ----------------------------------------------------

        const response =
            await fetch(
                `${API_URL}/screenings/result/${screeningId}`
            );


        console.log(
            "Backend response status:",
            response.status
        );


        // ----------------------------------------------------
        // CHECK RESPONSE
        // ----------------------------------------------------

        if (!response.ok) {

            throw new Error(
                `Backend returned status ${response.status}`
            );

        }


        // ----------------------------------------------------
        // CONVERT RESPONSE TO JSON
        // ----------------------------------------------------

        const data =
            await response.json();


        console.log(
            "Screening result response:",
            data
        );


        // ----------------------------------------------------
        // CHECK SCREENING DATA
        // ----------------------------------------------------

        if (
            !data.success ||
            !data.screening
        ) {

            throw new Error(
                "Screening result not found."
            );

        }


        const screening =
            data.screening;

            // ====================================================
            // DISPLAY NLP SCREENING EXPLANATION
            // ====================================================

        if (
            screening.explanation &&
            screening.explanation.trim() !== ""
        ) {

            nlpExplanation.textContent =
                screening.explanation;

        } else {

            nlpExplanation.textContent =
                "AI screening explanation is currently unavailable.";
        }

        // ====================================================
        // DISPLAY PREDICTION
        // ====================================================

        if (screening.prediction) {

            predictionResult.textContent =
                screening.prediction;

        } else {

            predictionResult.textContent =
                "Pending";

        }


        // ====================================================
        // DISPLAY CONFIDENCE
        // ====================================================

        if (
            screening.confidence !== null &&
            screening.confidence !== undefined
        ) {

            confidence.textContent =
                `${Number(
                    screening.confidence
                ).toFixed(2)}%`;

        } else {

            confidence.textContent =
                "N/A";

        }


        // ====================================================
        // DISPLAY RISK STATUS
        // ====================================================

        if (screening.risk_status) {

            riskStatus.textContent =
                screening.risk_status;

        } else {

            riskStatus.textContent =
                "Pending";

        }


        // ====================================================
        // DISPLAY ORIGINAL SCREENING IMAGE
        // ====================================================

        if (screening.image_path) {


            // ------------------------------------------------
            // Convert Windows path to browser path
            // ------------------------------------------------

            const imagePath =
                screening.image_path.replace(
                    /\\/g,
                    "/"
                );


            const imageUrl =
                `${API_URL}/${imagePath}`;


            console.log(
                "Original image path:",
                screening.image_path
            );


            console.log(
                "Final image URL:",
                imageUrl
            );


            // ------------------------------------------------
            // Set image
            // ------------------------------------------------

            resultImage.src =
                imageUrl;


            resultImage.style.display =
                "block";


            // ------------------------------------------------
            // Image loaded successfully
            // ------------------------------------------------

            resultImage.onload =
                function () {

                    console.log(
                        "Original screening image loaded successfully."
                    );

                };


            // ------------------------------------------------
            // Image loading failed
            // ------------------------------------------------

            resultImage.onerror =
                function () {

                    console.error(
                        "Could not load screening image:",
                        imageUrl
                    );

                };

        } else {

            resultImage.style.display =
                "none";

        }


        // ====================================================
        // DISPLAY GRAD-CAM
        // ====================================================

        // Grad-CAM implementation is currently pending.
        // If gradcam_path is NULL,
        // the pending message will be displayed.

        if (
            screening.gradcam_path &&
            screening.gradcam_path !== ""
        ) {


            const gradcamPath =
                screening.gradcam_path.replace(
                    /\\/g,
                    "/"
                );


            const gradcamUrl =
                `${API_URL}/${gradcamPath}`;


            console.log(
                "Grad-CAM URL:",
                gradcamUrl
            );


            gradcamImage.src =
                gradcamUrl;


            gradcamImage.style.display =
                "block";


            if (gradcamMessage) {

                gradcamMessage.style.display =
                    "none";

            }

        } else {


            console.log(
                "Grad-CAM is not available yet."
            );


            if (gradcamImage) {

                gradcamImage.style.display =
                    "none";

            }


            if (gradcamMessage) {

                gradcamMessage.style.display =
                    "block";


                gradcamMessage.textContent =
                    "Grad-CAM explanation is currently unavailable. It will be shown once the explainability process is completed.";

            }

        }


        // ====================================================
        // DISPLAY STATUS ICON
        // ====================================================

        if (statusIcon) {

            if (
                screening.prediction &&
                screening.prediction
                    .toLowerCase()
                    .includes("cancer")
            ) {

                statusIcon.textContent =
                    "⚠️";

            } else {

                statusIcon.textContent =
                    "✓";

            }

        }


        // ====================================================
        // DISPLAY DATE AND TIME
        // ====================================================

        if (screening.created_at) {

            displayDatabaseDateTime(
                screening.created_at
            );

        } else {

            screeningDate.textContent =
                "N/A";

            screeningTime.textContent =
                "N/A";

        }


        // ====================================================
        // SAVE LAST SCREENING ID
        // ====================================================

        localStorage.setItem(
            "last_screening_id",
            screeningId
        );


    } catch (error) {

        console.error(
            "Error loading screening result:",
            error
        );


        predictionResult.textContent =
            "Unable to load";


        confidence.textContent =
            "N/A";


        riskStatus.textContent =
            "N/A";


        screeningDate.textContent =
            "N/A";


        screeningTime.textContent =
            "N/A";


        if (gradcamMessage) {

            gradcamMessage.textContent =
                "Unable to load screening result.";

        }

    }

}


// ============================================================
// FUNCTION: DISPLAY DATABASE DATE AND TIME
// ============================================================
//
// This function does NOT perform timezone conversion.
//
// It displays the database time exactly as received.
// ============================================================

function displayDatabaseDateTime(dateString) {

    try {

        console.log(
            "Original created_at:",
            dateString
        );


        // ====================================================
        // STEP 1
        // Clean backend date string
        // ====================================================

        let cleanDate =
            dateString.trim();


        // ====================================================
        // STEP 2
        // CHECK GMT FORMAT
        // ====================================================

        if (
            cleanDate.includes("GMT")
        ) {


            // ------------------------------------------------
            // Remove GMT
            // ------------------------------------------------

            cleanDate =
                cleanDate.replace(
                    " GMT",
                    ""
                );


            // ------------------------------------------------
            // Split date
            // ------------------------------------------------

            const parts =
                cleanDate.split(" ");


            const day =
                parts[1];

            const monthName =
                parts[2];

            const year =
                parts[3];

            const timePart =
                parts[4];


            // ------------------------------------------------
            // Month mapping
            // ------------------------------------------------

            const months = {

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


            const month =
                months[monthName];


            // ------------------------------------------------
            // Format date
            // ------------------------------------------------

            const formattedDate =
                `${day}/${month}/${year}`;


            // ------------------------------------------------
            // Split time
            // ------------------------------------------------

            const timeParts =
                timePart.split(":");


            let hour =
                parseInt(
                    timeParts[0],
                    10
                );


            const minute =
                timeParts[1];

            const second =
                timeParts[2];


            // ------------------------------------------------
            // AM / PM
            // ------------------------------------------------

            let period;


            if (hour >= 12) {

                period = "PM";

            } else {

                period = "AM";

            }


            // ------------------------------------------------
            // Convert 24-hour -> 12-hour
            // ------------------------------------------------

            let displayHour;


            if (hour === 0) {

                displayHour = 12;

            } else if (hour > 12) {

                displayHour =
                    hour - 12;

            } else {

                displayHour =
                    hour;

            }


            // ------------------------------------------------
            // Add leading zero
            // ------------------------------------------------

            displayHour =
                String(displayHour)
                    .padStart(2, "0");


            // ------------------------------------------------
            // Final time
            // ------------------------------------------------

            const formattedTime =
                `${displayHour}:${minute}:${second} ${period}`;


            // ------------------------------------------------
            // Display
            // ------------------------------------------------

            screeningDate.textContent =
                formattedDate;

            screeningTime.textContent =
                formattedTime;


            console.log(
                "Displayed Date:",
                formattedDate
            );

            console.log(
                "Displayed Time:",
                formattedTime
            );


        } else {


            // =================================================
            // MYSQL DIRECT FORMAT
            // =================================================

            // Example:
            //
            // 2026-09-15 10:07:44


            const parts =
                cleanDate.split(" ");


            const datePart =
                parts[0];

            const timePart =
                parts[1];


            // ------------------------------------------------
            // Date
            // ------------------------------------------------

            const dateParts =
                datePart.split("-");


            const year =
                dateParts[0];

            const month =
                dateParts[1];

            const day =
                dateParts[2];


            const formattedDate =
                `${day}/${month}/${year}`;


            // ------------------------------------------------
            // Time
            // ------------------------------------------------

            const timeParts =
                timePart.split(":");


            let hour =
                parseInt(
                    timeParts[0],
                    10
                );


            const minute =
                timeParts[1];

            const second =
                timeParts[2];


            // ------------------------------------------------
            // AM / PM
            // ------------------------------------------------

            let period;


            if (hour >= 12) {

                period = "PM";

            } else {

                period = "AM";

            }


            // ------------------------------------------------
            // Convert 24-hour -> 12-hour
            // ------------------------------------------------

            let displayHour;


            if (hour === 0) {

                displayHour = 12;

            } else if (hour > 12) {

                displayHour =
                    hour - 12;

            } else {

                displayHour =
                    hour;

            }


            // ------------------------------------------------
            // Add leading zero
            // ------------------------------------------------

            displayHour =
                String(displayHour)
                    .padStart(2, "0");


            // ------------------------------------------------
            // Final time
            // ------------------------------------------------

            const formattedTime =
                `${displayHour}:${minute}:${second} ${period}`;


            // ------------------------------------------------
            // Display
            // ------------------------------------------------

            screeningDate.textContent =
                formattedDate;

            screeningTime.textContent =
                formattedTime;


            console.log(
                "Displayed Date:",
                formattedDate
            );


            console.log(
                "Displayed Time:",
                formattedTime
            );

        }


    } catch (error) {

        console.error(
            "Date/time formatting error:",
            error
        );


        screeningDate.textContent =
            "N/A";


        screeningTime.textContent =
            "N/A";

    }

}


// ============================================================
// NEW SCREENING BUTTON
// ============================================================

const newScreeningButton =
    document.getElementById(
        "newScreeningBtn"
    );


if (newScreeningButton) {

    newScreeningButton.addEventListener(
        "click",
        function () {

            window.location.href =
                "new-screening.html";

        }
    );

}


// ============================================================
// VIEW MY RESULTS BUTTON
// ============================================================

const viewResultsButton =
    document.getElementById(
        "viewResultsBtn"
    );


if (viewResultsButton) {

    viewResultsButton.addEventListener(
        "click",
        function () {

            window.location.href =
                "screening-history.html";

        }
    );

}


// =====================================================
// DOWNLOAD SCREENING REPORT (PDF)
// =====================================================

const downloadReportButton = document.getElementById("downloadReport");

console.log("Download Report button found:", downloadReportButton);

if (downloadReportButton) {
    downloadReportButton.addEventListener("click", async function () {
        console.log("Download Report button clicked!");

        const originalText = downloadReportButton.textContent;

        try {
            const urlParams = new URLSearchParams(window.location.search);
            const screeningId = urlParams.get("id");
            const userId = localStorage.getItem("user_id");

            if (!screeningId || !userId) {
                alert("Screening ID or patient information is missing.");
                return;
            }

            downloadReportButton.disabled = true;
            downloadReportButton.textContent = "Generating PDF...";

            const reportUrl =
                `http://127.0.0.1:5000/screenings/${encodeURIComponent(screeningId)}/report?user_id=${encodeURIComponent(userId)}`;

            const response = await fetch(reportUrl);

            console.log("Report response status:", response.status);
            console.log(
                "Report Content-Type:",
                response.headers.get("content-type")
            );

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Report server error:", errorText);
                throw new Error("The server could not generate the PDF report.");
            }

            const pdfBlob = await response.blob();

            console.log("Downloaded blob size:", pdfBlob.size);
            console.log("Downloaded blob type:", pdfBlob.type);

            if (pdfBlob.size === 0) {
                throw new Error("The generated PDF file is empty.");
            }

            if (pdfBlob.type !== "application/pdf") {
                const responseText = await pdfBlob.text();
                console.error("Expected PDF but received:", responseText);
                throw new Error(
                    "The server response is not a PDF. Check the Flask report service."
                );
            }

            const pdfUrl = URL.createObjectURL(pdfBlob);
            const downloadLink = document.createElement("a");

            downloadLink.href = pdfUrl;
            downloadLink.download =
                `OralAI_Screening_Report_${screeningId}.pdf`;

            document.body.appendChild(downloadLink);
            downloadLink.click();
            downloadLink.remove();

            // Release the temporary URL after the browser processes the download.
            setTimeout(() => URL.revokeObjectURL(pdfUrl), 1000);

            console.log("PDF download triggered successfully.");

        } catch (error) {
            console.error("Download Report Error:", error);
            alert(error.message || "Unable to download the report.");
        } finally {
            downloadReportButton.disabled = false;
            downloadReportButton.textContent = originalText;
        }
    });
}

