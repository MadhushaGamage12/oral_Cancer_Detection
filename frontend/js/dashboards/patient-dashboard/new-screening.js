document.addEventListener("DOMContentLoaded", function () {


    // =====================================================
    // GET HTML ELEMENTS
    // =====================================================

    const imageInput =
        document.getElementById("imageInput");


    const previewImage =
        document.getElementById("previewImage");


    const previewText =
        document.getElementById("previewText");


    const screeningBtn =
        document.getElementById("screeningBtn");


    // =====================================================
    // CHECK USER LOGIN
    // =====================================================

    const userId =
        localStorage.getItem("user_id");


    if (!userId) {

        window.location.href =
            "../../login.html";

        return;
    }



    // =====================================================
    // IMAGE PREVIEW
    // =====================================================

    imageInput.addEventListener(
        "change",
        function () {


            const file =
                this.files[0];


            if (file) {


                const reader =
                    new FileReader();


                reader.onload =
                    function (event) {


                        previewImage.src =
                            event.target.result;


                        previewImage.style.display =
                            "block";


                        previewText.style.display =
                            "none";

                    };


                reader.readAsDataURL(file);

            }

        }
    );



    // =====================================================
    // START SCREENING
    // =====================================================

    screeningBtn.addEventListener(
        "click",
        async function () {


            // =================================================
            // GET SELECTED IMAGE
            // =================================================

            const image =
                imageInput.files[0];



            // =================================================
            // GET CLINICAL INFORMATION
            // =================================================

            const age =
                document.getElementById("age").value;


            const tobacco =
                document.getElementById("tobacco").value;


            const alcohol =
                document.getElementById("alcohol").value;


            const lesionDuration =
                document.getElementById(
                    "lesionDuration"
                ).value;


            const previousLesion =
                document.getElementById(
                    "previousLesion"
                ).value;



            // =================================================
            // VALIDATE IMAGE
            // =================================================

            if (!image) {

                alert(
                    "Please upload an oral image."
                );

                return;
            }



            // =================================================
            // VALIDATE CLINICAL INFORMATION
            // =================================================

            if (
                !age ||
                !tobacco ||
                !alcohol ||
                !lesionDuration ||
                !previousLesion
            ) {

                alert(
                    "Please complete all screening information."
                );

                return;
            }



            // =================================================
            // CREATE FORMDATA
            // =================================================

            const formData =
                new FormData();



            // =================================================
            // ADD USER ID
            // =================================================

            formData.append(
                "user_id",
                userId
            );



            // =================================================
            // ADD IMAGE
            // =================================================

            formData.append(
                "image",
                image
            );



            // =================================================
            // ADD CLINICAL INFORMATION
            // =================================================

            formData.append(
                "age",
                age
            );


            formData.append(
                "tobacco",
                tobacco
            );


            formData.append(
                "alcohol",
                alcohol
            );


            formData.append(
                "lesionDuration",
                lesionDuration
            );


            formData.append(
                "previousLesion",
                previousLesion
            );



            // =================================================
            // DISABLE BUTTON
            // =================================================

            screeningBtn.disabled = true;


            screeningBtn.textContent =
                "Uploading...";



            // =================================================
            // SEND SCREENING TO BACKEND
            // =================================================

            try {


                const response =
                    await fetch(
                        "http://127.0.0.1:5000/screenings",
                        {
                            method: "POST",
                            body: formData
                        }
                    );



                // =================================================
                // READ BACKEND RESPONSE
                // =================================================

                const data =
                    await response.json();


                console.log(
                    "Screening response:",
                    data
                );



                // =================================================
                // CHECK SCREENING CREATION
                // =================================================

                if (
                    response.ok &&
                    data.success
                ) {


                    // -------------------------------------------------
                    // GET SCREENING ID
                    // -------------------------------------------------

                    const screeningId =
                        data.screening_id;


                    console.log(
                        "Created Screening ID:",
                        screeningId
                    );



                    // -------------------------------------------------
                    // SAVE SCREENING ID
                    // -------------------------------------------------

                    localStorage.setItem(
                        "screening_id",
                        screeningId
                    );



                    // =================================================
                    // STEP 2 - RUN AI PREDICTION
                    // =================================================

                    screeningBtn.textContent =
                        "Analysing Image...";


                    console.log(
                        "Starting AI prediction..."
                    );



                    const predictionResponse =
                        await fetch(
                            `http://127.0.0.1:5000/screenings/${screeningId}/predict`,
                            {
                                method: "POST"
                            }
                        );



                    // =================================================
                    // READ AI RESPONSE
                    // =================================================

                    const predictionData =
                        await predictionResponse.json();


                    console.log(
                        "AI Prediction response:",
                        predictionData
                    );



                    // =================================================
                    // CHECK AI PREDICTION
                    // =================================================

                    if (
                        predictionResponse.ok &&
                        predictionData.success
                    ) {


                        console.log(
                            "AI prediction completed successfully."
                        );



                        // =================================================
                        // SAVE SCREENING ID AGAIN
                        // =================================================

                        localStorage.setItem(
                            "screening_id",
                            screeningId
                        );



                        // =================================================
                        // SHOW SUCCESS MESSAGE
                        // =================================================

                        alert(
                            "Screening completed successfully!"
                        );



                        // =================================================
                        // OPEN SCREENING RESULT PAGE
                        // =================================================

                        window.location.href =
                            `screening-result.html?id=${screeningId}`;


                    }

                    else {


                        // =================================================
                        // AI PREDICTION ERROR
                        // =================================================

                        console.error(
                            "AI prediction failed:",
                            predictionData
                        );


                        alert(
                            predictionData.message ||
                            "AI prediction failed."
                        );

                    }


                }

                else {


                    // =================================================
                    // SCREENING CREATION ERROR
                    // =================================================

                    console.error(
                        "Screening creation failed:",
                        data
                    );


                    alert(
                        data.message ||
                        "Failed to create screening."
                    );

                }


            }

            catch (error) {


                // =================================================
                // NETWORK / SERVER ERROR
                // =================================================

                console.error(
                    "Screening error:",
                    error
                );


                alert(
                    "Unable to connect to the Flask server."
                );


            }


            finally {


                // =================================================
                // ENABLE BUTTON AGAIN
                // =================================================

                screeningBtn.disabled = false;


                screeningBtn.textContent =
                    "Start Screening";

            }

        }
    );



    // =========================================================
    // ACCOUNT MENU
    // =========================================================

    setupAccountMenu(userId);

});



/* =========================================================
   ACCOUNT MENU
========================================================= */

function setupAccountMenu(userId) {


    const userMenuButton =
        document.getElementById(
            "userMenuButton"
        );


    const userDropdown =
        document.getElementById(
            "userDropdown"
        );


    const logoutLink =
        document.getElementById(
            "logoutLink"
        );


    const userAvatarImage =
        document.getElementById(
            "userAvatarImage"
        );


    const userAvatarInitial =
        document.getElementById(
            "userAvatarInitial"
        );



    // =====================================================
    // LOAD USER PROFILE
    // =====================================================

    loadUserProfile(
        userId,
        userAvatarImage,
        userAvatarInitial
    );



    // =====================================================
    // OPEN / CLOSE DROPDOWN
    // =====================================================

    if (
        userMenuButton &&
        userDropdown
    ) {


        userMenuButton.addEventListener(
            "click",
            function (event) {


                event.stopPropagation();


                const isOpen =
                    userDropdown.classList.toggle(
                        "show"
                    );


                userMenuButton.setAttribute(
                    "aria-expanded",
                    isOpen ? "true" : "false"
                );

            }
        );



        // =================================================
        // CLOSE WHEN CLICKING OUTSIDE
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
        // CLOSE WHEN PRESSING ESC
        // =================================================

        document.addEventListener(
            "keydown",
            function (event) {


                if (
                    event.key === "Escape"
                ) {


                    userDropdown.classList.remove(
                        "show"
                    );


                    userMenuButton.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }
        );

    }



    // =====================================================
    // LOGOUT
    // =====================================================

    if (logoutLink) {


        logoutLink.addEventListener(
            "click",
            function (event) {


                event.preventDefault();


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
                    "screening_id"
                );


                window.location.href =
                    "../../login.html";

            }
        );

    }

}



/* =========================================================
   LOAD USER PROFILE
========================================================= */

async function loadUserProfile(
    userId,
    userAvatarImage,
    userAvatarInitial
) {


    try {


        const response =
            await fetch(
                `http://127.0.0.1:5000/users/${userId}`
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {


            console.error(
                "Unable to load user profile."
            );


            showUserInitial(
                userAvatarInitial,
                userAvatarImage,
                "P"
            );


            return;

        }


        const user =
            data.user;



        // =====================================================
        // SAVE USER INFORMATION
        // =====================================================

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



        // =====================================================
        // GET INITIAL
        // =====================================================

        let initial = "P";


        if (user.fullname) {


            const cleanName =
                user.fullname.trim();


            if (cleanName.length > 0) {

                initial =
                    cleanName
                        .charAt(0)
                        .toUpperCase();

            }

        }



        // =====================================================
        // SHOW PROFILE PHOTO
        // =====================================================

        if (
            user.profile_photo_url &&
            userAvatarImage
        ) {


            userAvatarImage.src =
                `http://127.0.0.1:5000${user.profile_photo_url}?t=${Date.now()}`;


            userAvatarImage.style.display =
                "block";


            if (userAvatarInitial) {

                userAvatarInitial.style.display =
                    "none";

            }



            // =================================================
            // IF PHOTO FAILS
            // =================================================

            userAvatarImage.onerror =
                function () {


                    showUserInitial(
                        userAvatarInitial,
                        userAvatarImage,
                        initial
                    );

                };

        }

        else {


            // =================================================
            // NO PROFILE PHOTO
            // =================================================

            showUserInitial(
                userAvatarInitial,
                userAvatarImage,
                initial
            );

        }


    }

    catch (error) {


        console.error(
            "Error loading user profile:",
            error
        );


        showUserInitial(
            userAvatarInitial,
            userAvatarImage,
            "P"
        );

    }

}



/* =========================================================
   SHOW USER INITIAL
========================================================= */

function showUserInitial(
    userAvatarInitial,
    userAvatarImage,
    initial
) {


    if (userAvatarImage) {

        userAvatarImage.style.display =
            "none";

    }


    if (userAvatarInitial) {

        userAvatarInitial.textContent =
            initial;


        userAvatarInitial.style.display =
            "flex";

    }

}
