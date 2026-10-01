/**
 * @addtogroup  aidl
 * @{
 * @file        IUpdateCallback.aidl
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
import swu.FcSwUpdateSrv.trUpdProgress;
import swu.FcSwUpdateSrv.trUpdState;
import swu.FcSwUpdateSrv.trErrorIds;

// Declare trUpdProgress and trUpdState so AIDL can find it and knows that it implements
// the parcelable protocol.

oneway interface IUpdateCallback {
   void onUpdateState(in trUpdState state);
   void onUpdateProgress(in trUpdProgress progress);
   void onUpdateError(in trErrorIds errors);
   void onCancelUpdResult(in trErrorIds errors);
   void onCompleteUpdResult(in trErrorIds errors);
}
