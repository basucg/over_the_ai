======================================================================
         AI Model ROOT CAUSE DIAGNOSIS (WITH PROCESS LOGS)
======================================================================
1. Package Type: DELTA PACKAGE
2. Version Information:
   - FROM_VERSION:qpr1_a12_int_2026.19.0
   - TO_VERSION:qpr1_a12_int_2026.18.0
3. Errorcode:39 (ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE)
Resolved Errorcode: 39
Resolved Error Enum: ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE
======================================================================
AI Model ENUM NEXT STEPS
======================================================================
1. Failure Reason: Downgrade prohibited.
2. Evidence:
[ERROR] da3_app_fcswupdate: System donot permit downgrade [cur=2026190][post=2026180]
   [ERROR] da3_app_fcswupdate: Error Update-Medium: ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE 39 FCID:0000
   [ERROR] da3_app_fcswupdate: Error Update-Medium: ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE 39 FCID:0000
   [ERROR] da3_app_fcswupdate: IntegrityCheck::setIntegrityCheckResult() set 0 to android property persist.vendor.bosch.swu.integrity_check SUCCESS
   [ERROR] da3_app_fcswupdate: Binder error in toBinderEnErrorId 39
   [ERROR] da3_app_fcswupdate: Binder error in toBinderEnErrorId 39
   [ERROR] da3_app_fcswupdate: Move Adb log file to FOTA after errorCode:=39
3. Next Steps: Investigate compatibility issues between the update image and the device version.
======================================================================
Report File Created on Linux Server: /tmp/ai-swupdate-reports/swupdate-report-1790762145.md
======================================================================
======================================================================
AI Model RECOVERY PLAN
======================================================================
error_code: ERROR_IMAGE_INCOMPATIBLE_DOWNGRADE
recovery_action: REGENERATE_PACKAGE AND RETRY UPDATE
detailed_recovery_plan: verify_version
recovery_info: {"src_version":"qpr1_a12_int_2026.19.0","target_version":"qpr1_a12_int_2026.18.0","package_type":"DELTA PACKAGE","service_request":"cloud_service","action_item":"verify_version"}
======================================================================

[14:30:44] [INFO] Connecting to Package Generator at swu_package_generator:9001 to generate package.
[14:30:44] [INFO] Sent package generation request with params: {'verify_version': True, 'verification_type': 'Upgrade', 'from_version': 'qpr1_a12_int_2026.19.0', 'to_version': 'qpr1_a12_int_2026.18.0', 'package_type': 'delta'}
[14:31:44] [INFO] Response from Package Generator: {'request_id': 'req-1790778644', 'result': {'status': 'success', 'package_name': 'delta_qpr1_a12_int_2026.19.0-qpr1_a12_int_2026.23.0.zip'}}
