import { initializeApp } from "https://www.gstatic.com/firebasejs/12.6.0/firebase-app.js";

import {
  getAuth,
  sendSignInLinkToEmail,
  isSignInWithEmailLink,
  signInWithEmailLink,
  onAuthStateChanged,
  signOut,
  updateProfile
} from "https://www.gstatic.com/firebasejs/12.6.0/firebase-auth.js";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDR1vgJNiazU-c8vrOsaF9Tk86ZZtzsCvs",
  authDomain: "safeher-22e02.firebaseapp.com",
  projectId: "safeher-22e02",
  storageBucket: "safeher-22e02.firebasestorage.app",
  messagingSenderId: "231625787712",
  appId: "1:231625787712:web:5042fa10e3eab67d7012a5",
  measurementId: "G-YKB3L9CMHL"
};

const $ = (id) => document.getElementById(id);

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

let map = null;
let userMarker = null;
let stationLayer = null;
let currentLocation = null;

// Display messages
function showMessage(id, message) {
  const element = $(id);
  if (element) element.textContent = message;
}

// Switch between login and dashboard
function showScreen(loggedIn) {
  $("authScreen").hidden = loggedIn;
  $("app").hidden = !loggedIn;

  if (loggedIn) {
    setTimeout(() => {
      initializeMap();
      if (map) map.invalidateSize();
    }, 200);
  }
}

// Friendly Firebase errors
function friendlyAuthError(error) {
  const code = error?.code || "";

  if (code === "auth/quota-exceeded") {
    return "Daily login email limit reached. Please try again after the quota resets.";
  }

  if (code === "auth/unauthorized-continue-uri") {
    return "This website domain is not authorized in Firebase Authentication settings.";
  }

  if (code === "auth/operation-not-allowed") {
    return "Email link sign-in is not enabled. Enable Email/Password and Email link in Firebase Authentication.";
  }

  if (code === "auth/invalid-email") {
    return "Please enter a valid email address.";
  }

  return "Unable to send the login link: " +
    (error?.message || "Unknown error");
}

// Passwordless email login
const actionCodeSettings = {
  url: window.location.origin + window.location.pathname,
  handleCodeInApp: true
};

$("authForm").addEventListener("submit", async (event) => {
  event.preventDefault();

  const email = $("authEmail").value.trim();
  const name = $("authName").value.trim();
  const button = $("authSubmit");

  if (!email) {
    showMessage("authError", "Please enter your email address.");
    return;
  }

  button.disabled = true;
  button.textContent = "Sending login link...";

  try {
    await sendSignInLinkToEmail(
      auth,
      email,
      actionCodeSettings
    );

    localStorage.setItem("safeherPendingEmail", email);

    if (name) {
      localStorage.setItem("safeherPendingName", name);
    }

    showMessage(
      "authError",
      "Login link sent! Check your inbox and spam folder."
    );

    $("authForm").reset();

  } catch (error) {
    console.error("Email link error:", error);
    showMessage("authError", friendlyAuthError(error));

  } finally {
    button.disabled = false;
    button.textContent = "Send Secure Login Link";
  }
});

// Complete email login
async function completeEmailLogin() {
  if (!isSignInWithEmailLink(auth, window.location.href)) {
    return;
  }

  let email = localStorage.getItem("safeherPendingEmail");

  if (!email) {
    email = window.prompt(
      "Enter the email address where you received the login link:"
    );
  }

  if (!email) {
    showMessage(
      "authError",
      "Email address is required to complete login."
    );
    return;
  }

  try {
    const result = await signInWithEmailLink(
      auth,
      email.trim(),
      window.location.href
    );

    const savedName = localStorage.getItem("safeherPendingName");

    if (savedName && !result.user.displayName) {
      await updateProfile(result.user, {
        displayName: savedName
      });
    }

    localStorage.removeItem("safeherPendingEmail");
    localStorage.removeItem("safeherPendingName");

    window.history.replaceState(
      {},
      document.title,
      window.location.pathname
    );

  } catch (error) {
    console.error("Email sign-in completion error:", error);

    showMessage(
      "authError",
      "Login could not be completed: " +
      (error?.message || "Please request a new link.")
    );
  }
}

// Logout
$("logoutBtn").addEventListener("click", async () => {
  try {
    await signOut(auth);
  } catch (error) {
    alert("Could not log out. Please try again.");
  }
});

// Authentication state
onAuthStateChanged(auth, (user) => {
  if (user) {
    showScreen(true);

    showMessage(
      "welcomeUser",
      "Welcome, " + (user.displayName || user.email || "User")
    );

    renderContacts();

  } else {
    showScreen(false);
  }
});

// Trusted contacts
function getContacts() {
  try {
    const value = JSON.parse(
      localStorage.getItem("safeherContacts") || "[]"
    );

    return Array.isArray(value) ? value : [];

  } catch {
    return [];
  }
}

function saveContacts(contacts) {
  localStorage.setItem(
    "safeherContacts",
    JSON.stringify(contacts)
  );
}

function renderContacts() {
  const container = $("contactList");

  if (!container) return;

  container.replaceChildren();

  const contacts = getContacts();

  if (!contacts.length) {
    const empty = document.createElement("p");
    empty.className = "muted small";
    empty.textContent = "No trusted contacts added yet.";

    container.appendChild(empty);
    return;
  }

  contacts.forEach((contact, index) => {
    const card = document.createElement("div");
    card.className = "contact-card";

    const info = document.createElement("div");
    info.className = "contact-info";

    const name = document.createElement("strong");
    name.textContent = contact.name;

    const phone = document.createElement("p");
    phone.textContent = contact.phone;

    info.append(name, phone);

    const call = document.createElement("a");
    call.href = "tel:" + contact.phone.replace(/[^\d+]/g, "");
    call.textContent = "Call";

    const sms = document.createElement("a");
    sms.href = "sms:" + contact.phone.replace(/[^\d+]/g, "");
    sms.textContent = "SMS";

    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "remove-btn";
    remove.textContent = "Remove";

    remove.addEventListener("click", () => {
      const latest = getContacts();
      latest.splice(index, 1);

      saveContacts(latest);
      renderContacts();
    });

    card.append(info, call, sms, remove);
    container.appendChild(card);
  });
}

// Add trusted contact
$("contactForm").addEventListener("submit", (event) => {
  event.preventDefault();

  const name = $("contactName").value.trim();
  const phone = $("contactPhone").value.trim();

  if (!name || !phone) return;

  if (!/^[+\d][\d\s()+-]{5,18}$/.test(phone)) {
    alert("Please enter a valid phone number.");
    return;
  }

  const contacts = getContacts();

  contacts.push({ name, phone });

  saveContacts(contacts);

  $("contactForm").reset();

  renderContacts();
});

renderContacts();

// Get current location
function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(
        new Error("Location is not supported by this browser.")
      );
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => resolve({
        lat: position.coords.latitude,
        lng: position.coords.longitude
      }),

      reject,

      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 30000
      }
    );
  });
}

// Initialize map
function initializeMap() {
  if (map || !window.L || !$("map")) return;

  map = L.map("map").setView(
    [11.0168, 76.9558],
    12
  );

  L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 19
    }
  ).addTo(map);

  stationLayer = L.layerGroup().addTo(map);
}

// Display user location
function displayLocationOnMap(location) {
  initializeMap();

  if (!map) return;

  const point = [location.lat, location.lng];

  map.setView(point, 14);

  if (userMarker) {
    userMarker.remove();
  }

  userMarker = L.marker(point)
    .addTo(map)
    .bindPopup("Your current location");

  userMarker.openPopup();
}

// Update current location
async function updateLocation() {
  const location = await getCurrentLocation();

  currentLocation = location;

  displayLocationOnMap(location);

  showMessage(
    "locationStatus",
    "Location found: " +
    location.lat.toFixed(5) +
    ", " +
    location.lng.toFixed(5)
  );

  const link = $("mapLink");

  link.href =
    "https://www.google.com/maps?q=" +
    location.lat +
    "," +
    location.lng;

  link.hidden = false;

  return location;
}

// Location button
$("locationBtn").addEventListener("click", async () => {
  showMessage(
    "locationStatus",
    "Requesting your location..."
  );

  try {
    await updateLocation();

  } catch (error) {
    console.warn("Location error:", error);

    showMessage(
      "locationStatus",
      "Unable to get location. Allow location access and use HTTPS or localhost."
    );
  }
});

// Calculate distance
function calculateDistance(lat1, lon1, lat2, lon2) {
  const radians = (value) => value * Math.PI / 180;

  const earthRadius = 6371;

  const dLat = radians(lat2 - lat1);
  const dLon = radians(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(radians(lat1)) *
    Math.cos(radians(lat2)) *
    Math.sin(dLon / 2) ** 2;

  return earthRadius *
    2 *
    Math.atan2(
      Math.sqrt(a),
      Math.sqrt(1 - a)
    );
}

// Nearby police stations with multiple servers
$("policeBtn").addEventListener("click", async () => {
  const output = $("policeList");
  const button = $("policeBtn");

  output.textContent =
    "Searching nearby police stations...";

  button.disabled = true;

  const servers = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter"
  ];

  try {
    const location =
      currentLocation || await updateLocation();

    const query = `
      [out:json][timeout:25];
      (
        node["amenity"="police"](around:10000,${location.lat},${location.lng});
        way["amenity"="police"](around:10000,${location.lat},${location.lng});
        relation["amenity"="police"](around:10000,${location.lat},${location.lng});
      );
      out center tags;
    `;

    let data = null;
    let lastError = null;

    for (const server of servers) {
      try {
        const controller = new AbortController();

        const timeout = setTimeout(
          () => controller.abort(),
          30000
        );

        try {
          const response = await fetch(server, {
            method: "POST",

            headers: {
              "Content-Type": "text/plain;charset=UTF-8"
            },

            body: query,
            signal: controller.signal
          });

          if (!response.ok) {
            throw new Error(
              "Server returned HTTP " + response.status
            );
          }

          const result = await response.json();

          if (!Array.isArray(result.elements)) {
            throw new Error("Invalid map data received.");
          }

          data = result;
          break;

        } finally {
          clearTimeout(timeout);
        }

      } catch (error) {
        console.warn(
          "Overpass server failed:",
          server,
          error
        );

        lastError = error;
      }
    }

    if (!data) {
      throw lastError ||
        new Error("All map servers are unavailable.");
    }

    const stations = (data.elements || [])
      .map((item) => {
        const lat = item.lat ?? item.center?.lat;
        const lng = item.lon ?? item.center?.lon;

        if (
          typeof lat !== "number" ||
          typeof lng !== "number"
        ) {
          return null;
        }

        return {
          name:
            item.tags?.name ||
            "Police Station (unnamed listing)",

          lat,
          lng,

          distance: calculateDistance(
            location.lat,
            location.lng,
            lat,
            lng
          )
        };
      })

      .filter(Boolean)

      .sort((a, b) =>
        a.distance - b.distance
      )

      .slice(0, 10);

    output.replaceChildren();

    if (stationLayer) {
      stationLayer.clearLayers();
    }

    if (!stations.length) {
      output.textContent =
        "No police stations found in available OpenStreetMap data. Please check Google Maps or official local listings too.";

      return;
    }

    stations.forEach((station) => {
      const card = document.createElement("div");
      card.className = "police-card";

      const details = document.createElement("div");

      const title = document.createElement("strong");
      title.textContent = station.name;

      const distance = document.createElement("p");

      distance.textContent =
        station.distance.toFixed(2) +
        " km straight-line distance";

      details.append(title, distance);

      const directions = document.createElement("a");

      directions.href =
        "https://www.google.com/maps/dir/?api=1" +
        "&origin=" + location.lat + "," + location.lng +
        "&destination=" + station.lat + "," + station.lng;

      directions.target = "_blank";
      directions.rel = "noopener noreferrer";
      directions.textContent = "Directions";

      card.append(details, directions);

      output.appendChild(card);

      if (stationLayer) {
        L.marker([station.lat, station.lng])
          .addTo(stationLayer)
          .bindPopup(station.name);
      }
    });

    if (map && stationLayer) {
      const markers = [
        userMarker,
        ...stationLayer.getLayers()
      ].filter(Boolean);

      if (markers.length) {
        map.fitBounds(
          L.featureGroup(markers)
            .getBounds()
            .pad(0.15)
        );
      }
    }

  } catch (error) {
    console.error(
      "Police station search error:",
      error
    );

    output.textContent =
      "Police listings are temporarily unavailable. Please try again or check Google Maps.";
  } finally {
    button.disabled = false;
  }
});

// SOS message preparation
$("sosBtn").addEventListener("click", async () => {
  const contacts = getContacts();

  if (!contacts.length) {
    alert("Please add a trusted contact first.");
    return;
  }

  const confirmed = window.confirm(
    "Prepare an SOS message for " +
    contacts[0].name +
    "? Your messaging app will open; review the message and send it yourself."
  );

  if (!confirmed) return;

  let locationText =
    "My location is unavailable.";

  try {
    const location =
      currentLocation || await updateLocation();

    locationText =
      "My location: https://www.google.com/maps?q=" +
      location.lat +
      "," +
      location.lng;

  } catch {
    // Message can still be prepared without location.
  }

  const message =
    "SAFEHER ALERT: I may need help. " +
    locationText;

  const phone =
    contacts[0].phone.replace(/[^\d+]/g, "");

  window.location.href =
    "sms:" +
    phone +
    "?body=" +
    encodeURIComponent(message);
});

// Browser notifications
$("notificationBtn").addEventListener("click", async () => {
  if (!("Notification" in window)) {
    alert(
      "Notifications are not supported in this browser."
    );

    return;
  }

  try {
    const permission =
      await Notification.requestPermission();

    if (permission === "granted") {
      new Notification("SafeHer", {
        body:
          "Browser notifications are enabled on this device."
      });

    } else {
      alert(
        "Notification permission was not granted."
      );
    }

  } catch (error) {
    alert(
      "Could not enable notifications in this browser."
    );
  }
});

// Complete email login
await completeEmailLogin();
