
# Native Android Wrapper Scaffold

AI Workflow OS can export an Android wrapper scaffold for the local console.

This is not a signed APK yet. It is the safe intermediate layer:

- creates Gradle project files
- declares launcher activity
- uses local-first WebView entrypoint
- includes launcher icon vector
- declares no broad permissions
- stores no secrets or signing keys

A later build/sign stage may compile this scaffold into an installable APK.
