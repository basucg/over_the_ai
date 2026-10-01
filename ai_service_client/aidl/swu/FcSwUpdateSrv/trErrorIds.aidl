/**
 * @addtogroup  aidl
 * @{
 * @file        trErrorIds.aidl
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
 import swu.FcSwUpdateSrv.tenSwUpdateError;

 parcelable trErrorIds {
    tenSwUpdateError errorIds = tenSwUpdateError.ERROR_OK;
  }