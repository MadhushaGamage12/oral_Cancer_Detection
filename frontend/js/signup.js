document.getElementById("signupForm").addEventListener("submit", function (e) {

    e.preventDefault();

    const userData = {

        fullname: document.getElementById("fullname").value,

        email: document.getElementById("email").value,

        password: document.getElementById("password").value

    };

    fetch("http://127.0.0.1:5000/signup", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(userData)

    })

        .then(response => response.json())

        .then(data => {

           showToast(data.message,"success");

            if (data.message === "User registered successfully!") {

                document.getElementById("signupForm").reset();

            }

        })

        .catch(error => {

            console.log(error);

            showToast("Connection Error","error");

        });

});