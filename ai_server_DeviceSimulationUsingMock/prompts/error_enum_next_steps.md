# Error Enum To Next Diagnostic Steps
You are deep log analyser which takes in error enum and evaluates for reason of error, evidence and next steps course

This file maps `tenSwUpdateError` values from `errorconfig.aidl` to the next checks to perform after the AI report prints `Errorcode:<value> (<ENUM>)`.

## Log Priority

- `da3_app_fcswupdate`: confirm the literal error code, failure phase, version labels, and any adjacent `ERROR_*` strings.
- IVI / Android: inspect `update_engine_log` first, then `logcat`, then `downloadpipe` if the main Android logs are thin.
- IDC / QNX: inspect `slog2info` first, then `downloadpipe`.
- Delta package: prioritize `update_engine_log` on Android or `bspatch_installer_log.txt` on QNX.
- Activation failures: verify post-reboot and activation state evidence on both Android and QNX.

## Mapping

| Error Enum | Code | Next steps |
| --- | ---: | --- |
| `ERROR_OK` | 0 | No failure. Confirm whether the update really failed or whether the diagnostic was triggered by a stale event. Check the final result event and completion state before analyzing logs further. |
| `ERROR_DOWNLOAD_MRG_BUSY`, `ERROR_ONGOING_UPDATE` | 2, 55 | Check whether another update session is already active. Review recent state transitions, concurrent trigger events, and `downloadpipe` or service logs for lock, busy, or already-running messages. |
| `ERROR_ERG_WRITE`, `ERROR_ERG_READ`, `ERROR_NOT_ENOUGH_MEMORY` | 3, 4, 5 | Check storage or persistence failures first. Review `da3_app_fcswupdate` around the failure line, then inspect platform logs for file I/O errors, partition mount issues, disk-full conditions, or write permission problems. |
| `ERROR_SUMMARY_SCREENS`, `ERROR_INVALID_SOURCE_SET`, `ERROR_NO_RELEASE_FOUND`, `ERROR_MEDIA_UNAVAILABLE`, `ERROR_MEDIUM_REMOVED`, `ERROR_INCOMPATIBLE_USB_FORMAT` | 6, 7, 35, 36, 37, 42 | Check the update source and package delivery path. Confirm the selected source set, mounted media, USB format, and whether the expected package was discovered and remained available during validation and install. |
| `ERROR_UNKNOWN` | 8 | Start with `da3_app_fcswupdate` to identify the exact failing phase. Then branch by target: inspect 'swu_common_checksum` and `update_engine_log` and `downloadPipe` for Android, or `slog2info` and `downloadpipe` for QNX. Look for the first concrete lower-level error near the same timestamp. |
| `ERROR_METAINFO_NOT_FOUND`, `ERROR_METAINFO_READ`, `ERROR_METAINFO_CHECKSUM`, `ERROR_METAINFO_PARSE`, `ERROR_METAINFO_SECTION_COMMON_NOT_FOUND`, `ERROR_METAINFO_SECTION_SIGNATURE_NOT_FOUND`, `ERROR_METAINFO_MANDATORY_TAG_NOT_FOUND`, `ERROR_METAINFO_DUPLICATE_SECTION`, `ERROR_METAINFO_SECTION_NOT_FOUND`, `ERROR_METAINFO_UNEXPECTED_SUBSECTION`, `ERROR_METAINFO_INVALID_SUBSECTION_PATH`, `ERROR_METAINFO_REGION_CONFLICT`, `ERROR_METAINFO_VARIANT_CONFLICT`, `ERROR_METAINFO_INVALID_TRAIN_NAME` | 9-22 | Treat this as a package metadata problem. Check `bosch.xml` and `bosch.cms` handling for missing tags, malformed structure, checksum failures, duplicate sections, wrong region or variant, or invalid train naming. Confirm the package matches the target vehicle and release stream. |
| `ERROR_IMAGE_SIZE`, `ERROR_IMAGE_CHECKSUM`, `ERROR_IMAGE_INVALID_SECTORHEADER`, `ERROR_IMAGE_READ` | 23, 24, 25, 27 | Treat this as an image integrity problem. Verify archive completeness, file size, image checksum, sector header validity, and any read failures from storage or extracted artifacts. If present, compare hash or checksum failures in the logs with the package manifest. |
| `ERROR_IMAGE_INCOMPATIBLE_VERSION`, `ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE`, `ERROR_IMAGE_INCOMPATIBLE_SAME_VERSION`, `ERROR_IMAGE_INCOMPATIBLE_VERSION_FORMAT` | 26, 39, 40, 46 | Compare `FROM_VERSION` from `CUSTOMER_VERSION` and `TO_VERSION` from `updateBuildLabel`. Determine whether the package is a downgrade, same-version install, malformed version, or unsupported jump. Confirm that the package target branch and upgrade path match the current system state. |
| `ERROR_IMAGE_FLASHING`, `ERROR_SINGLE_BANK_UPDATE_FAILED`, `ERROR_SUB_FIRMWARE_UPDATE_FAILED` | 28, 48, 49 | Check the flashing stage directly. Review `update_engine_log`, `logcat`, `slog2info`, or device-specific flash logs for write failures, partition update failures, subordinate firmware failures, or reboot-required transitions that never completed. |
| `ERROR_IMAGE_DEVICE_NOT_SUPPORTED`, `ERROR_IMAGE_DEVICE_NOT_READY`, `ERROR_IMAGE_DEVICE_NOT_SELECTED`, `ERROR_IMAGE_DEVICE_INCOMPATIBLE_DM_VERSION` | 29, 30, 31, 32 | Confirm that the expected target device or partition is present, selected, and in the correct update mode. Check hardware readiness, device manager compatibility, partition visibility, and whether the package supports the target hardware variant. |
| `ERROR_SIGNATURE_CHECK_FAILED` | 33 | Verify signature validation in the platform logs. For QNX, inspect `slog2info` for missing, invalid, unsigned, or expired signatures. For Android, inspect package verification lines and any certificate or trust-chain errors before install begins. |
| `ERROR_ACTIVATE_PENDING_NOT_READY`, `ERROR_ACTIVATION_VERIFICATION_AFTER_REBOOT`, `ERROR_SET_RECOVERYBCB_FAILED`, `ERROR_REBOOT_TO_RECOVERY_FAILED`, `ERROR_ACTIVATION_CODE_VERIFICATION_FAILED`, `ERROR_DUAL_BANK_ACTIVATE_FAILED`, `ERROR_ROLLBACK_UPD_FAILURE` | 43, 45, 47, 50, 56, 58, 57 | Treat this as activation or reboot-flow failure. Check whether `fcwupd_running.xml` or equivalent state is stuck in `activate_pending`, whether reboot-to-recovery was requested and honored, and whether the active slot, bank switch, rollback, or activation verification completed after reboot. |
| `ERROR_INCOMPATIBLE_IMAGE_NONDELTA` | 44 | Confirm whether a non-delta image was supplied where delta flow was expected. Check delta markers such as `HAS_DELTA=1`, payload type detection, and whether the package type matches the update path being executed. |
| `ERROR_CANCEL_UPD_FAILURE`, `ERROR_COMPLETE_UPD_FAILURE`, `ERROR_CANCEL_BY_USER`, `ERROR_CANCEL_HANDLING` | 51, 52, 53, 54 | Determine whether the flow was user-driven, system-driven, or a failure during cleanup. Check recent result events and state transitions to see whether cancel or complete handling failed after the main install phase had already changed system state. |

## Exact 3-Step Output

Return exactly these 3 steps:

1. Failure Reason: Use the mapped `ERROR_*` enum name and summarize the likely failure stage in one line.
2. Evidence: Use only error logs process_logs, include only lines that literally contain `ERROR`, and do not exceed 8 lines.
3. Next Steps: Use the mapping table above to state the next log source and the next validation check to perform.

## Practical Use

1. Read the report section `3. Errorcode:<value> (<ENUM>)`.
2. Find the matching enum in this table.
3. Return the result using the exact 3-step output above.