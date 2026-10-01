/**
  * @swcomponent OTA
  * @{
  * @file        IOtaHmiService.aidl
  * @brief       Interface definitions for service side.
  *	             OTA module shall create an instance of this service at native side.
  *              HMI application register later and send relating requests.
  * @authors     hrd3kor, gur6kor, unn5hc
  * @copyright   (C) 2020 Robert Bosch Engineering and Business Solutions Limited.
  *              The reproduction, distribution and utilization of this file as
  *              well as the communication of its contents to others without express
  *              authorization is prohibited. Offenders will be held liable for the
  *              payment of damages. All rights reserved in the event of the grant
  *              of a patent, utility model or design.
  * @}
  */

package fota.hmi;

import fota.hmi.IOtaHmiServiceCallback;
import fota.hmi.ParcelableOtaCommandCode;
import fota.hmi.ParcelableOtaCleanAlert;

interface IOtaHmiService {
    /**
    * Register a callback which will respond for request from OTA module.
    * @param1 [in] callback, [type] IOtaHmiServiceCallback, [size] NA, [range] NA, [desc] object of IOtaHmiServiceCallback
    * @return [type] boolean, [value] always return true
    */
    boolean registerCallback( IOtaHmiServiceCallback callback, String topic)                   = 0;

    /**
    * Unregister a callback registered before in callback vector.
    * @param1 [in] callback, [type] IOtaHmiServiceCallback, [size] NA, [range] NA, [desc] object of IOtaHmiServiceCallback
    * @return [type] boolean, [value] true on success, false if can't remove from callback list
    */
    boolean deregisterCallback( IOtaHmiServiceCallback callback, String topic)                 = 1;

    /**
    * HMI request a session to OTA module. Command code is listed in ParcelableHmiServiceEnums.h
    * @param1 [in] otaCommandCode, [type] ParcelableOtaCommandCode, [size] NA, [range] NA, [desc] it's a part of OTA state machine such as DownloadStart, UpdateOverUSB, ActivateDecline
    * @return [type] boolean, [value] -1 if unable to send otaCommandCode, 0 if succeed
    */
    boolean otaSessionControl( in ParcelableOtaCommandCode otaCommandCode )       = 2;

    /**
    * The Alert about OTA session is closed by User Actions or Some HMI Actions. Command code is listed in ParcelableOtaCleanAlert.h
    * @param1 [in] cleanAlert, [type] ParcelableOtaCleanAlert, [size] NA, [range] NA, [desc] Once the Alert on HMI such as Download/Install/Activation Failed, Update Available is closed by User or by Any Actions on HMI.
    * @return [type] boolean, [value] -1 if unable to take Action on CleanAlert, 0 if succeed
    */
    boolean otaCleanAlert( in ParcelableOtaCleanAlert cleanAlert )       = 3;
}

