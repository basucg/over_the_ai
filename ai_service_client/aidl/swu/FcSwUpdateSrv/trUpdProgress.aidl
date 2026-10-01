/**
 * @addtogroup  aidl
 * @{
 * @file        trUpdProgress.aidl
 * @brief       defines interface for SWU service
 *
 * @copyright   (C) 2023 Robert Bosch GmbH.
 *              The reproduction, distribution and utilization of this file as
 *              well as the communication of its contents to others without express
 *              authorization is prohibited. Offenders will be held liable for the
 *              payment of damages. All rights reserved in the event of the grant
 *              of a patent, utility model or design.
 * @}
 */


package swu.FcSwUpdateSrv;

parcelable trUpdProgress {
    String train;
    String deviceName;
    String moduleName;
    String subModuleName;
    String refKey;
    String source;
    String line1;
    String line2;
    String luaCmd;
    int u32Retries;
    int u32NumAll;
    int u32NumComplete;
    int u32NumRunning;
    int u32NumNotApplicable;
    int u32NumFailed;
    int u32NumRemaining;
    int u8SubModulePercentComplete;
    int u8ReleasePercentComplete;
    int u8ReleasePercentCompleteForPhase;
  }

