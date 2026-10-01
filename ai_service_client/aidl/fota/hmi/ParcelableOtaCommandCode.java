/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableOtaCommandCode.java
  * @brief       This file has definitions/implementations for ParcelableOtaCommandCode.java
  * @authors     hrd3kor
  * @copyright   (C) 2020 Robert Bosch Engineering and Business Solutions Limited.
  *              The reproduction, distribution and utilization of this file as
  *              well as the communication of its contents to others without express
  *              authorization is prohibited. Offenders will be held liable for the
  *              payment of damages. All rights reserved in the event of the grant
  *              of a patent, utility model or design.
  * @}
  */

package fota.hmi;

import android.os.Parcel;
import android.os.Parcelable;

public class ParcelableOtaCommandCode implements Parcelable
{
public static final Parcelable.Creator < ParcelableOtaCommandCode > CREATOR = new Parcelable.Creator < ParcelableOtaCommandCode >() {
   @Override
   public ParcelableOtaCommandCode createFromParcel( Parcel source ) {
      return ( new ParcelableOtaCommandCode( source ) );
   }

   @Override
   public ParcelableOtaCommandCode [] newArray( int size ) {
      return ( new ParcelableOtaCommandCode[size] );
   }

};
private EnOtaCommandCode mOtaCommandCode;

public ParcelableOtaCommandCode( EnOtaCommandCode otaCommandCode ) {
   this.mOtaCommandCode = otaCommandCode;
}

protected ParcelableOtaCommandCode( Parcel in ) {
   int tmpMOtaCommandCode = in.readInt();

   this.mOtaCommandCode = tmpMOtaCommandCode == - 1 ? null : EnOtaCommandCode.values()[tmpMOtaCommandCode];
}

@Override
public int describeContents() {
   return ( 0 );
}

@Override
public void writeToParcel( Parcel dest,
                           int    flags ) {
   dest.writeInt( this.mOtaCommandCode == null ? - 1 : this.mOtaCommandCode.ordinal() );
}

public EnOtaCommandCode getOtaCommandCode() {
   return ( mOtaCommandCode );
}

public void setOtaCommandCode( EnOtaCommandCode otaCommandCode ) {
   this.mOtaCommandCode = otaCommandCode;
}

public enum EnOtaCommandCode
{
   GET_UPDATE_HISTORY,
   CHECK_FOR_UPDATES,
   UPDATE_VIA_USB,
   CHECK_FOR_UPDATES_CANCELLED,
   DOWNLOAD_CONSENT_ACCEPTED,
   DOWNLOAD_CONSENT_CANCELLED,
   DOWNLOAD_CANCELLED,
   ACTIVATE_CONSENT_ACCEPTED,
   ACTIVATE_POSTPONED,
   AUTO_PKG_NOTIFY_VIEW,
   AUTO_PKG_NOTIFY_LATER,
   NONE
}
}

