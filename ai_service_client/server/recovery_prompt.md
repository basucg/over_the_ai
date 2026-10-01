# Recovery Plan Classification

Classify the resolved SW update failure into a recovery action.

Inputs:
- Error Number: includes the numeric error code and resolved enum when available.
- Evidence: only `[ERROR]` lines from the relevant logs.
- Package Type: package type extracted from the main diagnostic report.
- Version Information: `FROM_VERSION` and `TO_VERSION` extracted from the main diagnostic report.

Allowed recovery actions:
- `NO_ACTION`
- `MEMORY_RECOVERY`
- `RETRY_UPDATE`
- `REGENERATE_PACKAGE`
- `ROLLBACK`
- `SINGLE_BANK_ROLLBACK`
- `MANUAL_INTERVENTION`
- `CLASSIFY_ERROR`

Classification rules:
- Metadata, image validation, signature, version, release, or package corruption issues -> `REGENERATE_PACKAGE`
- Flashing, recovery boot, sub-firmware, or medium removal issues -> `RETRY_UPDATE`
- Activation or bank-switch verification failures -> `ROLLBACK`
- Unsupported device, configuration, region, train, or hardware compatibility issues -> `MANUAL_INTERVENTION`
- Memory shortage -> `MEMORY_RECOVERY`
- User cancel, ongoing update, busy, or benign status -> `NO_ACTION`
- Unknown error or insufficient evidence -> `CLASSIFY_ERROR`

Output format:
- Return exactly 2 lines.
- Line 1: `error_code: <original error number and enum when available>`
- Line 2: `recovery_action: <one allowed recovery action>`
- Do not add explanation or extra text.
