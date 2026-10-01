/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableOtaUpdateHistory.java
  * @brief       This file has definitions/implementations for ParcelableOtaUpdateHistory.java
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

import fota.hmi.ParcelableDate;

public class ParcelableOtaUpdateHistory implements Parcelable {
    public static final Parcelable.Creator<ParcelableOtaUpdateHistory> CREATOR = new Parcelable.Creator<ParcelableOtaUpdateHistory>() {
            @Override
            public ParcelableOtaUpdateHistory createFromParcel(Parcel source) {
                return (new ParcelableOtaUpdateHistory(source));
            }

            @Override
            public ParcelableOtaUpdateHistory[] newArray(int size) {
                return (new ParcelableOtaUpdateHistory[size]);
            }
        };

    boolean mDefaultVersion;
    String mVersion;
    ParcelableDate mDate;
    String mReleaseNotes;

    public ParcelableOtaUpdateHistory(boolean defaultVersion,
        String version, ParcelableDate date, String releaseNotes) {
        this.mDefaultVersion = defaultVersion;
        this.mVersion = version;
        this.mDate = date;
        this.mReleaseNotes = releaseNotes;
    }

    protected ParcelableOtaUpdateHistory(Parcel in) {
        this.mDefaultVersion = in.readByte() != 0;
        this.mVersion = in.readString();

        final ParcelableDate dateParcel = in.readTypedObject(ParcelableDate.CREATOR);
        this.mDate = dateParcel;
        this.mReleaseNotes = in.readString();
    }

    @Override
    public int describeContents() {
        return (0);
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeByte(this.mDefaultVersion ? (byte)1 : (byte)0);
        dest.writeString(this.mVersion);
        dest.writeParcelable(this.mDate, flags);
        dest.writeString(this.mReleaseNotes);
    }

    public boolean isDefaultVersion() {
        return ( mDefaultVersion );
     }

     public void setDefaultVersion( boolean isDefaultVersion ) {
        this.mDefaultVersion = isDefaultVersion;
     }

    public String getVersion() {
        return (mVersion);
    }

    public void setVersion(String mVersion) {
        this.mVersion = mVersion;
    }

    public ParcelableDate getDate() {
        return (mDate);
    }

    public void setDate(ParcelableDate mDate) {
        this.mDate = mDate;
    }

    public String getReleaseNotes() {
        return (mReleaseNotes);
    }

    public void setReleaseNotes(String mReleaseNotes) {
        this.mReleaseNotes = mReleaseNotes;
    }
}
