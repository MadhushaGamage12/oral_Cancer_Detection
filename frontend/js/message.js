// OralAI - Reusable Notification System

function showMessage(message, type = "success") {
    let container = document.getElementById("toastContainer");

    // Create the container if it doesn't exist
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container";
        container.setAttribute("aria-live", "polite");
        container.setAttribute("aria-atomic", "true");
        document.body.appendChild(container);
    }

    // Clear the previous message
    container.replaceChildren();

    const toast = document.createElement("div");
    toast.className = `toast-message ${
        type === "error" ? "error" : "success"
    }`;

    toast.textContent = message;
    container.appendChild(toast);

    // Automatically remove after 3 seconds
    setTimeout(() => {
        if (toast.parentElement === container) {
            toast.remove();
        }
    }, 3000);
}
