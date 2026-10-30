# Yami Trades AI — private Android APK starter

This project packages your existing Streamlit dashboard inside a simple Android WebView app.

Dashboard: https://atlas-paper-trader-br8eapwmnjpkrz6wqnswew.streamlit.app/

## What this first APK does
- Opens the existing hosted dashboard inside an app named Yami Trades AI.
- Enables JavaScript and browser storage required by Streamlit.
- Keeps HTTPS navigation to the configured dashboard host inside the app.
- Opens external links in your phone browser.
- Supports back navigation and a loading bar.

## Limitations
This is an Android shell for the current cloud dashboard. It does not add live prices, AI predictions, broker connectivity, push notifications, or real order execution. It requires internet access and the Streamlit app to be available. The dashboard is still the paper-trading prototype.

This workflow produces a debug APK for personal testing, not a signed Play Store release. Never put broker API keys or passwords in this app or repository.

## Build from Android using GitHub Actions
1. Open your existing GitHub repository `atlas-paper-trader`.
2. Upload the contents of this ZIP into the repository root, keeping folder structure. Do not delete `app.py` or `requirements.txt`.
3. Commit the changes.
4. Open the repository's Actions tab.
5. Select **Build Yami Trades AI APK**.
6. Tap **Run workflow** if it has not started automatically.
7. Wait for a green check.
8. Open the completed run and find **Artifacts**.
9. Download `yami-trades-ai-debug-apk`, extract it, then tap `app-debug.apk` to install.
10. Android may ask you to allow installs from that source. Only enable it for the file you built from your own repository.

The workflow uses Java 17, Android SDK, Gradle 8.9, and Android Gradle Plugin 8.7.3.
