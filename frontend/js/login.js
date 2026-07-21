document.getElementById("loginForm").addEventListener("submit", function (e) {

    e.preventDefault();

    const loginData = {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    fetch("http://127.0.0.1:5000/login", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(loginData)

    })

    .then(response => response.json())

    .then(data => {

        if(data.success){

    showToast(data.message,"success");

    setTimeout(()=>{

        window.location.href="dashboard.html";

    },1500);

}else{

    showToast(data.message,"error");

}

    })

    .catch(error => {

        console.error(error);

        showToast("Connection Error","error");
    });

});