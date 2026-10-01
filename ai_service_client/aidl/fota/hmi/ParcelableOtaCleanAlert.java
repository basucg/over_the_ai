/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableOtaCleanAlert.java
  * @brief       This file has definitions/implementations for ParcelableOtaCleanAlert.java
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

public class ParcelableOtaCleanAlert implements Parcelable
{
public static final Parcelable.Creator < ParcelableOtaCleanAlert > CREATOR = new Parcelable.Creator < ParcelableOtaCleanAlert >() {
   @Override
   public ParcelableOtaCleanAlert createFromParcel( Parcel source ) {
      return ( new ParcelableOtaCleanAlert( source ) );
   }

   @Override
   public ParcelableOtaCleanAlert [] newArray( int size ) {
      return ( new ParcelableOtaCleanAlert[size] );
   }

};
private EnOtaCleanAlert mOtaCleanAlert;

public ParcelableOtaCleanAlert( EnOtaCleanAlert OtaCleanAlert ) {
   this.mOtaCleanAlert = OtaCleanAlert;
}

protected ParcelableOtaCleanAlert( Parcel in ) {
   int tmpMOtaCleanAlert = in.readInt();

   this.mOtaCleanAlert = tmpMOtaCleanAlert == - 1 ? null : EnOtaCleanAlert.values()[tmpMOtaCleanAlert];
}

@Override
public int describeContents() {
   return ( 0 );
}

@Override
public void writeToParcel( Parcel dest,
                           int    flags ) {
   dest.writeInt( this.mOtaCleanAlert == null ? - 1 : this.mOtaCleanAlert.ordinal() );
}

public EnOtaCleanAlert getOtaCleanAlert() {
   return ( mOtaCleanAlert );
}

public void setOtaCleanAlert( EnOtaCleanAlert OtaCleanAlert ) {
   this.mOtaCleanAlert = OtaCleanAlert;
}

public enum EnOtaCleanAlert
{
   CLEAN_ALERT_NONE,
   CLEAN_ALERT_ALL,
   CLEAN_ALERT_OTAUpdateAvailable,
   CLEAN_ALERT_USBUpdateAvailable
}
}

