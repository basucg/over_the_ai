/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableOtaUpdateHistory.cpp
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

#include "ParcelableOtaUpdateHistory.h"
#include <binder/Parcel.h>
#include "OtaCommon.h"

namespace fota {
namespace hmi {

ParcelableDate::ParcelableDate() : mDay( 0 ), mMonth( 0 ), mYear( 0 ) {

}

ParcelableDate::ParcelableDate( uint32_t day,
                                uint32_t month,
                                uint32_t year ) : mDay( day ),
   mMonth( month ),
   mYear( year ) {

}

ParcelableDate::~ParcelableDate() {}

uint32_t ParcelableDate::getDay() const {
   return ( mDay );
}

void ParcelableDate::setDay( const uint32_t day ) {
   mDay = day;
}

uint32_t ParcelableDate::getMonth() const {
   return ( mMonth );
}

void ParcelableDate::setMonth( const uint32_t month ) {
   mMonth = month;
}

uint32_t ParcelableDate::getYear() const {
   return ( mYear );
}

void ParcelableDate::setYear( const uint32_t year ) {
   mYear = year;
}

status_t ParcelableDate::writeToParcel( Parcel *parcel ) const {
   RETURN_IF_FAILED( parcel->writeUint32( mDay ) );
   RETURN_IF_FAILED( parcel->writeUint32( mMonth ) );
   RETURN_IF_FAILED( parcel->writeUint32( mYear ) );
   return ( OK );
}

status_t ParcelableDate::readFromParcel( const Parcel *parcel ) {
   RETURN_IF_FAILED( parcel->readUint32( &mDay ) );
   RETURN_IF_FAILED( parcel->readUint32( &mMonth ) );
   RETURN_IF_FAILED( parcel->readUint32( &mYear ) );
   return ( OK );
}

ParcelableOtaUpdateHistory::ParcelableOtaUpdateHistory() : mDefaultVersion( true ),
   mVersion( "" ),
   mDate( 0, 0, 0 ),
   mReleaseNotes( "" ) {
}

ParcelableOtaUpdateHistory::ParcelableOtaUpdateHistory( bool          defaultVersion,
                                                        String16      & version,
                                                        ParcelableDate& date,
                                                        String16      & releaseNotes)
   : mDefaultVersion( defaultVersion ),
   mVersion( version ),
   mDate( date ),
   mReleaseNotes( releaseNotes ){

}

ParcelableOtaUpdateHistory::~ParcelableOtaUpdateHistory() {

}

bool ParcelableOtaUpdateHistory::isDefaultVersion() const {
   return ( mDefaultVersion );
}

void ParcelableOtaUpdateHistory::setDefaultVersion( const bool isDefaultVersion ) {
   this->mDefaultVersion = isDefaultVersion;
}

String16 ParcelableOtaUpdateHistory::getVersion() const {
   return ( mVersion );
}

void ParcelableOtaUpdateHistory::setVersion( const String16& version ) {
   mVersion = version;
}

ParcelableDate ParcelableOtaUpdateHistory::getDate() {
   return ( mDate );
}

void ParcelableOtaUpdateHistory::setDate( ParcelableDate& date ) {
   mDate = date;
}

String16 ParcelableOtaUpdateHistory::getReleaseNotes() const {
   return ( mReleaseNotes );
}

void ParcelableOtaUpdateHistory::setReleaseNotes( const String16& releaseNotes ) {
   mReleaseNotes = releaseNotes;
}

status_t ParcelableOtaUpdateHistory::writeToParcel( Parcel *parcel ) const {
   RETURN_IF_FAILED( parcel->writeBool( mDefaultVersion ) );
   RETURN_IF_FAILED( parcel->writeString16( mVersion ) );
   RETURN_IF_FAILED( parcel->writeParcelable( mDate ) );
   RETURN_IF_FAILED( parcel->writeString16( mReleaseNotes ) );
   return ( OK );
}

status_t ParcelableOtaUpdateHistory::readFromParcel( const Parcel *parcel ) {
   RETURN_IF_FAILED( parcel->readBool( &mDefaultVersion ) );
   RETURN_IF_FAILED( parcel->readString16( &mVersion ) );
   RETURN_IF_FAILED( parcel->readParcelable( &mDate ) );
   RETURN_IF_FAILED( parcel->readString16( &mReleaseNotes ) );
   return ( OK );
}

}  // namespace hmi
}  // namespace fota

