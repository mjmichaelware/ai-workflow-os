# App Factory Contract Standard

The app factory endpoint must create material files.

## Contract

/api/operator/run must return:

- ok
- created_apps
- compile result
- test result
- repo_scoped true
- raw_shell false
- keys_printed false

A successful build with no generated app is a failure.
