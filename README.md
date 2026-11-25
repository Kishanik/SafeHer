SAFEHER - LATEST STARTER PROJECT

Files:
- index.html
- style.css
- script.js
- firebase.json

IMPORTANT FIREBASE SETUP
1. Open Firebase Console -> Authentication -> Sign-in method.
2. Enable Email/Password AND enable the Email link (passwordless sign-in) option.
3. Open Authentication -> Settings -> Authorized domains.
4. Ensure localhost and safeher-22e02.web.app are authorized.
5. In Firebase Console -> Project settings -> Your apps, verify the web app configuration in script.js.

RUN LOCALLY
- Open a terminal in this folder.
- Run: firebase serve
  or: firebase emulators:start (only if you have configured emulators).
- A simple local web server is also acceptable. Do not open index.html directly as file:// for Firebase email-link sign-in.
- To deploy: firebase deploy --only hosting

SAFETY / LIMITATIONS
- SOS only prepares an SMS and opens the device messaging app. The user must review and send it.
- Call 112 directly in an emergency in India.
- Browser location requires permission and a secure context (HTTPS or localhost).
- Trusted contacts are stored in this browser's localStorage, not in Firebase or synced between devices.
- Police station results are community map listings and may be incomplete or outdated. Verify the station independently.
- This is a student prototype, not a monitored emergency service.

SECURITY
Firebase web configuration values identify the web app and are expected to be present in client code. Protect data with appropriate Firebase Security Rules if you later add Firestore or Storage. Never place service-account private keys or other server secrets in script.js.


⭐If you find this project interesting, consider giving the repository a star!

Developed as a hackathon project.
