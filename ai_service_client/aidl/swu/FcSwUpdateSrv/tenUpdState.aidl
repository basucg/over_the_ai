/**
 * @addtogroup  aidl
 * @{
 * @file        tenUpdState.aidl
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

enum tenUpdState{
    IDLE = 0,
    NOTREADY = 1,
    RUNNING = 5,
    ERROR = 6,
    RESULT = 9,
    REBOOT = 10,
    WAITACTIVATE = 18,
    ACTIVATION_VERIFIED = 19,
  }