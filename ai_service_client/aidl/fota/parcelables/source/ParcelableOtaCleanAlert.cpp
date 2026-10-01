/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableHmiServiceEnums.cpp
  * @brief       Parcelable Implementation for HmiServiceEnums.
  * @authors     hrd3kor, gur6kor
  * @copyright   (C) 2020 Robert Bosch Engineering and Business Solutions Limited.
  *              The reproduction, distribution and utilization of this file as
  *              well as the communication of its contents to others without express
  *              authorization is prohibited. Offenders will be held liable for the
  *              payment of damages. All rights reserved in the event of the grant
  *              of a patent, utility model or design.
  * @}
  */

#include "ParcelableOtaCleanAlert.h"
#include "OtaCommon.h"
#include <binder/Parcel.h>

namespace fota {
namespace hmi {

//ParcelableOtaCleanAlert
ParcelableOtaCleanAlert::ParcelableOtaCleanAlert() : mOtaCleanAlert( enOtaCleanAlert::CLEAN_ALERT_NONE ) {

}

ParcelableOtaCleanAlert::ParcelableOtaCleanAlert( enOtaCleanAlert mOtaCleanAlert ) : mOtaCleanAlert( mOtaCleanAlert ) {
}

ParcelableOtaCleanAlert::~ParcelableOtaCleanAlert() {
}

status_t ParcelableOtaCleanAlert::writeToParcel( Parcel *parcel ) const {
   RETURN_IF_FAILED( parcel->writeUint32( static_cast < uint32_t >( mOtaCleanAlert ) ) );

   return ( OK );
}

status_t ParcelableOtaCleanAlert::readFromParcel( const Parcel *parcel ) {
   mOtaCleanAlert = static_cast < enOtaCleanAlert >( parcel->readUint32() );

   return ( OK );
}

enOtaCleanAlert ParcelableOtaCleanAlert::getOtaCleanAlert() const {
   return ( mOtaCleanAlert );
}

void ParcelableOtaCleanAlert::setOtaCleanAlert( const enOtaCleanAlert OtaCleanAlert ) {
   mOtaCleanAlert = OtaCleanAlert;
}

}  // namespace hmi
}  // namespace fota

