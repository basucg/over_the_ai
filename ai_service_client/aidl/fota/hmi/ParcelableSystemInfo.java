/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableSystemInfo.java
  * @brief       This file has definitions/implementations for ParcelableSystemInfo.java
  * @authors     unn5hc
  * @copyright   (C) 2023 Robert Bosch Engineering and Business Solutions Limited.
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

public class ParcelableSystemInfo implements Parcelable
{

public static final Parcelable.Creator < ParcelableSystemInfo > CREATOR = new Parcelable.Creator < ParcelableSystemInfo >() {
   @Override
   public ParcelableSystemInfo createFromParcel( Parcel source ) {
      return ( new ParcelableSystemInfo( source ) );
   }

   @Override
   public ParcelableSystemInfo [] newArray( int size ) {
      return ( new ParcelableSystemInfo[size] );
   }

};
private String mSerialNumber;
private String mSoftwareVersion;
private String mSoftwareID;

public ParcelableSystemInfo( String serialNumber,
                             String softwareVersion,
                             String softwareID ) {
   this.mSerialNumber      = serialNumber;
   this.mSoftwareVersion   = softwareVersion;
   this.mSoftwareID        = softwareID;
}

protected ParcelableSystemInfo( Parcel in ) {
   this.mSerialNumber      = in.readString();
   this.mSoftwareVersion   = in.readString();
   this.mSoftwareID        = in.readString();
}

public String getSerialNumber() {
   return ( mSerialNumber );
}

public void setSerialNumber( String serialNumber ) {
   this.mSerialNumber = serialNumber;
}

public String getSoftwareVersion() {
   return ( mSoftwareVersion );
}

public void setSoftwareVersion( String softwareVersion ) {
   this.mSoftwareVersion = softwareVersion;
}

public String getSoftwareID() {
   return ( mSoftwareID );
}

public void setSoftwareID( String softwareID ) {
   this.mSoftwareID = softwareID;
}

@Override
public int describeContents() {
   return ( 0 );
}

@Override
public void writeToParcel( Parcel dest,
                           int    flags ) {
   dest.writeString( this.mSerialNumber );
   dest.writeString( this.mSoftwareVersion );
   dest.writeString( this.mSoftwareID );
}

}

