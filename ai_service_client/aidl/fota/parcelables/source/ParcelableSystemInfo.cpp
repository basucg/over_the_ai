/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableSystemInfo.cpp
  * @brief       Parcelable Implementation for System Information.
  * @authors     unn5hc
  * @copyright   (C) 2023 Robert Bosch Engineering and Business Solutions Limited.
  *              The reproduction, distribution and utilization of this file as
  *              well as the communication of its contents to others without express
  *              authorization is prohibited. Offenders will be held liable for the
  *              payment of damages. All rights reserved in the event of the grant
  *              of a patent, utility model or design.
  * @}
  */

#include "ParcelableSystemInfo.h"
#include <binder/Parcel.h>
#include "OtaCommon.h"

namespace fota {
namespace hmi {

ParcelableSystemInfo::ParcelableSystemInfo() : mSerialNumber( "Sample-Serial" ), mSoftwareVersion( "0.0" ), mSoftwareID( "Sample-ID" ) {

}

ParcelableSystemInfo::ParcelableSystemInfo(  String16 & serialNumer,
                                             String16 & softwareVersion,
                                             String16 & softwareID ) :
   mSerialNumber( serialNumer ),
   mSoftwareVersion( softwareVersion ),
   mSoftwareID( softwareID ) {

}

ParcelableSystemInfo::~ParcelableSystemInfo() {}

String16 ParcelableSystemInfo::getSerialNumber() const {
   return ( mSerialNumber );
}

void ParcelableSystemInfo::setSerialNumber( const String16 serialNumber ) {
   mSerialNumber = serialNumber;
}

String16 ParcelableSystemInfo::getSoftwareVersion() const {
   return ( mSoftwareVersion );
}

void ParcelableSystemInfo::setSoftwareVersion( const String16 softwareVersion ) {
   mSoftwareVersion = softwareVersion;
}

String16 ParcelableSystemInfo::getSoftwareID() const {
   return ( mSoftwareID );
}

void ParcelableSystemInfo::setSoftwareID( const String16 softwareID ) {
   mSoftwareID = softwareID;
}

status_t ParcelableSystemInfo::writeToParcel( Parcel *parcel ) const {
   RETURN_IF_FAILED( parcel->writeString16( mSerialNumber ) );
   RETURN_IF_FAILED( parcel->writeString16( mSoftwareVersion ) );
   RETURN_IF_FAILED( parcel->writeString16( mSoftwareID ) );
   return ( OK );
}

status_t ParcelableSystemInfo::readFromParcel( const Parcel *parcel ) {
   RETURN_IF_FAILED( parcel->readString16( &mSerialNumber ) );
   RETURN_IF_FAILED( parcel->readString16( &mSoftwareVersion ) );
   RETURN_IF_FAILED( parcel->readString16( &mSoftwareID ) );
   return ( OK );
}

}  // namespace hmi
}  // namespace fota