importScripts("https://www.gstatic.com/firebasejs/12.6.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/12.6.0/firebase-messaging-compat.js");

firebase.initializeApp({
  // Copy the same Firebase config values from your script.js
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  const title = payload.notification?.title || "SafeHer360";
  const options = {
    body: payload.notification?.body || "You have a new notification.",
    icon: "/favicon.ico"
  };

  self.registration.showNotification(title, options);
});
