// =========================================================
// ORALAI - PATIENT PROFILE JAVASCRIPT
// =========================================================
//
// Handles:
//
// 1. Loading patient profile
// 2. Showing full name
// 3. Showing email
// 4. Showing first login date/time
// 5. Showing profile photo
// 6. Showing first-letter avatar
// 7. Changing name
// 8. Uploading profile photo
// 9. Top-right user dropdown
// 10. Logout
//
// Password + Appearance are handled in:
// patient-settings.html / patient-settings.js
//
// =========================================================


// =========================================================
// BACKEND API URL
// =========================================================

const API_URL = "http://127.0.0.1:5000";


// =========================================================
// GET LOGGED-IN USER
// =========================================================

const userId = localStorage.getItem("user_id");


// =========================================================
// CHECK LOGIN
// =========================================================

if (!userId) {

    window.location.href = "../../login.html";

}


// =========================================================
// PAGE ELEMENTS
// =========================================================

const profileImage =
    document.getElementById("profileImage");

const profileInitial =
    document.getElementById("profileInitial");

const profileName =
    document.getElementById("profileName");

const profileEmail =
    document.getElementById("profileEmail");

const fullnameInput =
    document.getElementById("fullnameInput");

const emailDisplay =
    document.getElementById("emailDisplay");

const memberSince =
    document.getElementById("memberSince");

const profilePhotoInput =
    document.getElementById("profilePhotoInput");

const nameForm =
    document.getElementById("nameForm");


// =========================================================
// TOP USER MENU ELEMENTS
// =========================================================

const userMenuButton =
    document.getElementById("userMenuButton");

const userDropdown =
    document.getElementById("userDropdown");

const userWelcome =
    document.getElementById("userWelcome");

const logoutLink =
    document.getElementById("logoutLink");


// =========================================================
// GET FIRST LETTER
// =========================================================
//
// Example:
//
// Madhusha Udani
//      ↓
//      M
//
// =========================================================

function getFirstLetter(name) {

    if (!name) {

        return "P";

    }


    return name
        .trim()
        .charAt(0)
        .toUpperCase();

}


// =========================================================
// GET FIRST NAME
// =========================================================
//
// Example:
//
// Madhusha Udani
//      ↓
// Madhusha
//
// =========================================================

function getFirstName(name) {

    if (!name) {

        return "Patient";

    }


    return name
        .trim()
        .split(" ")[0];

}


// =========================================================
// FORMAT FIRST LOGIN DATE/TIME
// =========================================================
//
// Backend may return:
//
// 2026-09-15 10:05:21
//
// or:
//
// Tue, 15 Sep 2026 10:05:21 GMT
//
// We display:
//
// 15/09/2026 10:05:21 AM
//
// =========================================================

function formatMemberSince(dateValue) {

    if (!dateValue) {

        return "-";

    }


    let day;
    let month;
    let year;

    let hour;
    let minute;
    let second;


    // =====================================================
    // Flask HTTP DATE FORMAT
    // =====================================================

    if (
        typeof dateValue === "string" &&
        dateValue.includes("GMT")
    ) {

        const cleanValue =
            dateValue.replace(" GMT", "");

        const parts =
            cleanValue.split(" ");


        day = parts[1];

        const monthName = parts[2];

        year = parts[3];


        const timeParts =
            parts[4].split(":");


        hour =
            parseInt(timeParts[0], 10);

        minute =
            timeParts[1];

        second =
            timeParts[2];


        const monthMap = {

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


        month =
            monthMap[monthName];

    }


    // =====================================================
    // MYSQL FORMAT
    //
    // 2026-09-15 10:05:21
    // =====================================================

    else {

        const value =
            String(dateValue);


        const parts =
            value.split(" ");


        const datePart =
            parts[0];

        const timePart =
            parts[1];


        if (!datePart) {

            return value;

        }


        const dateParts =
            datePart.split("-");


        year =
            dateParts[0];

        month =
            dateParts[1];

        day =
            dateParts[2];


        if (timePart) {

            const timeParts =
                timePart.split(":");


            hour =
                parseInt(timeParts[0], 10);

            minute =
                timeParts[1];

            second =
                timeParts[2];

        } else {

            hour = 0;

            minute = "00";

            second = "00";

        }

    }


    // =====================================================
    // 24 HOUR → 12 HOUR
    // =====================================================

    const numericHour =
        parseInt(hour, 10);


    const period =
        numericHour >= 12
            ? "PM"
            : "AM";


    let displayHour =
        numericHour % 12;


    if (displayHour === 0) {

        displayHour = 12;

    }


    displayHour =
        String(displayHour)
            .padStart(2, "0");


    return (
        `${day}/${month}/${year} ` +
        `${displayHour}:${minute}:${second} ${period}`
    );

}


// =========================================================
// UPDATE AVATAR
// =========================================================

function updateAvatar(fullname, photoUrl) {

    const firstLetter =
        getFirstLetter(fullname);


    // =====================================================
    // NO PROFILE PHOTO
    // =====================================================

    if (!photoUrl) {

        profileImage.style.display =
            "none";


        profileInitial.style.display =
            "flex";


        profileInitial.textContent =
            firstLetter;


        return;

    }


    // =====================================================
    // PROFILE PHOTO EXISTS
    // =====================================================

    profileImage.src =
        API_URL +
        photoUrl +
        "?t=" +
        Date.now();


    profileImage.style.display =
        "block";


    profileInitial.style.display =
        "none";

}


// =========================================================
// LOAD PROFILE
// =========================================================

async function loadProfile() {

    try {

        const response =
            await fetch(
                `${API_URL}/users/${userId}`
            );


        const data =
            await response.json();


        if (!response.ok || !data.success) {

            throw new Error(
                data.message ||
                "Failed to load profile."
            );

        }


        const user =
            data.user;


        // =================================================
        // FULL NAME
        // =================================================

        profileName.textContent =
            user.fullname;


        fullnameInput.value =
            user.fullname;


        // =================================================
        // EMAIL
        // =================================================

        profileEmail.textContent =
            user.email;


        emailDisplay.value =
            user.email;


        // =================================================
        // FIRST LOGIN
        // =================================================
        //
        // IMPORTANT:
        // Use first_login_at instead of created_at.
        //
        // =================================================

        memberSince.textContent =
            formatMemberSince(
                user.first_login_at
            );


        // =================================================
        // TOP-RIGHT USER NAME
        // =================================================

        const firstName =
            getFirstName(
                user.fullname
            );


        userWelcome.textContent =
            `Welcome, ${firstName}`;


        // =================================================
        // AVATAR
        // =================================================

        updateAvatar(

            user.fullname,

            user.profile_photo_url

        );


        // =================================================
        // UPDATE LOCAL STORAGE
        // =================================================

        localStorage.setItem(
            "user_fullname",
            user.fullname
        );


        localStorage.setItem(
            "user_email",
            user.email
        );


    } catch (error) {

        console.error(
            "Profile loading error:",
            error
        );


        alert(
            "Unable to load your profile."
        );

    }

}


// =========================================================
// CHANGE NAME
// =========================================================

nameForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const newName =
            fullnameInput.value.trim();


        // =================================================
        // VALIDATION
        // =================================================

        if (!newName) {

            alert(
                "Please enter your full name."
            );

            return;

        }


        try {

            const response =
                await fetch(

                    `${API_URL}/users/${userId}/name`,

                    {

                        method: "PUT",

                        headers: {

                            "Content-Type":
                                "application/json"

                        },

                        body: JSON.stringify({

                            fullname:
                                newName

                        })

                    }

                );


            const data =
                await response.json();


            if (!response.ok || !data.success) {

                throw new Error(
                    data.message ||
                    "Failed to update name."
                );

            }


            // =================================================
            // UPDATE PROFILE PAGE
            // =================================================

            profileName.textContent =
                data.fullname;


            fullnameInput.value =
                data.fullname;


            // =================================================
            // UPDATE TOP MENU
            // =================================================

            const firstName =
                getFirstName(
                    data.fullname
                );


            userWelcome.textContent =
                `Welcome, ${firstName}`;


            // =================================================
            // UPDATE AVATAR
            // =================================================

            const firstLetter =
                getFirstLetter(
                    data.fullname
                );


            profileInitial.textContent =
                firstLetter;


            // =================================================
            // UPDATE LOCAL STORAGE
            // =================================================

            localStorage.setItem(
                "user_fullname",
                data.fullname
            );


            alert(
                "Full name updated successfully."
            );


        } catch (error) {

            console.error(
                "Name update error:",
                error
            );


            alert(
                error.message ||
                "Failed to update name."
            );

        }

    }
);


// =========================================================
// PROFILE PHOTO UPLOAD
// =========================================================

profilePhotoInput.addEventListener(
    "change",
    async function () {

        const file =
            profilePhotoInput.files[0];


        if (!file) {

            return;

        }


        // =================================================
        // ALLOWED FILE TYPES
        // =================================================

        const allowedTypes = [

            "image/jpeg",
            "image/png",
            "image/webp"

        ];


        if (!allowedTypes.includes(file.type)) {

            alert(
                "Please select a JPG, PNG or WEBP image."
            );


            profilePhotoInput.value =
                "";


            return;

        }


        // =================================================
        // FILE SIZE
        // =================================================

        if (file.size > 5 * 1024 * 1024) {

            alert(
                "Profile photo must be smaller than 5 MB."
            );


            profilePhotoInput.value =
                "";


            return;

        }


        try {

            const formData =
                new FormData();


            formData.append(
                "photo",
                file
            );


            const response =
                await fetch(

                    `${API_URL}/users/${userId}/profile-photo`,

                    {

                        method: "POST",

                        body: formData

                    }

                );


            const data =
                await response.json();


            if (!response.ok || !data.success) {

                throw new Error(
                    data.message ||
                    "Failed to upload profile photo."
                );

            }


            // =================================================
            // SHOW NEW IMAGE
            // =================================================

            profileImage.src =
                API_URL +
                data.profile_photo_url +
                "?t=" +
                Date.now();


            profileImage.style.display =
                "block";


            profileInitial.style.display =
                "none";


            alert(
                "Profile photo updated successfully."
            );


        } catch (error) {

            console.error(
                "Profile photo error:",
                error
            );


            alert(
                error.message ||
                "Failed to upload profile photo."
            );

        }


        // Clear input

        profilePhotoInput.value = "";

    }
);


// =========================================================
// USER DROPDOWN
// =========================================================

function setupUserMenu() {

    if (
        !userMenuButton ||
        !userDropdown
    ) {

        return;

    }


    // =====================================================
    // OPEN / CLOSE DROPDOWN
    // =====================================================

    userMenuButton.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

            userDropdown.classList.toggle(
                "show"
            );

        }
    );


    // =====================================================
    // CLICK OUTSIDE → CLOSE
    // =====================================================

    document.addEventListener(
        "click",
        function () {

            userDropdown.classList.remove(
                "show"
            );

        }
    );


    // =====================================================
    // CLICK INSIDE DROPDOWN
    // =====================================================

    userDropdown.addEventListener(
        "click",
        function (event) {

            event.stopPropagation();

        }
    );

}


// =========================================================
// LOGOUT
// =========================================================

function logout(event) {

    if (event) {

        event.preventDefault();

    }


    // =====================================================
    // REMOVE LOGIN INFORMATION
    // =====================================================

    localStorage.removeItem(
        "user_id"
    );


    localStorage.removeItem(
        "user_fullname"
    );


    localStorage.removeItem(
        "user_email"
    );


    // =====================================================
    // DO NOT REMOVE THEME
    // =====================================================

    window.location.href =
        "../../login.html";

}


// =========================================================
// LOGOUT EVENT
// =========================================================

if (logoutLink) {

    logoutLink.addEventListener(
        "click",
        logout
    );

}


// =========================================================
// INITIAL PAGE LOAD
// =========================================================

setupUserMenu();

loadProfile();
