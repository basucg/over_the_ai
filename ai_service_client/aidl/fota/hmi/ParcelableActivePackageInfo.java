/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableActivePackageInfo.java
  * @brief       This file has definitions/implementations for ParcelableActivePackageInfo.java
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

public class ParcelableActivePackageInfo implements Parcelable {
    public static final Parcelable.Creator<ParcelableActivePackageInfo> CREATOR = new Parcelable.Creator<ParcelableActivePackageInfo>() {
            @Override
            public ParcelableActivePackageInfo createFromParcel(Parcel source) {
                return (new ParcelableActivePackageInfo(source));
            }

            @Override
            public ParcelableActivePackageInfo[] newArray(int size) {
                return (new ParcelableActivePackageInfo[size]);
            }
        };

    private String mVersion;             // Need in set_gnl_57/68
    private long mPackageSize;            // Need in set_gnl_57/68
    private String mReleaseNotes;        // Need in set_gnl_57/68. It should be What's new field
    private EnCampaignType mCampaignType;
    private EnUpdateType   mUpdateType;
    private int mEstimatedDownloadTime;  // Need in set_gnl_57/68. How to extract it? Don't exist in trOtaPackageInfo struct
    private int mEstimatedInstallationTime;     // Is not needed, to be removed with discussion with HMI
    private int mEstimatedActivateTime;  // Need in set_gnl_59/70. Use in activating step

    public ParcelableActivePackageInfo(String version, long packageSize, String releaseNotes,
        EnCampaignType campaignType, EnUpdateType updateType, int estimatedDownloadTime,
        int estimatedInstallationTime, int estimatedActivateTime) {
        this.mVersion = version;
        this.mPackageSize = packageSize;
        this.mReleaseNotes = releaseNotes;
        this.mCampaignType = campaignType;
        this.mUpdateType = updateType;
        this.mEstimatedDownloadTime = estimatedDownloadTime;
        this.mEstimatedInstallationTime = estimatedInstallationTime;
        this.mEstimatedActivateTime = estimatedActivateTime;
    }

    protected ParcelableActivePackageInfo(Parcel in) {
        this.mVersion = in.readString();
        this.mPackageSize = in.readLong();
        this.mReleaseNotes = in.readString();
        int tmpType = in.readInt();
        if (tmpType >= 0 && tmpType < EnCampaignType.values().length) {
            this.mCampaignType = EnCampaignType.values()[tmpType];
        }
        else
        {
            this.mCampaignType = EnCampaignType.Invalid;  // Handle invalid value safely
        }
        tmpType = in.readInt();
        if (tmpType >= 0 && tmpType < EnUpdateType.values().length) {
            this.mUpdateType = EnUpdateType.values()[tmpType];
        } else {
            this.mUpdateType = EnUpdateType.NA;  // Handle invalid value safely
        }
        this.mEstimatedDownloadTime = in.readInt();
        this.mEstimatedInstallationTime = in.readInt();
        this.mEstimatedActivateTime = in.readInt();
    }

    @Override
    public int describeContents() {
        return (0);
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(this.mVersion);
        dest.writeLong(this.mPackageSize);
        dest.writeString(this.mReleaseNotes);
        dest.writeInt( this.mCampaignType == null ? - 1 : this.mCampaignType.ordinal() );
        dest.writeInt( this.mUpdateType == null ? - 1 : this.mUpdateType.ordinal() );
        dest.writeInt(this.mEstimatedDownloadTime);
        dest.writeInt(this.mEstimatedInstallationTime);
        dest.writeInt(this.mEstimatedActivateTime);
    }

    public String getVersion() {
        return (mVersion);
    }

    public void setVersion(String version) {
        this.mVersion = version;
    }

    public long getPackageSize() {
        return (mPackageSize);
    }

    public void setPackageSize(long packageSize) {
        this.mPackageSize = packageSize;
    }

    public String getReleaseNotes() {
        return (mReleaseNotes);
    }

    public void setReleaseNotes(String releaseNotes) {
        this.mReleaseNotes = releaseNotes;
    }

    public EnCampaignType getCampaignType() {
        return ( mCampaignType );
     }

    public void setCampaignType( EnCampaignType campaignType ) {
        this.mCampaignType = campaignType;
     }

    public EnUpdateType getUpdateType() {
        return ( mUpdateType );
     }

    public void setUpdateType( EnUpdateType updateType ) {
        this.mUpdateType = updateType;
     }

    public int getEstimatedDownloadTime() {
        return (mEstimatedDownloadTime);
    }

    public void setEstimatedDownloadTime(int estimatedDownloadTime) {
        this.mEstimatedDownloadTime = estimatedDownloadTime;
    }

    public int getEstimatedInstallationTime() {
        return (mEstimatedInstallationTime);
    }

    public void setEstimatedInstallationTime(int estimatedInstallationTime) {
        this.mEstimatedInstallationTime = estimatedInstallationTime;
    }

    public int getEstimatedActivateTime() {
        return (mEstimatedActivateTime);
    }

    public void setEstimatedActivateTime(int estimatedActivateTime) {
        this.mEstimatedActivateTime = estimatedActivateTime;
    }

public enum EnCampaignType
{
   Invalid,
   Regular,
   Silent,
   Critical
}

public enum EnUpdateType
{
   NA,
   OTA,
   USB
}
}

