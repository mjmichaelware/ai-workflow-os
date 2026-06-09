# GitHub Actions APK Build

The Android debug APK is built on a Linux GitHub Actions runner instead of Android ARM64 Termux.

## Why

Termux can run local Java, Gradle, d8, zipalign, apksigner, and native aapt/aapt2 packages, but the tested on-device resource packaging paths could not load a compatible Android framework include on this phone. The official Android resource packaging path expects Android SDK Build Tools AAPT2, which is a host build tool.

## Workflow

`.github/workflows/android-debug-apk.yml`

The workflow:

1. Checks out the repository.
2. Sets up JDK 17.
3. Installs Android command-line tools under the runner workspace.
4. Installs platform-tools, platform android-36, and build-tools 36.0.0.
5. Runs `scripts/prove_real_apk_build.py`.
6. Uploads `AI-Workflow-OS-debug.apk` as a workflow artifact when the build succeeds.

## Secrets

No signing secrets are required for the debug APK artifact. Production signing remains outside the repository.
