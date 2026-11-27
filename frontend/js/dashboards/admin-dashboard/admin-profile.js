const API_BASE_URL = "http://127.0.0.1:5000";

const adminId = localStorage.getItem("admin_id");

if (!adminId) {
    window.location.href = "../../login.html";
}

const profileForm = document.getElementById("profileForm");
const fullnameInput = document.getElementById("fullname");
const emailInput = document.getElementById("email");
const firstLoginInput = document.getElementById("firstLogin");

const profileFullName = document.getElementById("profileFullName");
const profileEmail = document.getElementById("profileEmail");

const profilePhoto = document.getElementById("profilePhoto");
const defaultProfileAvatar = document.getElementById("defaultProfileAvatar");

const topAvatar = document.getElementById("topAvatar");
const sidebarAvatar = document.getElementById("sidebarAvatar");
const sidebarAdminName = document.getElementById("sidebarAdminName");

const photoInput = document.getElementById("photoInput");
const removePhotoBtn = document.getElementById("removePhotoBtn");

const messageBox = document.getElementById("messageBox");

const profileAvatarButton = document.getElementById("profileAvatarButton");
const profileDropdown = document.getElementById("profileDropdown");

const sidebarLogout = document.getElementById("sidebarLogout");
const dropdownLogout = document.getElementById("dropdownLogout");
const settingsButton = document.getElementById("settingsButton");


/* ================================
   LOAD ADMIN PROFILE
================================ */

async function loadAdminProfile() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/admin/profile/${adminId}`
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            showMessage(
                data.message || "Failed to load admin profile.",
                "error"
            );
            return;
        }

        const admin = data.admin;

        fullnameInput.value = admin.fullname || "";
        emailInput.value = admin.email || "";
        firstLoginInput.value = formatDate(admin.first_login_at);

        profileFullName.textContent =
            admin.fullname || "Administrator";

        profileEmail.textContent =
            admin.email || "";

        sidebarAdminName.textContent =
            admin.fullname || "Administrator";

        const firstLetter =
            (admin.fullname || "A").charAt(0).toUpperCase();

        topAvatar.textContent = firstLetter;
        sidebarAvatar.textContent = firstLetter;
        defaultProfileAvatar.textContent = firstLetter;

        if (admin.profile_photo_url) {

            const photoURL =
                API_BASE_URL + admin.profile_photo_url;

            profilePhoto.src = photoURL;
            profilePhoto.style.display = "block";

            defaultProfileAvatar.style.display = "none";

            topAvatar.innerHTML =
                `<img src="${photoURL}" alt="Admin">`;

        } else {

            profilePhoto.style.display = "none";
            defaultProfileAvatar.style.display = "flex";

        }

    } catch (error) {

        console.error("Admin profile error:", error);

        showMessage(
            "Cannot connect to the backend server.",
            "error"
        );
    }
}


/* ================================
   UPDATE ADMIN NAME
================================ */

profileForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const fullname = fullnameInput.value.trim();

    if (!fullname) {

        showMessage(
            "Please enter your full name.",
            "error"
        );

        return;
    }

    try {

        const response = await fetch(
            `${API_BASE_URL}/admin/profile/${adminId}/name`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    fullname: fullname
                })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            showMessage(
                data.message || "Failed to update name.",
                "error"
            );

            return;
        }

        profileFullName.textContent = fullname;
        sidebarAdminName.textContent = fullname;

        const firstLetter =
            fullname.charAt(0).toUpperCase();

        topAvatar.textContent = firstLetter;
        sidebarAvatar.textContent = firstLetter;
        defaultProfileAvatar.textContent = firstLetter;

        localStorage.setItem(
            "admin_fullname",
            fullname
        );

        showMessage(
            "Profile name updated successfully.",
            "success"
        );

    } catch (error) {

        console.error("Update name error:", error);

        showMessage(
            "Cannot connect to the backend server.",
            "error"
        );
    }
});


/* ================================
   UPLOAD PROFILE PHOTO
================================ */

photoInput.addEventListener("change", async function () {

    const file = photoInput.files[0];

    if (!file) {
        return;
    }

    const formData = new FormData();

    formData.append("profile_photo", file);

    try {

        const response = await fetch(
            `${API_BASE_URL}/admin/profile/${adminId}/profile-photo`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            showMessage(
                data.message || "Failed to upload photo.",
                "error"
            );

            return;
        }

        const photoURL =
            API_BASE_URL + data.profile_photo_url;

        profilePhoto.src = photoURL;
        profilePhoto.style.display = "block";

        defaultProfileAvatar.style.display = "none";

        topAvatar.innerHTML =
            `<img src="${photoURL}" alt="Admin">`;

        showMessage(
            "Profile photo updated successfully.",
            "success"
        );

        photoInput.value = "";

    } catch (error) {

        console.error("Photo upload error:", error);

        showMessage(
            "Cannot connect to the backend server.",
            "error"
        );
    }
});


/* ================================
   REMOVE PROFILE PHOTO
================================ */

removePhotoBtn.addEventListener("click", async function () {

    try {

        const response = await fetch(
            `${API_BASE_URL}/admin/profile/${adminId}/profile-photo`,
            {
                method: "DELETE"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            showMessage(
                data.message || "Failed to remove photo.",
                "error"
            );

            return;
        }

        profilePhoto.src = "";
        profilePhoto.style.display = "none";

        defaultProfileAvatar.style.display = "flex";

        const fullname =
            fullnameInput.value || "Administrator";

        const firstLetter =
            fullname.charAt(0).toUpperCase();

        topAvatar.textContent = firstLetter;

        showMessage(
            "Profile photo removed successfully.",
            "success"
        );

    } catch (error) {

        console.error("Remove photo error:", error);

        showMessage(
            "Cannot connect to the backend server.",
            "error"
        );
    }
});


/* ================================
   PROFILE DROPDOWN
================================ */

profileAvatarButton.addEventListener("click", function (event) {

    event.stopPropagation();

    profileDropdown.classList.toggle("show");
});


document.addEventListener("click", function (event) {

    if (!profileDropdown.contains(event.target) &&
        !profileAvatarButton.contains(event.target)) {

        profileDropdown.classList.remove("show");
    }
});


/* ================================
   SETTINGS
================================ */

settingsButton.addEventListener("click", function (event) {

    event.preventDefault();

    alert("Admin Settings page will be added next.");

});


/* ================================
   ADMIN LOGOUT
================================ */

function adminLogout() {

    localStorage.removeItem("admin_id");
    localStorage.removeItem("admin_fullname");
    localStorage.removeItem("admin_email");

    window.location.href = "../../login.html";
}

sidebarLogout.addEventListener(
    "click",
    adminLogout
);

dropdownLogout.addEventListener(
    "click",
    adminLogout
);


/* ================================
   FORMAT DATE
================================ */

function formatDate(dateValue) {

    if (!dateValue) {
        return "-";
    }

    const date = new Date(dateValue);

    if (isNaN(date.getTime())) {
        return dateValue;
    }

    return date.toLocaleString();
}


/* ================================
   SHOW MESSAGE
================================ */

function showMessage(message, type) {

    messageBox.textContent = message;

    messageBox.className =
        "message-box " + type;

    setTimeout(function () {

        messageBox.textContent = "";
        messageBox.className = "message-box";

    }, 4000);
}


/* ================================
   START
================================ */

loadAdminProfile();
