/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableActivePackageInfo.h
  * @brief       Parcelable Implementation for ActivePackageInfo.
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
#include "ParcelableHmiServiceEnums.h"

using namespace android;

namespace fota {
namespace hmi {

class ParcelableActivePackageInfo : public Parcelable
{

public:
/**
  * Default Constructor for ParcelableActivePackageInfo
  * @param None
  * @return object of ParcelableActivePackageInfo
  */
   ParcelableActivePackageInfo();

/**
  * Constructor for ParcelableActivePackageInfo
  * @param version, packageSize, releaseNotes, campaignType, estimatedDownloadTime, estimatedInstallationTime, estimatedActivateTime
  * @return object of ParcelableActivePackageInfo
  */
   ParcelableActivePackageInfo( String16      & version,
                                uint64_t        packageSize,
                                String16      & releaseNotes,
                                enCampaignType  campaignType,
                                enUpdateType    updateType,
                                uint32_t        estimatedDownloadTime,
                                uint32_t        estimatedInstallationTime,
                                uint32_t        estimatedActivateTime );

   ParcelableActivePackageInfo( const ParcelableActivePackageInfo& other )      = default;
   ParcelableActivePackageInfo& operator=( const ParcelableActivePackageInfo& ) = default;

   ParcelableActivePackageInfo( ParcelableActivePackageInfo&& )                 = default;
   ParcelableActivePackageInfo& operator=( ParcelableActivePackageInfo&& )      = default;

   ~ParcelableActivePackageInfo() override;

   status_t writeToParcel( Parcel *parcel ) const override;

   status_t readFromParcel( const Parcel *parcel ) override;

   String16 getVersion() const;

   void setVersion( const String16& version );

   uint64_t getPackageSize() const;

   void setPackageSize( const uint64_t packageSize );

   String16 getReleaseNotes() const;

   void setReleaseNotes( const String16& releaseNotes );

   enCampaignType getCampaignType() const;

   void setCampaignType( const enCampaignType& campaignType );

   enUpdateType getUpdateType() const;

   void setUpdateType( const enUpdateType& updateType );

   uint32_t getEstimatedDownloadTime() const;

   void setEstimatedDownloadTime( const uint32_t estimatedDownloadTime );

   uint32_t getEstimatedInstallationTime() const;

   void setEstimatedInstallationTime( const uint32_t estimatedInstallationTime );

   uint32_t getEstimatedActivateTime() const;

   void setEstimatedActivateTime( const uint32_t estimatedActivateTime );


private:
   String16 mVersion;                       // Need in set_gnl_57/68
   uint64_t mPackageSize;                   // Need in set_gnl_57/68
   String16 mReleaseNotes;                  // Need in set_gnl_57/68. It should be What's new field
   enCampaignType mCampaignType;
   enUpdateType mUpdateType;                // Let HMI know current update type on Activation fail handling
   uint32_t mEstimatedDownloadTime;         // Need in set_gnl_57/68. How to extract it? Don't exist in trOtaPackageInfo struct
   uint32_t mEstimatedInstallationTime;     // Is not needed, to be removed with discussion with HMI
   uint32_t mEstimatedActivateTime;         // Need in set_gnl_59/70. Use in activating step
};

}  // namespace hmi
}  // namespace fota

