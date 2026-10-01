/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableActivePackageInfo.cpp
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

#include "ParcelableActivePackageInfo.h"
#include <binder/Parcel.h>
#include "OtaCommon.h"
//#include "Logger.h"

namespace fota {
namespace hmi {

ParcelableActivePackageInfo::ParcelableActivePackageInfo() :
   mVersion( "" ),
   mPackageSize( 0 ),
   mReleaseNotes( "" ),
   mCampaignType( enCampaignType::Invalid ),
   mUpdateType( enUpdateType::NA ),
   mEstimatedDownloadTime( 0 ),
   mEstimatedInstallationTime( 0 ),
   mEstimatedActivateTime( 0 ){
}

ParcelableActivePackageInfo::ParcelableActivePackageInfo( String16      & version,
                                                          uint64_t        packageSize,
                                                          String16      & releaseNotes,
                                                          enCampaignType  campaignType,
                                                          enUpdateType    updateType,
                                                          uint32_t        estimatedDownloadTime,
                                                          uint32_t        estimatedInstallationTime,
                                                          uint32_t        estimatedActivateTime)
   : mVersion( version ),
   mPackageSize( packageSize ),
   mReleaseNotes( releaseNotes ),
   mCampaignType( campaignType ),
   mUpdateType( updateType ),
   mEstimatedDownloadTime( estimatedDownloadTime ),
   mEstimatedInstallationTime( estimatedInstallationTime ),
   mEstimatedActivateTime( estimatedActivateTime ){

}

ParcelableActivePackageInfo::~ParcelableActivePackageInfo() {

}

String16 ParcelableActivePackageInfo::getVersion() const {
   return ( mVersion );
}

void ParcelableActivePackageInfo::setVersion( const String16& version ) {
   mVersion = version;
}

uint64_t ParcelableActivePackageInfo::getPackageSize() const {
   return ( mPackageSize );
}

void ParcelableActivePackageInfo::setPackageSize( const uint64_t packageSize ) {
   mPackageSize = packageSize;
}

String16 ParcelableActivePackageInfo::getReleaseNotes() const {
   return ( mReleaseNotes );
}

void ParcelableActivePackageInfo::setReleaseNotes( const String16& releaseNotes ){
   mReleaseNotes = releaseNotes;
}

enCampaignType ParcelableActivePackageInfo::getCampaignType() const {
   return ( mCampaignType );
}

void ParcelableActivePackageInfo::setCampaignType( const enCampaignType& campaignType ){
   mCampaignType = campaignType;
}

enUpdateType ParcelableActivePackageInfo::getUpdateType() const {
   return ( mUpdateType );
}

void ParcelableActivePackageInfo::setUpdateType( const enUpdateType& updateType ){
   mUpdateType = updateType;
}

uint32_t ParcelableActivePackageInfo::getEstimatedDownloadTime() const {
   return ( mEstimatedDownloadTime );
}

void ParcelableActivePackageInfo::setEstimatedDownloadTime( const uint32_t estimatedDownloadTime ) {
   mEstimatedDownloadTime = estimatedDownloadTime;
}

uint32_t ParcelableActivePackageInfo::getEstimatedInstallationTime() const {
   return ( mEstimatedInstallationTime );
}

void ParcelableActivePackageInfo::setEstimatedInstallationTime( const uint32_t estimatedInstallationTime ) {
   mEstimatedInstallationTime = estimatedInstallationTime;
}

uint32_t ParcelableActivePackageInfo::getEstimatedActivateTime() const {
   return ( mEstimatedActivateTime );
}

void ParcelableActivePackageInfo::setEstimatedActivateTime( const uint32_t estimatedActivateTime ) {
   mEstimatedActivateTime = estimatedActivateTime;
}

status_t ParcelableActivePackageInfo::writeToParcel( Parcel *parcel ) const {
   RETURN_IF_FAILED( parcel->writeString16( mVersion ) );
   RETURN_IF_FAILED( parcel->writeUint64( mPackageSize ) );
   RETURN_IF_FAILED( parcel->writeString16( mReleaseNotes ) );
   RETURN_IF_FAILED( parcel->writeUint32( static_cast < uint32_t >( mCampaignType ) ) );
   RETURN_IF_FAILED( parcel->writeUint32( static_cast < uint32_t >( mUpdateType ) ) );
   RETURN_IF_FAILED( parcel->writeUint32( mEstimatedDownloadTime ) );
   RETURN_IF_FAILED( parcel->writeUint32( mEstimatedInstallationTime ) );
   RETURN_IF_FAILED( parcel->writeUint32( mEstimatedActivateTime ) );
   return ( OK );
}

status_t ParcelableActivePackageInfo::readFromParcel( const Parcel *parcel ) {
   RETURN_IF_FAILED( parcel->readString16( &mVersion ) );
   RETURN_IF_FAILED( parcel->readUint64( &mPackageSize ) );
   RETURN_IF_FAILED( parcel->readString16( &mReleaseNotes ) );
   mCampaignType = static_cast < enCampaignType >( parcel->readUint32() );
   mUpdateType   = static_cast < enUpdateType >( parcel->readUint32() );
   RETURN_IF_FAILED( parcel->readUint32( &mEstimatedDownloadTime ) );
   RETURN_IF_FAILED( parcel->readUint32( &mEstimatedInstallationTime ) );
   RETURN_IF_FAILED( parcel->readUint32( &mEstimatedActivateTime ) );
   return ( OK );
}

}  // namespace hmi
}  // namespace fota

