/**
  * @swcomponent OTA
  * @{
  * @file        IOtaHmiServiceCallback.aidl
  * @brief       Interface definitions for client callback.
  *	             HMI applicaiton should implement this interface to handle respond from OTA module.
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

import fota.hmi.ParcelableActivePackageInfo;
import fota.hmi.ParcelableDynamicHMIInfo;
import fota.hmi.ParcelableOtaDisplayState;
import fota.hmi.ParcelableOtaUpdateHistory;
import fota.hmi.ParcelableSystemInfo;

interface IOtaHmiServiceCallback {
    /**
    * set_gnl_3 to set_gnl_55
    * set_gnl_57 to set_gnl_58
    * set_gnl_58 to set_gnl_77
    * set_gnl_77 to set_gnl_59
    * set_gnl_59 to set_gnl_60 etc.
    * OTA responds to HMI application about OTA state change.
    * @param1 [in] otaDisplayState, [type] ParcelableOtaDisplayState, [size] NA, [range] NA, [desc] specific current state of OTA and Alerts
    * @return [type] void, [value] NA
    */
    void onOtaStateChange( in ParcelableOtaDisplayState otaDisplayState )                              = 0;

    /**
    * set_gnl_55 to set_gnl_57
    * set_gnl_77 to set_gnl_59
    * OTA send detail of Software Update package information to HMI application before Download and Activation step.
    * @param1 [in] activePackageInfo, [type] ParcelableActivePackageInfo, [size] NA, [range] NA, [desc] detail information of package
    * @return [type] void, [value] NA
    */
    void onActivePackageInfoChange( in ParcelableActivePackageInfo activePackageInfo )                 = 1;

    /**
     * set_gnl_55/77/69/80
     * OTA sends current complete percentage of Downloading or Installing step.
     * @param1 [in] dynamicHmiInfo, [type] ParcelableDynamicHMIInfo, [size] NA, [range] NA, [desc] detail information that HMI should aware
     * @return [type] void, [value] NA
     */
    void onDynamicHmiInfoChange( in ParcelableDynamicHMIInfo dynamicHmiInfo )                          = 2;

    /**
    * set_gnl_3 to set_gnl_53/54
    * OTA responds after HMI checks Software version.
    * @param1 [in] otaUpdateHistoryList, [type] ParcelableOtaUpdateHistory, [size] NA, [range] NA, [desc] list of update history
    * @return [type] void, [value] NA
    */
    void onUpdateHistoryChange( in ParcelableOtaUpdateHistory [] otaUpdateHistoryList )                = 3;

    /**
    * OTA notices to HMI to disable/enable Check For Update via OTA button.
    * @param1 [in] isEnable, [type] boolean, [size] NA, [range] NA, [desc] is enable or not.
    * @return [type] void, [value] NA
    */
    void onCheckForUpdateStatusChange( in boolean isEnable )                                           = 4;

    /**
    * OTA notices to HMI to disable/enable Check For Update via USB button.
    * @param1 [in] isEnable, [type] boolean, [size] NA, [range] NA, [desc] is enable or not
    * @return [type] void, [value] NA
    */
    void onUpdateViaUSBStatusChange( in boolean isEnable )                                             = 5;

    /**
    * OTA sends current system information to HMI application
    * @param1 [in] systemInfo, [type] ParcelableSystemInfo, [size] NA, [range] NA, [desc] detail system information that HMI want
    * @return [type] void, [value] NA
    */
    void onSystemInfoUpdate( in ParcelableSystemInfo systemInfo )                                      = 6;

    /**
    * OTA notices to HMI to disable/enable Check For Update via USB button.
    * @param1 [in] isEnable, [type] boolean, [size] NA, [range] NA, [desc] is enable or not
    * @return [type] void, [value] NA
    */
    void onCriticalSWDownloadConsent( in boolean isEnable )                                            = 7;
}

