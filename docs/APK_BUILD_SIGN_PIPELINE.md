# APK Build and Sign Pipeline Scaffold

AI Workflow OS now includes an APK build/sign pipeline scaffold.

The scaffold creates scripts for:

- building a release APK from a wrapper project
- signing an unsigned APK with `apksigner`
- verifying a signed APK

The scaffold does not store keystores, passwords, aliases, tokens, or signing material in the repository.

## Signing environment contract

The signing scripts expect these variables to exist outside the repository:

- `AIWOS_ANDROID_KEYSTORE`
- `AIWOS_ANDROID_KEY_ALIAS`
- `AIWOS_ANDROID_KEYSTORE_PASSWORD`
- `AIWOS_ANDROID_KEY_PASSWORD`

The proof reports presence only. It does not print values.
