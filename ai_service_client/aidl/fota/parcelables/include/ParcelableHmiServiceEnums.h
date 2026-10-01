/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableHmiServiceEnums.h
  * @brief       Parcelable Implementation for HmiServiceEnums classes.
  * @authors     hrd3kor, gur6kor
  * @copyright   (C) 2020 Robert Bosch Engineering and Business Solutions Limited.
  *              The reproduction, distribution and utilization of this file as
  *              well as the communication of its contents to others without express
  *              authorization is prohibited. Offenders will be held liable for the
  *              payment of damages. All rights reserved in the event of the grant
  *              of a patent, utility model or design.
  * @}
  */

#pragma once

#include <binder/Parcel.h>
#include <binder/Parcelable.h>

using namespace android;

namespace fota {
namespace hmi {

/**
* Action that HMI application requests to OTA module
*/
enum enOtaCommandCode : uint32_t
{
   GET_UPDATE_HISTORY = 0,
   CHECK_FOR_UPDATES,
   UPDATE_VIA_USB,
   CHECK_FOR_UPDATES_CANCELLED,
   DOWNLOAD_CONSENT_ACCEPTED,
   DOWNLOAD_CONSENT_CANCELLED,
   DOWNLOAD_CANCELLED,
   ACTIVATE_CONSENT_ACCEPTED,
   ACTIVATE_POSTPONED,
   AUTO_PKG_NOTIFY_VIEW,
   AUTO_PKG_NOTIFY_LATER,
   NONE
};

/**
* Current state of OTA that HMI application should aware
*/
enum enOtaDisplayState : uint32_t
{
   Idle                          = 0,
   NoUpdateAvailable             = 1,
   UpdateAvailable               = 2,
   CheckForUpdateFail            = 3,
   DownloadInProgress            = 4,
   DownloadFailure               = 5,
   DownloadComplete              = 6,
   DownloadCancelSuccess         = 7,
   InstallInProgress             = 8,
   InstallFailure                = 9,
   InstallSuccess                = 10, // HMI does not need any action on this enum
   ReadyToActivate               = 11, // this is for wait Activation consent
   ActivationPostponed           = 12,
   ActivationConditionsMet       = 13, // HMI does not need any action on this enum
   ActivationConditionsNotMet    = 14,
   ActivationInProgress          = 15,
   ActivationFailure             = 16,
   ActivationRebootRequired      = 17,
   ActivationSuccess             = 18,
   ValidUsbNotConnected          = 19,
   ValidUsbConnected             = 20,
   USBInvCopyResult              = 21,
   AutomaticUpdateViaOTA         = 22,
   AutomaticUpdateViaUSB         = 23,
   DownloadInterrupt_waitingToReConnect = 24
};

enum enOtaNotificationAlerts: uint32_t
{
   OTA_ALERT_None                       = 0,
   OTA_ALERT_OTAUpdateAvailable         = 1,
   OTA_ALERT_USBUpdateAvailable         = 2
};

enum enCampaignType : uint32_t
{
   Invalid = 0,
   Regular,
   Silent,
   Critical
};

enum enUpdateType : uint32_t
{
   NA = 0,
   OTA,
   USB
};

//ParcelableOtaCommandCode
class ParcelableOtaCommandCode : public Parcelable
{
public:
   ParcelableOtaCommandCode();
   explicit ParcelableOtaCommandCode( enOtaCommandCode otaCommandCode );

   ParcelableOtaCommandCode( const ParcelableOtaCommandCode& other )      = default;
   ParcelableOtaCommandCode& operator=( const ParcelableOtaCommandCode& ) = default;

   ParcelableOtaCommandCode( ParcelableOtaCommandCode&& )                 = default;
   ParcelableOtaCommandCode& operator=( ParcelableOtaCommandCode&& )      = default;

   ~ParcelableOtaCommandCode() override;

   status_t writeToParcel( Parcel *parcel ) const override;

   status_t readFromParcel( const Parcel *parcel ) override;

   enOtaCommandCode getOtaCommandCode() const;

   void setOtaCommandCode( const enOtaCommandCode otaCommandCode );

private:
   enOtaCommandCode mOtaCommandCode;
};

//ParcelableOtaDisplayState
class ParcelableOtaDisplayState : public Parcelable
{
public:
   ParcelableOtaDisplayState();
   explicit ParcelableOtaDisplayState( enOtaDisplayState otaDisplayState, enOtaNotificationAlerts OtaNotificationAlerts );

   ParcelableOtaDisplayState( const ParcelableOtaDisplayState& other )      = default;
   ParcelableOtaDisplayState& operator=( const ParcelableOtaDisplayState& ) = default;

   ParcelableOtaDisplayState( ParcelableOtaDisplayState&& )                 = default;
   ParcelableOtaDisplayState& operator=( ParcelableOtaDisplayState&& )      = default;

   ~ParcelableOtaDisplayState() override;

   status_t writeToParcel( Parcel *parcel ) const override;

   status_t readFromParcel( const Parcel *parcel ) override;

   enOtaDisplayState getOtaDisplayState() const;

   void setOtaDisplayState( const enOtaDisplayState otaDisplayState );

   enOtaNotificationAlerts getOtaNotificationAlerts() const;

   void setOtaNotificationAlerts( const enOtaNotificationAlerts OtaNotificationAlerts );

private:
   enOtaDisplayState mOtaDisplayState;
   enOtaNotificationAlerts mOtaNotificationAlerts;
};

}  // namespace hmi
}  // namespace fota

