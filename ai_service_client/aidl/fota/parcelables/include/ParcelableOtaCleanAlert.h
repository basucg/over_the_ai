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

enum enOtaCleanAlert : uint32_t
{
   CLEAN_ALERT_NONE                    = 0,
   CLEAN_ALERT_ALL                     = 1,
   CLEAN_ALERT_OTAUpdateAvailable      = 2,
   CLEAN_ALERT_USBUpdateAvailable      = 3
};

//ParcelableOtaCleanAlert
class ParcelableOtaCleanAlert : public Parcelable
{
public:
   ParcelableOtaCleanAlert();
   explicit ParcelableOtaCleanAlert( enOtaCleanAlert OtaCleanAlert );

   ParcelableOtaCleanAlert( const ParcelableOtaCleanAlert& other )      = default;
   ParcelableOtaCleanAlert& operator=( const ParcelableOtaCleanAlert& ) = default;

   ParcelableOtaCleanAlert( ParcelableOtaCleanAlert&& )                 = default;
   ParcelableOtaCleanAlert& operator=( ParcelableOtaCleanAlert&& )      = default;

   ~ParcelableOtaCleanAlert() override;

   status_t writeToParcel( Parcel *parcel ) const override;

   status_t readFromParcel( const Parcel *parcel ) override;

   enOtaCleanAlert getOtaCleanAlert() const;

   void setOtaCleanAlert( const enOtaCleanAlert OtaCleanAlert );

private:
   enOtaCleanAlert mOtaCleanAlert;
};

}  // namespace hmi
}  // namespace fota

