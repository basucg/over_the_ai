TASK:
Classify a resolved SW update failure and generate exactly four output lines.

INPUTS:
- Error Number
- Failure Reason
- Evidence
- Package Type
- FROM_VERSION
- TO_VERSION

INPUT VALIDATION:
- Missing values become:
  - Version -> N/A
  - Package Type -> UNKNOWN
- Never invent values.
- If insufficient evidence exists, classify as ERROR_UNKNOWN and CLASSIFY_ERROR.



CLASSIFICATION PROCESS:

Step 1:
Determine final error_code.

Rules:
- If a known ERROR_* code is provided and is not ERROR_UNKNOWN, retain it.
- Only classify when input error equals ERROR_UNKNOWN.
- Use Failure Reason first.
- Use Evidence as tie-breaker.
- Use Package Type and Version Information as supporting signals.

Priority order:
1. Version-related errors
2. Package/metadata/signature/checksum errors
3. Activation errors
4. Device compatibility errors
5. Retryable flashing errors
6. Memory errors
7. Benign status errors

STEP 2: MAP final error_code TO recovery_action

CRITICAL RULE:
recovery_action MUST be determined exclusively by the Primary classification map.

RULES:

Use the FINAL error_code produced in Step 1 as the lookup key.

Find that error_code in the Primary classification map.

Return the recovery_action assigned to that error_code EXACTLY as written.

Do NOT infer recovery_action from:

detailed_recovery_plan

Failure Reason

Evidence

Package Type

FROM_VERSION

TO_VERSION

service_request

action_item

Do NOT modify, shorten, rename, or paraphrase the mapped recovery_action.

If an error_code has a specific mapping in the Primary classification map, that mapping ALWAYS takes precedence over any generic recovery-action rule.

ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE MUST ALWAYS map to:
REGENERATE_PACKAGE AND RETRY UPDATE

Even though the detailed_recovery_plan for ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE says to search for a compatible version and retry the update, the recovery_action MUST remain:
REGENERATE_PACKAGE AND RETRY UPDATE

detailed_recovery_plan and recovery_action are independent fields. Never derive one from the wording of the other.

PRIMARY CLASSIFICATION MAP:

NO_ACTION:
ERROR_DOWNLOAD_MRG_BUSY
ERROR_ERG_WRITE
ERROR_ERG_READ
ERROR_SUMMARY_SCREENS
ERROR_ACTIVATE_PENDING_NOT_READY
ERROR_CANCEL_UPD_FAILURE
ERROR_COMPLETE_UPD_FAILURE
ERROR_CANCEL_BY_USER
ERROR_CANCEL_HANDLING
ERROR_ONGOING_UPDATE

MEMORY_RECOVERY:
ERROR_NOT_ENOUGH_MEMORY

RETRY_UPDATE:
ERROR_INVALID_SOURCE_SET
ERROR_IMAGE_FLASHING
ERROR_MEDIUM_REMOVED
ERROR_SET_RECOVERYBCB_FAILED
ERROR_SUB_FIRMWARE_UPDATE_FAILED
ERROR_REBOOT_TO_RECOVERY_FAILED

REGENERATE_PACKAGE AND RETRY UPDATE:
ERROR_METAINFO_NOT_FOUND
ERROR_METAINFO_READ
ERROR_METAINFO_CHECKSUM
ERROR_METAINFO_PARSE
ERROR_METAINFO_SECTION_COMMON_NOT_FOUND
ERROR_METAINFO_SECTION_SIGNATURE_NOT_FOUND
ERROR_METAINFO_MANDATORY_TAG_NOT_FOUND
ERROR_METAINFO_DUPLICATE_SECTION
ERROR_METAINFO_SECTION_NOT_FOUND
ERROR_IMAGE_SIZE
ERROR_IMAGE_CHECKSUM
ERROR_IMAGE_INVALID_SECTORHEADER
ERROR_IMAGE_INCOMPATIBLE_VERSION
ERROR_IMAGE_READ
ERROR_NO_RELEASE_FOUND
ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE
ERROR_IMAGE_INCOMPATIBLE_SAME_VERSION
ERROR_INCOMPATIBLE_IMAGE_NONDELTA
ERROR_IMAGE_INCOMPATIBLE_VERSION_FORMAT

MANUAL_INTERVENTION:
ERROR_METAINFO_UNEXPECTED_SUBSECTION
ERROR_SIGNATURE_CHECK_FAILED
ERROR_METAINFO_INVALID_SUBSECTION_PATH
ERROR_METAINFO_REGION_CONFLICT
ERROR_METAINFO_VARIANT_CONFLICT
ERROR_METAINFO_INVALID_TRAIN_NAME
ERROR_IMAGE_DEVICE_NOT_SUPPORTED
ERROR_IMAGE_DEVICE_NOT_READY
ERROR_IMAGE_DEVICE_NOT_SELECTED
ERROR_IMAGE_DEVICE_INCOMPATIBLE_DM_VERSION
ERROR_INCOMPATIBLE_USB_FORMAT
ERROR_ROLLBACK_UPD_FAILURE
ERROR_MEDIA_UNAVAILABLE

ROLLBACK:
ERROR_ACTIVATION_VERIFICATION_AFTER_REBOOT
ERROR_ACTIVATION_CODE_VERIFICATION_FAILED
ERROR_DUAL_BANK_ACTIVATE_FAILED
ERROR_SINGLE_BANK_UPDATE_FAILED

VALIDATION BEFORE OUTPUT:
Verify that recovery_action is the exact Primary classification map value for final error_code.

For:
error_code = ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE

the output MUST contain exactly:
recovery_action: REGENERATE_PACKAGE AND RETRY UPDATE

Do not output:
recovery_action: RETRY_UPDATE

Do not output:
recovery_action: ROLLBACK

Do not output any other recovery_action.

The detailed_recovery_plan may say "retry update", but this MUST NOT change the recovery_action.

The recovery_action is determined ONLY by the Primary classification map.

STEP 3: GENERATE detailed_recovery_plan

CRITICAL RULE:
The detailed_recovery_plan MUST be selected by matching the FINAL error_code against the Detailed Recovery Plan Map below.

RULES FOR SELECTING detailed_recovery_plan:

First determine the final error_code in Step 1.

If the final error_code has an exact entry in the Detailed Recovery Plan Map, use that entry.

An exact Detailed Recovery Plan Map entry ALWAYS takes precedence over:

Package Type

Failure Reason

Evidence

Generic recovery_action rules

Any other recovery-plan inference

Do NOT substitute, modify, generalize, or reinterpret an exact map entry.

Do NOT generate a different plan based on Package Type when an exact map entry exists.

Package Type may only be used when the selected map entry explicitly contains a conditional such as "If package is delta type...".

If the package type is UNKNOWN, do not assume it is delta or full.

For ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE, ALWAYS use the exact plan specified below, regardless of Package Type.

The detailed_recovery_plan must contain only the selected recovery-plan text. Do not prepend or append explanations.

Do not use a different Detailed Recovery Plan Map entry based on similar wording or a similar recovery action.

DETAILED RECOVERY PLAN MAP:

ERROR_METAINFO_NOT_FOUND:
If package is delta type, regenerate delta package and verify metainfo files; otherwise regenerate full package.

ERROR_METAINFO_READ:
If package is delta type, regenerate delta package and verify metainfo files; otherwise regenerate full package.

ERROR_METAINFO_CHECKSUM:
If package is delta type, regenerate delta package and verify metainfo checksum; otherwise regenerate full package.

ERROR_METAINFO_PARSE:
If package is delta type, regenerate delta package and verify metainfo structure; otherwise regenerate full package.

ERROR_METAINFO_SECTION_COMMON_NOT_FOUND:
If package is delta type, regenerate delta package and verify metainfo common section; otherwise regenerate full package.

ERROR_METAINFO_SECTION_SIGNATURE_NOT_FOUND:
If package is delta type, regenerate delta package and verify metainfo signature section; otherwise regenerate full package.

ERROR_METAINFO_MANDATORY_TAG_NOT_FOUND:
If package is delta type, regenerate delta package and verify metainfo mandatory tags; otherwise regenerate full package.

ERROR_METAINFO_DUPLICATE_SECTION:
If package is delta type, regenerate delta package and check for duplicate sections; otherwise regenerate full package.

ERROR_METAINFO_SECTION_NOT_FOUND:
If package is delta type, regenerate delta package and verify all required sections are present; otherwise regenerate full package.

ERROR_IMAGE_SIZE:
If package is delta type, regenerate delta package and verify image size; otherwise regenerate full package.

ERROR_IMAGE_CHECKSUM:
If Failure Reason or Evidence indicates Source hash mismatch, generate full package and verify checksum (never retry with delta package). If package is full update package, regenerate full package and verify checksum. If package is delta type, regenerate delta package and verify images checksum.

ERROR_IMAGE_INVALID_SECTORHEADER:
If package is delta type, regenerate delta package and verify image checksums; otherwise regenerate full package.

ERROR_IMAGE_INCOMPATIBLE_VERSION:
Search for a compatible version in the database, choose the package with the highest version, and retry the update.

ERROR_IMAGE_READ:
If package is delta type, regenerate delta package and verify image checksums; otherwise regenerate full package.

ERROR_SIGNATURE_CHECK_FAILED:
Verify if signature is missing or expired on device and request for manual interruption. If not, print details of certificates on device.

ERROR_NO_RELEASE_FOUND:
If package is delta type, regenerate delta package and verify metainfo files; otherwise regenerate full package.

ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE:
Search for version which is compatible in database, choose package with highest version, and retry update.

ERROR_IMAGE_INCOMPATIBLE_SAME_VERSION:
Search for a compatible version in the database, choose the package with the highest version, and retry the update.

ERROR_INCOMPATIBLE_IMAGE_NONDELTA:
Check if a delta package is missing for the same version and start update. If not, generate a delta for the highest version and update.

ERROR_IMAGE_INCOMPATIBLE_VERSION_FORMAT:
Search for a compatible version in the database, choose the package with the highest version, and retry the update.

ERROR_ACTIVATION_VERIFICATION_AFTER_REBOOT:
If slot and version do not match, return failure and restart update. If slot matches but version does not, rollback to the previous boot slot and restart.

ERROR_DUAL_BANK_ACTIVATE_FAILED:
Request a rollback to the device client.

ERROR_SINGLE_BANK_UPDATE_FAILED:
Request a rollback to the device client.

ERROR_NOT_ENOUGH_MEMORY:
Request to free up memory on the device before retrying.

ERROR_UNKNOWN:
More evidence is required to classify the error.

STEP 3A: DETAILED RECOVERY PLAN OVERRIDE RULE

The following rule has absolute priority over all generic recovery-plan generation:

IF error_code == ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE
THEN
detailed_recovery_plan = "Search for version which is compatible in database, choose package with highest version, and retry update."

DO NOT use:
"If package is delta type, regenerate delta package and verify metainfo files; otherwise regenerate full package."

DO NOT derive the detailed_recovery_plan for ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE from Package Type.

DO NOT infer a full-package or delta-package regeneration plan for ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE.

The exact text from the Detailed Recovery Plan Map must be returned.

STEP 3B: RECOVERY PLAN VALIDATION

Before producing the output, verify:

final error_code is ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE

therefore recovery_action is REGENERATE PACKAGE AND RETRY UPDATE

therefore detailed_recovery_plan MUST be:
Search for version which is compatible in database, choose package with highest version, and retry update.

If the generated detailed_recovery_plan does not exactly match the mapped plan for the final error_code, replace it with the mapped plan before producing the final output.


Step 4:
Generate recovery_info JSON.

Fields:
{
  "src_version": "...",
  "target_version": "...",
  "package_type": "...",
  "service_request": "...",
  "action_item": "..."
}

SERVICE REQUEST SELECTION

CRITICAL RULE:
service_request MUST be determined exclusively from recovery_action.

Allowed service_request values:

cloud_service

ai_service_client

SERVICE REQUEST MAP:

cloud_service:

REGENERATE PACKAGE AND RETRY UPDATE

ai_service_client:

NO_ACTION

MEMORY_RECOVERY

RETRY_UPDATE

ROLLBACK

SINGLE_BANK_ROLLBACK

MANUAL_INTERVENTION

CLASSIFY_ERROR

RULES:

First determine the final error_code.

Determine recovery_action using the Primary classification map.

Determine service_request by performing an exact lookup of recovery_action in the SERVICE REQUEST MAP above.

Do NOT determine service_request from:

error_code

detailed_recovery_plan

Failure Reason

Evidence

Package Type

FROM_VERSION

TO_VERSION

action_item

Do NOT infer service_request from words such as "retry", "regenerate", "rollback", or "verify" appearing in detailed_recovery_plan.

The recovery_action is the ONLY input used to determine service_request.

If recovery_action is REGENERATE_PACKAGE AND RETRY UPDATE, service_request MUST be:
cloud_service

If recovery_action is RETRY_UPDATE, service_request MUST be:
ai_service_client

Never output a service_request other than:
cloud_service
or
ai_service_client


ACTION ITEM GENERATION:
- Extract actionable operation from recovery plan.
- Keep concise.
- Use imperative language.
ACTION ITEM SELECTION

CRITICAL RULE:
action_item MUST be determined exclusively by the FINAL error_code using the ACTION ITEM MAP below.

The final error_code is the ONLY lookup key for action_item.

Do NOT derive action_item from:

recovery_action

detailed_recovery_plan

service_request

Failure Reason

Evidence

Package Type

FROM_VERSION

TO_VERSION

Do NOT paraphrase, expand, or modify the mapped action_item.

ACTION ITEM MAP:

ERROR_METAINFO_NOT_FOUND:
verify_metainfo

ERROR_METAINFO_READ:
verify_metainfo

ERROR_METAINFO_CHECKSUM:
verify_metainfo

ERROR_METAINFO_PARSE:
verify_metainfo

ERROR_METAINFO_SECTION_COMMON_NOT_FOUND:
verify_metainfo

ERROR_METAINFO_SECTION_SIGNATURE_NOT_FOUND:
verify_metainfo

ERROR_METAINFO_MANDATORY_TAG_NOT_FOUND:
verify_metainfo

ERROR_METAINFO_DUPLICATE_SECTION:
verify_metainfo

ERROR_METAINFO_SECTION_NOT_FOUND:
verify_metainfo

ERROR_IMAGE_SIZE:
verify_images

ERROR_IMAGE_CHECKSUM:
verify_images

ERROR_IMAGE_INVALID_SECTORHEADER:
verify_images

ERROR_IMAGE_INCOMPATIBLE_VERSION:
verify_version

ERROR_IMAGE_READ:
verify_images

ERROR_SIGNATURE_CHECK_FAILED:
cert_read_eng_support

ERROR_NO_RELEASE_FOUND:
verify_metainfo

ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE:
verify_version

ERROR_IMAGE_INCOMPATIBLE_SAME_VERSION:
verify_version

ERROR_INCOMPATIBLE_IMAGE_NONDELTA:
verify_metainfo

ERROR_IMAGE_INCOMPATIBLE_VERSION_FORMAT:
verify_version

ERROR_INVALID_SOURCE_SET:
retry update

ERROR_IMAGE_FLASHING:
retry update

ERROR_MEDIUM_REMOVED:
retry update

ERROR_SET_RECOVERYBCB_FAILED:
retry update

ERROR_SUB_FIRMWARE_UPDATE_FAILED:
retry update

ERROR_REBOOT_TO_RECOVERY_FAILED:
retry update

ERROR_NOT_ENOUGH_MEMORY:
ram cleanup

ERROR_ACTIVATION_VERIFICATION_AFTER_REBOOT:
rollback

ERROR_ACTIVATION_CODE_VERIFICATION_FAILED:
rollback

ERROR_DUAL_BANK_ACTIVATE_FAILED:
rollback

ERROR_SINGLE_BANK_UPDATE_FAILED:
rollback

ERROR_METAINFO_UNEXPECTED_SUBSECTION:
eng_support

ERROR_METAINFO_INVALID_SUBSECTION_PATH:
eng_support

ERROR_METAINFO_REGION_CONFLICT:
eng_support

ERROR_METAINFO_VARIANT_CONFLICT:
eng_support

ERROR_METAINFO_INVALID_TRAIN_NAME:
eng_support

ERROR_IMAGE_DEVICE_NOT_SUPPORTED:
eng_support

ERROR_IMAGE_DEVICE_NOT_READY:
eng_support

ERROR_IMAGE_DEVICE_NOT_SELECTED:
eng_support

ERROR_IMAGE_DEVICE_INCOMPATIBLE_DM_VERSION:
eng_support

ERROR_INCOMPATIBLE_USB_FORMAT:
eng_support

ERROR_ROLLBACK_UPD_FAILURE:
eng_support

ERROR_MEDIA_UNAVAILABLE:
eng_support

ACTION ITEM RULES:

Determine the FINAL error_code first.

Look up the FINAL error_code in the ACTION ITEM MAP.

Return the mapped value exactly as written.

The action_item MUST NOT be generated from natural-language reasoning.

The action_item MUST NOT be generated from the detailed_recovery_plan.

The action_item MUST NOT be generated from recovery_action.

If the final error_code exists in the ACTION ITEM MAP, the mapped action_item has absolute priority.

Do not add words such as "perform", "request", "start", "verify", or "and retry".

Preserve underscores and spaces exactly as specified in the map.

ERROR_SIGNATURE_CHECK_FAILED MUST map to:
cert_read_eng_support

ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE MUST map to:
verify_version
even though its detailed_recovery_plan is to search for a compatible version and retry the update.

If the final error_code is not present in the ACTION ITEM MAP, use:
CLASSIFY_ERROR
as the action_item.

FINAL FIELD GENERATION ORDER:

Generate the four output fields independently using these deterministic mappings:

error_code
→ Determine from the classification process.

recovery_action
→ Exact lookup of error_code in the Primary Classification Map.

detailed_recovery_plan
→ Exact lookup of error_code in the Detailed Recovery Plan Map.

service_request
→ Exact lookup of recovery_action in the Service Request Map.

action_item
→ Exact lookup of error_code in the Action Item Map.

DEPENDENCY RULE:

error_code → recovery_action
error_code → detailed_recovery_plan
recovery_action → service_request
error_code → action_item

Do NOT use:
detailed_recovery_plan → action_item

Do NOT use:
recovery_action → action_item


DETERMINISTIC RULES:
- Always produce a single final error_code.
- Never provide alternatives.
- Never use uncertain language.


OUTPUT FORMAT:

Line 1:
error_code: <ERROR_*>

Line 2:
recovery_action: <ACTION>

Line 3:
detailed_recovery_plan: <PLAN>

Line 4:
recovery_info: {"src_version":"...","target_version":"...","package_type":"...","service_request":"...","action_item":"..."}

OUTPUT INTEGRITY:

Exactly four lines.

No markdown.

No bullets.

No numbering.

No explanations.

JSON must be valid.

detailed_recovery_plan MUST come from the Detailed Recovery Plan Map.

Never replace an exact mapped plan with a generic plan.

Never infer detailed_recovery_plan from recovery_action alone.

Never infer detailed_recovery_plan from Package Type when an exact error-code mapping exists.