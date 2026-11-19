const sosBtn = document.getElementById("sosBtn");
const message = document.getElementById("message");
const languageBtn = document.getElementById("languageBtn");

let tamil = false;

sosBtn.addEventListener("click", () => {
    const confirmSOS = confirm(
        "DEMO ONLY: Simulate an emergency alert?"
    );

    if (confirmSOS) {
        message.textContent =
            "Demo alert activated. No real alert was sent.";
    }
});

function shareLocation() {
    if (!navigator.geolocation) {
        message.textContent = "Location is not supported.";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            message.textContent =
                `Location: ${lat.toFixed(4)}, ${lon.toFixed(4)}`;
        },
        () => {
            message.textContent =
                "Location unavailable. Check permission.";
        }
    );
}

function showAssistant() {
    message.textContent =
        "AI Assistant: Move to a public place and contact someone you trust. In India, call 112 for emergencies.";
}

function showContacts() {
    message.textContent =
        "Trusted contacts feature will be added soon.";
}

languageBtn.addEventListener("click", () => {
    tamil = !tamil;

    document.getElementById("heading").textContent =
        tamil ? "உங்கள் பாதுகாப்பு எங்கள் முன்னுரிமை" :
        "Your Safety, Our Priority";

    document.getElementById("description").textContent =
        tamil ? "விழிப்புடன் இருங்கள். பாதுகாப்பாக இருங்கள்." :
        "Stay aware. Stay connected. Stay safe.";

    languageBtn.textContent = tamil ? "English" : "தமிழ்";
});
