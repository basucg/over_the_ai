/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableOtaUpdateHistory.h
  * @brief       Parcelable Implementation for OtaUpdateHistory.
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

class ParcelableDate : public Parcelable
{
public:
   ParcelableDate();
   ParcelableDate( uint32_t day,
                   uint32_t month,
                   uint32_t year );

   ParcelableDate( const ParcelableDate& other )      = default;
   ParcelableDate& operator=( const ParcelableDate& ) = default;

   ParcelableDate( ParcelableDate&& )                 = default;
   ParcelableDate& operator=( ParcelableDate&& )      = default;

   ~ParcelableDate() override;

   uint32_t getDay() const;

   void setDay( const uint32_t day );

   uint32_t getMonth() const;

   void setMonth( const uint32_t month );

   uint32_t getYear() const;

   void setYear( const uint32_t year );

   status_t writeToParcel( Parcel *parcel ) const;

   status_t readFromParcel( const Parcel *parcel );

private:
   uint32_t mDay;
   uint32_t mMonth;
   uint32_t mYear;
};

class ParcelableOtaUpdateHistory : public Parcelable
{

public:
   /**
     * Default Constructor for ParcelableOtaUpdateHistory
     * @param None
     * @return object of ParcelableOtaUpdateHistory
     */
   ParcelableOtaUpdateHistory();

   /**
     * Constructor for ParcelableOtaUpdateHistory
     * @param defaultVersion, version, date, releaseNotes
     * @return object of ParcelableOtaUpdateHistory
     */
   ParcelableOtaUpdateHistory( bool          defaultVersion,
                               String16      & version,
                               ParcelableDate& date,
                               String16      & releaseNotes);

   ParcelableOtaUpdateHistory( const ParcelableOtaUpdateHistory& other )      = default;
   ParcelableOtaUpdateHistory& operator=( const ParcelableOtaUpdateHistory& ) = default;

   ParcelableOtaUpdateHistory( ParcelableOtaUpdateHistory&& )                 = default;
   ParcelableOtaUpdateHistory& operator=( ParcelableOtaUpdateHistory&& )      = default;

   ~ParcelableOtaUpdateHistory() override;

   status_t writeToParcel( Parcel *parcel ) const override;

   status_t readFromParcel( const Parcel *parcel ) override;

   bool isDefaultVersion() const;

   void setDefaultVersion( const bool isDefaultVersion );

   String16 getVersion() const;

   void setVersion( const String16& version );

   ParcelableDate getDate();

   void setDate( ParcelableDate& date );

   String16 getReleaseNotes() const;

   void setReleaseNotes( const String16& releaseNotes );

private:
   bool mDefaultVersion;
   String16 mVersion;
   ParcelableDate mDate;
   String16 mReleaseNotes;
};

}  // namespace hmi
}  // namespace fota

