/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableSystemInfo.h
  * @brief       Parcelable Definition for System Information.
  * @authors     unn5hc
  * @copyright   (C) 2023 Robert Bosch Engineering and Business Solutions Limited.
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

class ParcelableSystemInfo : public Parcelable
{
public:
   ParcelableSystemInfo();
   ParcelableSystemInfo( String16 & serialNumber,
                         String16 & softwareVersion,
                         String16 & softwareID );

   ParcelableSystemInfo( const ParcelableSystemInfo& other )      = default;
   ParcelableSystemInfo& operator=( const ParcelableSystemInfo& ) = default;

   ParcelableSystemInfo( ParcelableSystemInfo&& )                 = default;
   ParcelableSystemInfo& operator=( ParcelableSystemInfo&& )      = default;

   ~ParcelableSystemInfo() override;

   String16 getSerialNumber() const;

   void setSerialNumber( const String16 serialNumber );

   String16 getSoftwareVersion() const;

   void setSoftwareVersion( const String16 sotfwareVersion );

   String16 getSoftwareID() const;

   void setSoftwareID( const String16 softwareID );

   status_t writeToParcel( Parcel *parcel ) const;

   status_t readFromParcel( const Parcel *parcel );

private:
   String16 mSerialNumber;
   String16 mSoftwareVersion;
   String16 mSoftwareID;
};

}  // namespace hmi
}  // namespace fota