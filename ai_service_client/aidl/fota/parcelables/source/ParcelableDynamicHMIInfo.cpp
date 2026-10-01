/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableDynamicHMIInfo.cpp
  * @brief       Parcelable Implementation for DynamicHMIInfo.
  * @authors     bcd2kor, unn5hc
  * @copyright   (C) 2023 Robert Bosch Engineering and Business Solutions Limited.
  *              The reproduction, distribution and utilization of this file as
  *              well as the communication of its contents to others without express
  *              authorization is prohibited. Offenders will be held liable for the
  *              payment of damages. All rights reserved in the event of the grant
  *              of a patent, utility model or design.
  * @}
  */

#include "ParcelableDynamicHMIInfo.h"
#include <binder/Parcel.h>
#include "OtaCommon.h"
//#include "Logger.h"

namespace fota {
namespace hmi {

ParcelableDynamicHMIInfo::ParcelableDynamicHMIInfo() :
   mDownloadProgressPercentage ( 0 ),
   mInstallationProgressPercentage( 0 ),
   mActivationProgressPercentage( 0 ),
   mOtaCheckForUpdateErrorCode( 0 ),
   mOtaCheckForUpdateErrorDescription( "" ),
   mOtaDownloadErrorCode( 0 ),
   mOtaDownloadErrorDescription( "" ),
   mInstallErrorCode( 0 ),
   mInstallErrorDescription( "" ),
   mActivationErrorCode( 0 ),
   mActivationErrorDescription( "" ),
   mSwUpdateErrorCode( 0 ),
   mSwUpdateErrorDescription( "" ),
   mUsbCheckForUpdateErrorCode( 0 ),
   mUsbCheckForUpdateErrorDescription( "" ),
   mUsbDownloadErrorCode( 0 ),
   mUsbDownloadErrorDescription( "" ) {
}


ParcelableDynamicHMIInfo::ParcelableDynamicHMIInfo( uint32_t   downloadProgressPercentage,
                                                   uint32_t   installationProgressPercentage,
                                                   uint32_t   activationProgressPercentage,
                                                   uint32_t   otaCheckForUpdateErrorCode,
                                                   String16 & otaCheckForUpdateErrorDescription,
                                                   uint32_t   otadownloadErrorCode,
                                                   String16 & otadownloadErrorDescription,
                                                   uint32_t   installErrorCode,
                                                   String16 & installErrorDescription,
                                                   uint32_t   activationErrorCode,
                                                   String16 & activationErrorDescription,
                                                   uint32_t   swUpdateErrorCode,   
                                                   String16   swUpdateErrorDescription,
                                                   uint32_t   usbCheckForUpdateErrorCode,
                                                   String16   usbCheckForUpdateErrorDescription,
                                                   uint32_t   usbDownloadErrorCode,
                                                   String16   usbDownloadErrorDescription ) :
   mDownloadProgressPercentage( downloadProgressPercentage ),
   mInstallationProgressPercentage( installationProgressPercentage ),
   mActivationProgressPercentage( activationProgressPercentage ),
   mOtaCheckForUpdateErrorCode( otaCheckForUpdateErrorCode ),
   mOtaCheckForUpdateErrorDescription( otaCheckForUpdateErrorDescription ),
   mOtaDownloadErrorCode( otadownloadErrorCode ),
   mOtaDownloadErrorDescription( otadownloadErrorDescription ),
   mInstallErrorCode( installErrorCode ),
   mInstallErrorDescription( installErrorDescription ),
   mActivationErrorCode( activationErrorCode ),
   mActivationErrorDescription( activationErrorDescription ),
   mSwUpdateErrorCode( swUpdateErrorCode ),
   mSwUpdateErrorDescription( swUpdateErrorDescription ),
   mUsbCheckForUpdateErrorCode( usbCheckForUpdateErrorCode ),
   mUsbCheckForUpdateErrorDescription( usbCheckForUpdateErrorDescription ),
   mUsbDownloadErrorCode( usbDownloadErrorCode ),
   mUsbDownloadErrorDescription( usbDownloadErrorDescription ) {

}

ParcelableDynamicHMIInfo::~ParcelableDynamicHMIInfo() {

}

uint32_t ParcelableDynamicHMIInfo::getDownloadProgressPercentage() const {
   return ( mDownloadProgressPercentage );
}

void ParcelableDynamicHMIInfo::setDownloadProgressPercentage( const uint32_t downloadProgressPercentage ) {
   mDownloadProgressPercentage = downloadProgressPercentage;
}

uint32_t ParcelableDynamicHMIInfo::getInstallationProgressPercentage() const {
   return ( mInstallationProgressPercentage );
}

void ParcelableDynamicHMIInfo::setInstallationProgressPercentage( const uint32_t installationProgressPercentage ) {
   mInstallationProgressPercentage = installationProgressPercentage;
}

uint32_t ParcelableDynamicHMIInfo::getActivationProgressPercentage() const {
   return ( mActivationProgressPercentage );
}

void ParcelableDynamicHMIInfo::setActivationProgressPercentage( const uint32_t ActivationProgressPercentage ) {
   mActivationProgressPercentage = ActivationProgressPercentage;
}

uint32_t ParcelableDynamicHMIInfo::getOtaCheckForUpdateErrorCode() const {
   return ( mOtaCheckForUpdateErrorCode );
}

void ParcelableDynamicHMIInfo::setOtaCheckForUpdateErrorCode( const uint32_t OtaCheckForUpdateErrorCode ) {
   mOtaCheckForUpdateErrorCode = OtaCheckForUpdateErrorCode;
}

String16 ParcelableDynamicHMIInfo::getOtaCheckForUpdateErrorDescription() const {
   return ( mOtaCheckForUpdateErrorDescription );
}

void ParcelableDynamicHMIInfo::setOtaCheckForUpdateErrorDescription( const String16& OtaCheckForUpdateErrorDescription ) {
   mOtaCheckForUpdateErrorDescription = OtaCheckForUpdateErrorDescription;
}

uint32_t ParcelableDynamicHMIInfo::getOtaDownloadErrorCode() const {
   return ( mOtaDownloadErrorCode );
}

void ParcelableDynamicHMIInfo::setOtaDownloadErrorCode( const uint32_t OtaDownloadErrorCode ) {
   mOtaDownloadErrorCode = OtaDownloadErrorCode;
}

String16 ParcelableDynamicHMIInfo::getOtaDownloadErrorDescription() const {
   return ( mOtaDownloadErrorDescription );
}

void ParcelableDynamicHMIInfo::setOtaDownloadErrorDescription( const String16& otadownloadErrorDescription ) {
   mOtaDownloadErrorDescription = otadownloadErrorDescription;
}

uint32_t ParcelableDynamicHMIInfo::getInstallErrorCode() const {
   return ( mInstallErrorCode );
}

void ParcelableDynamicHMIInfo::setInstallErrorCode( const uint32_t installErrorCode ) {
   mInstallErrorCode = installErrorCode;
}

String16 ParcelableDynamicHMIInfo::getInstallErrorDescription() const {
   return ( mInstallErrorDescription );
}

void ParcelableDynamicHMIInfo::setInstallErrorDescription( const String16& installErrorDescription ) {
   mInstallErrorDescription = installErrorDescription;
}

uint32_t ParcelableDynamicHMIInfo::getActivationErrorCode() const {
   return ( mActivationErrorCode );
}

void ParcelableDynamicHMIInfo::setActivationErrorCode( const uint32_t activationErrorCode ) {
   mActivationErrorCode = activationErrorCode;
}

String16 ParcelableDynamicHMIInfo::getActivationErrorDescription() const {
   return ( mActivationErrorDescription );
}

void ParcelableDynamicHMIInfo::setActivationErrorDescription( const String16& activationErrorDescription ) {
   mActivationErrorDescription = activationErrorDescription;
}

uint32_t ParcelableDynamicHMIInfo::getSwUpdateErrorCode() const {
   return ( mSwUpdateErrorCode );
}

void ParcelableDynamicHMIInfo::setSwUpdateErrorCode( const uint32_t SwUpdateErrorCode ) {
   mSwUpdateErrorCode = SwUpdateErrorCode;
}

String16 ParcelableDynamicHMIInfo::getSwUpdateErrorDescription() const {
   return ( mSwUpdateErrorDescription );
}

void ParcelableDynamicHMIInfo::setSwUpdateErrorDescription( const String16& SwUpdateErrorDescription ) {
   mSwUpdateErrorDescription = SwUpdateErrorDescription;
}

uint32_t ParcelableDynamicHMIInfo::getUsbCheckForUpdateErrorCode() const {
   return ( mUsbCheckForUpdateErrorCode );
}

void ParcelableDynamicHMIInfo::setUsbCheckForUpdateErrorCode( const uint32_t UsbCheckForUpdateErrorCode ) {
   mUsbCheckForUpdateErrorCode = UsbCheckForUpdateErrorCode;
}

String16 ParcelableDynamicHMIInfo::getUsbCheckForUpdateErrorDescription() const {
   return ( mUsbCheckForUpdateErrorDescription );
}

void ParcelableDynamicHMIInfo::setUsbCheckForUpdateErrorDescription( const String16& UsbCheckForUpdateErrorDescription ) {
   mUsbCheckForUpdateErrorDescription = UsbCheckForUpdateErrorDescription;
}

uint32_t ParcelableDynamicHMIInfo::getUsbDownloadErrorCode() const {
   return ( mUsbDownloadErrorCode );
}

void ParcelableDynamicHMIInfo::setUsbDownloadErrorCode( const uint32_t UsbDownloadErrorCode ) {
   mUsbDownloadErrorCode = UsbDownloadErrorCode;
}

String16 ParcelableDynamicHMIInfo::getUsbDownloadErrorDescription() const {
   return ( mUsbDownloadErrorDescription );
}

void ParcelableDynamicHMIInfo::setUsbDownloadErrorDescription( const String16& UsbDownloadErrorDescription ) {
   mUsbDownloadErrorDescription = UsbDownloadErrorDescription;
}

status_t ParcelableDynamicHMIInfo::writeToParcel( Parcel *parcel ) const {
   RETURN_IF_FAILED( parcel->writeUint32( mDownloadProgressPercentage ) );
   RETURN_IF_FAILED( parcel->writeUint32( mInstallationProgressPercentage ) );
   RETURN_IF_FAILED( parcel->writeUint32( mActivationProgressPercentage ) );
   RETURN_IF_FAILED( parcel->writeUint32( mOtaCheckForUpdateErrorCode ) );
   RETURN_IF_FAILED( parcel->writeString16( mOtaCheckForUpdateErrorDescription ) );
   RETURN_IF_FAILED( parcel->writeUint32( mOtaDownloadErrorCode ) );
   RETURN_IF_FAILED( parcel->writeString16( mOtaDownloadErrorDescription ) );
   RETURN_IF_FAILED( parcel->writeUint32( mInstallErrorCode ) );
   RETURN_IF_FAILED( parcel->writeString16( mInstallErrorDescription ) );
   RETURN_IF_FAILED( parcel->writeUint32( mActivationErrorCode ) );
   RETURN_IF_FAILED( parcel->writeString16( mActivationErrorDescription ) );
   RETURN_IF_FAILED( parcel->writeUint32( mSwUpdateErrorCode ) );
   RETURN_IF_FAILED( parcel->writeString16( mSwUpdateErrorDescription ) );
   RETURN_IF_FAILED( parcel->writeUint32( mUsbCheckForUpdateErrorCode ) );
   RETURN_IF_FAILED( parcel->writeString16( mUsbCheckForUpdateErrorDescription ) );
   RETURN_IF_FAILED( parcel->writeUint32( mUsbDownloadErrorCode ) );
   RETURN_IF_FAILED( parcel->writeString16( mUsbDownloadErrorDescription ) );

   return ( OK );
}

status_t ParcelableDynamicHMIInfo::readFromParcel( const Parcel *parcel ) {
   RETURN_IF_FAILED( parcel->readUint32( &mDownloadProgressPercentage ) );
   RETURN_IF_FAILED( parcel->readUint32( &mInstallationProgressPercentage ) );
   RETURN_IF_FAILED( parcel->readUint32( &mActivationProgressPercentage ) );
   RETURN_IF_FAILED( parcel->readUint32( &mOtaCheckForUpdateErrorCode ) );
   RETURN_IF_FAILED( parcel->readString16( &mOtaCheckForUpdateErrorDescription ) );
   RETURN_IF_FAILED( parcel->readUint32( &mOtaDownloadErrorCode ) );
   RETURN_IF_FAILED( parcel->readString16( &mOtaDownloadErrorDescription ) );
   RETURN_IF_FAILED( parcel->readUint32( &mInstallErrorCode ) );
   RETURN_IF_FAILED( parcel->readString16( &mInstallErrorDescription ) );
   RETURN_IF_FAILED( parcel->readUint32( &mActivationErrorCode ) );
   RETURN_IF_FAILED( parcel->readString16( &mActivationErrorDescription ) );
   RETURN_IF_FAILED( parcel->readUint32( &mSwUpdateErrorCode ) );
   RETURN_IF_FAILED( parcel->readString16( &mSwUpdateErrorDescription ) );
   RETURN_IF_FAILED( parcel->readUint32( &mUsbCheckForUpdateErrorCode ) );
   RETURN_IF_FAILED( parcel->readString16( &mUsbCheckForUpdateErrorDescription ) );
   RETURN_IF_FAILED( parcel->readUint32( &mUsbDownloadErrorCode ) );
   RETURN_IF_FAILED( parcel->readString16( &mUsbDownloadErrorDescription ) );

   return ( OK );
}
}  // namespace hmi
}  // namespace fota
