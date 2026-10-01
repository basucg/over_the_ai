/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableDate.java
  * @brief       This file has definitions/implementations for ParcelableDate.java
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

public class ParcelableDate implements Parcelable
{

public static final Parcelable.Creator < ParcelableDate > CREATOR = new Parcelable.Creator < ParcelableDate >() {
   @Override
   public ParcelableDate createFromParcel( Parcel source ) {
      return ( new ParcelableDate( source ) );
   }

   @Override
   public ParcelableDate [] newArray( int size ) {
      return ( new ParcelableDate[size] );
   }

};
private int mDay;
private int mMonth;
private int mYear;

public ParcelableDate( int mDay,
                       int mMonth,
                       int mYear ) {
   this.mDay   = mDay;
   this.mMonth = mMonth;
   this.mYear  = mYear;
}

protected ParcelableDate( Parcel in ) {
   this.mDay   = in.readInt();
   this.mMonth = in.readInt();
   this.mYear  = in.readInt();
}

public int getDay() {
   return ( mDay );
}

public void setDay( int mDay ) {
   this.mDay = mDay;
}

public int getMonth() {
   return ( mMonth );
}

public void setMonth( int mMonth ) {
   this.mMonth = mMonth;
}

public int getYear() {
   return ( mYear );
}

public void setYear( int mYear ) {
   this.mYear = mYear;
}

@Override
public int describeContents() {
   return ( 0 );
}

@Override
public void writeToParcel( Parcel dest,
                           int    flags ) {
   dest.writeInt( this.mDay );
   dest.writeInt( this.mMonth );
   dest.writeInt( this.mYear );
}

}

