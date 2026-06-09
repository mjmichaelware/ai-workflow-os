# Final Release Hardening v1 Standard

## Rules

- Final release must compile all Python modules.
- Final release must pass pytest.
- Final release must pass workflow verification.
- Final release must pass public surface verification.
- Final release must not print secrets.
- Final release must not request broad permissions.
- Final release must leave the repo clean after proof artifacts are removed or committed.
- Final release must create a release report and tag.
