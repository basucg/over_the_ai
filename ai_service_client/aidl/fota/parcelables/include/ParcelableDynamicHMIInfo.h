/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableDynamicHMIInfo.h
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

#pragma once

#include <binder/Parcel.h>
#include <binder/Parcelable.h>

using namespace android;

namespace fota {
namespace hmi {

class ParcelableDynamicHMIInfo : public Parcelable
{

public:
/**
  * Default Constructor for ParcelableDynamicHMIInfo
  * @param None
  * @return object of ParcelableDynamicHMIInfo
  */
   ParcelableDynamicHMIInfo();

/**
  * Constructor for ParcelableDynamicHMIInfo
  * @param downloadProgressPercentage, installationProgressPercentage, downloadErrorCode, downloadErrorDescription,
  *        installErrorCode, installErrorDescription, activationErrorCode, activationErrorDescription
  * @return object of ParcelableDynamicHMIInfo
  */
   ParcelableDynamicHMIInfo( uint32_t   downloadProgressPercentage,
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
                             String16   usbDownloadErrorDescription
                             );

   ParcelableDynamicHMIInfo( const ParcelableDynamicHMIInfo& other )      = default;
   ParcelableDynamicHMIInfo& operator=( const ParcelableDynamicHMIInfo& ) = default;

   ParcelableDynamicHMIInfo( ParcelableDynamicHMIInfo&& )                 = default;
   ParcelableDynamicHMIInfo& operator=( ParcelableDynamicHMIInfo&& )      = default;

   ~ParcelableDynamicHMIInfo() override;

   status_t writeToParcel( Parcel *parcel ) const override;

   status_t readFromParcel( const Parcel *parcel ) override;

   uint32_t getDownloadProgressPercentage() const;

   void setDownloadProgressPercentage( const uint32_t downloadProgressPercentage );

   uint32_t getInstallationProgressPercentage() const;

   void setInstallationProgressPercentage( const uint32_t installationProgressPercentage );

   uint32_t getActivationProgressPercentage() const;

   void setActivationProgressPercentage( const uint32_t ActivationProgressPercentage );

   uint32_t getOtaCheckForUpdateErrorCode() const;

   void setOtaCheckForUpdateErrorCode( const uint32_t OtaCheckForUpdateErrorCode );

   String16 getOtaCheckForUpdateErrorDescription() const;

   void setOtaCheckForUpdateErrorDescription( const String16& OtaCheckForUpdateErrorDescription );  

   uint32_t getOtaDownloadErrorCode() const;

   void setOtaDownloadErrorCode( const uint32_t OtaDownloadErrorCode );

   String16 getOtaDownloadErrorDescription() const;

   void setOtaDownloadErrorDescription( const String16& otadownloadErrorDescription );

   uint32_t getInstallErrorCode() const;

   void setInstallErrorCode( const uint32_t installErrorCode );

   String16 getInstallErrorDescription() const;

   void setInstallErrorDescription( const String16& installErrorDescription );

   uint32_t getActivationErrorCode() const;

   void setActivationErrorCode( const uint32_t activationErrorCode );

   String16 getActivationErrorDescription() const;

   void setActivationErrorDescription( const String16& activationErrorDescription );

   uint32_t getSwUpdateErrorCode() const;

   void setSwUpdateErrorCode( const uint32_t SwUpdateErrorCode );

   String16 getSwUpdateErrorDescription() const;

   void setSwUpdateErrorDescription( const String16& SwUpdateErrorDescription );

   uint32_t getUsbCheckForUpdateErrorCode() const;

   void setUsbCheckForUpdateErrorCode( const uint32_t UsbCheckForUpdateErrorCode );

   String16 getUsbCheckForUpdateErrorDescription() const;

   void setUsbCheckForUpdateErrorDescription( const String16& UsbCheckForUpdateErrorDescription );

   uint32_t getUsbDownloadErrorCode() const;

   void setUsbDownloadErrorCode( const uint32_t UsbDownloadErrorCode );

   String16 getUsbDownloadErrorDescription() const;

   void setUsbDownloadErrorDescription( const String16& UsbDownloadErrorDescription );

private:
  uint32_t mDownloadProgressPercentage;
  uint32_t mInstallationProgressPercentage;
  uint32_t mActivationProgressPercentage;  //For Future Use only, Not used now.
  uint32_t mOtaCheckForUpdateErrorCode;
  String16 mOtaCheckForUpdateErrorDescription; //For Future Use only, Not used now.
  uint32_t mOtaDownloadErrorCode;
  String16 mOtaDownloadErrorDescription; //For Future Use only, Not used now.
  uint32_t mInstallErrorCode;
  String16 mInstallErrorDescription; //For Future Use only, Not used now.
  uint32_t mActivationErrorCode;
  String16 mActivationErrorDescription; //For Future Use only, Not used now.
  uint32_t mSwUpdateErrorCode;   //For Future Use only, Not used now.
  String16 mSwUpdateErrorDescription; //For Future Use only, Not used now.
  uint32_t mUsbCheckForUpdateErrorCode;
  String16 mUsbCheckForUpdateErrorDescription; //For Future Use only, Not used now.
  uint32_t mUsbDownloadErrorCode;
  String16 mUsbDownloadErrorDescription; //For Future Use only, Not used now.
};

}  // namespace hmi
}  // namespace fota

