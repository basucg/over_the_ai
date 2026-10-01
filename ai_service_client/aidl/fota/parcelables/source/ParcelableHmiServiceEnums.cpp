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

#include "ParcelableHmiServiceEnums.h"
#include "OtaCommon.h"
#include <binder/Parcel.h>

namespace fota {
namespace hmi {

//ParcelableOtaCommandCode
ParcelableOtaCommandCode::ParcelableOtaCommandCode() : mOtaCommandCode( enOtaCommandCode::NONE ) {

}

ParcelableOtaCommandCode::ParcelableOtaCommandCode( enOtaCommandCode OtaCommandCode ) : mOtaCommandCode( OtaCommandCode ) {
}

ParcelableOtaCommandCode::~ParcelableOtaCommandCode() {
}

status_t ParcelableOtaCommandCode::writeToParcel( Parcel *parcel ) const {
   RETURN_IF_FAILED( parcel->writeUint32( static_cast < uint32_t >( mOtaCommandCode ) ) );

   return ( OK );
}

status_t ParcelableOtaCommandCode::readFromParcel( const Parcel *parcel ) {
   mOtaCommandCode = static_cast < enOtaCommandCode >( parcel->readUint32() );

   return ( OK );
}

enOtaCommandCode ParcelableOtaCommandCode::getOtaCommandCode() const {
   return ( mOtaCommandCode );
}

void ParcelableOtaCommandCode::setOtaCommandCode( const enOtaCommandCode otaCommandCode ) {
   mOtaCommandCode = otaCommandCode;
}

//ParcelableOtaDisplayState
ParcelableOtaDisplayState::ParcelableOtaDisplayState() : mOtaDisplayState( enOtaDisplayState::Idle ),mOtaNotificationAlerts(enOtaNotificationAlerts::OTA_ALERT_None) {

}

ParcelableOtaDisplayState::ParcelableOtaDisplayState( enOtaDisplayState mOtaDisplayState, enOtaNotificationAlerts OtaNotificationAlerts ) : mOtaDisplayState( mOtaDisplayState ) , mOtaNotificationAlerts(OtaNotificationAlerts) {
}

ParcelableOtaDisplayState::~ParcelableOtaDisplayState() {
}

status_t ParcelableOtaDisplayState::writeToParcel( Parcel *parcel ) const {
   RETURN_IF_FAILED( parcel->writeUint32( static_cast < uint32_t >( mOtaDisplayState ) ) );
   RETURN_IF_FAILED( parcel->writeUint32( static_cast < uint32_t >( mOtaNotificationAlerts ) ) );

   return ( OK );
}

status_t ParcelableOtaDisplayState::readFromParcel( const Parcel *parcel ) {
   mOtaDisplayState = static_cast < enOtaDisplayState >( parcel->readUint32() );
   mOtaNotificationAlerts = static_cast < enOtaNotificationAlerts >( parcel->readUint32() );

   return ( OK );
}

enOtaDisplayState ParcelableOtaDisplayState::getOtaDisplayState() const {
   return ( mOtaDisplayState );
}

void ParcelableOtaDisplayState::setOtaDisplayState( const enOtaDisplayState otaDisplayState ) {
   mOtaDisplayState = otaDisplayState;
}

enOtaNotificationAlerts ParcelableOtaDisplayState::getOtaNotificationAlerts() const {
   return ( mOtaNotificationAlerts );
}

void ParcelableOtaDisplayState::setOtaNotificationAlerts( const enOtaNotificationAlerts OtaNotificationAlerts ) {
   mOtaNotificationAlerts = OtaNotificationAlerts;
}

}  // namespace hmi
}  // namespace fota

