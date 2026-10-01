/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableDynamicHMIInfo.java
  * @brief       This file has definitions/implementations for ParcelableDynamicHMIInfo.java
  * @authors     bcd2kor, unn5hc
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

public class ParcelableDynamicHMIInfo implements Parcelable {
    public static final Parcelable.Creator<ParcelableDynamicHMIInfo> CREATOR = new Parcelable.Creator<ParcelableDynamicHMIInfo>() {
            @Override
            public ParcelableDynamicHMIInfo createFromParcel(Parcel source) {
                return (new ParcelableDynamicHMIInfo(source));
            }

            @Override
            public ParcelableDynamicHMIInfo[] newArray(int size) {
                return (new ParcelableDynamicHMIInfo[size]);
            }
        };

    private int mDownloadProgressPercentage;
    private int mInstallationProgressPercentage;
    private int mActivationProgressPercentage;
    private int mOtaCheckForUpdateErrorCode;
    private String mOtaCheckForUpdateErrorDescription; // maybe no need at HMI application
    private int mOtaDownloadErrorCode;
    private String mOtaDownloadErrorDescription; // maybe no need at HMI application
    private int mInstallErrorCode;
    private String mInstallErrorDescription; // maybe no need at HMI application
    private int mActivationErrorCode;
    private String mActivationErrorDescription; // maybe no need at HMI application
    private int mSwUpdateErrorCode;
    private String mSwUpdateErrorDescription; // maybe no need at HMI application
    private int mUsbCheckForUpdateErrorCode;
    private String mUsbCheckForUpdateErrorDescription; // maybe no need at HMI application
    private int mUsbDownloadErrorCode;
    private String mUsbDownloadErrorDescription; // maybe no need at HMI application


    public ParcelableDynamicHMIInfo(int downloadProgressPercentage, int installationProgressPercentage,
        int activationProgressPercentage, int OtaCheckForUpdateErrorCode, String OtaCheckForUpdateErrorDescription,
        int otadownloadErrorCode, String otadownloadErrorDescription, int installErrorCode,
        String installErrorDescription, int activationErrorCode, String activationErrorDescription ,
        int swUpdateErrorCode, String SwUpdateErrorDescription, int UsbCheckForUpdateErrorCode,
        String UsbCheckForUpdateErrorDescription, int UsbDownloadErrorCode, String UsbDownloadErrorDescription) {
        this.mDownloadProgressPercentage = downloadProgressPercentage;
        this.mInstallationProgressPercentage = installationProgressPercentage;
        this.mActivationProgressPercentage = activationProgressPercentage;
        this.mOtaCheckForUpdateErrorCode = OtaCheckForUpdateErrorCode;
        this.mOtaCheckForUpdateErrorDescription = OtaCheckForUpdateErrorDescription;
        this.mOtaDownloadErrorCode = otadownloadErrorCode;
        this.mOtaDownloadErrorDescription = otadownloadErrorDescription;
        this.mInstallErrorCode = installErrorCode;
        this.mInstallErrorDescription = installErrorDescription;
        this.mActivationErrorCode = activationErrorCode;
        this.mActivationErrorDescription = activationErrorDescription;
        this.mSwUpdateErrorCode = swUpdateErrorCode;
        this.mSwUpdateErrorDescription = SwUpdateErrorDescription;
        this.mUsbCheckForUpdateErrorCode = UsbCheckForUpdateErrorCode;
        this.mUsbCheckForUpdateErrorDescription = UsbCheckForUpdateErrorDescription;
        this.mUsbDownloadErrorCode = UsbDownloadErrorCode;
        this.mUsbDownloadErrorDescription = UsbDownloadErrorDescription;
    }

    protected ParcelableDynamicHMIInfo(Parcel in) {
        this.mDownloadProgressPercentage = in.readInt();
        this.mInstallationProgressPercentage = in.readInt();
        this.mActivationProgressPercentage = in.readInt();
        this.mOtaCheckForUpdateErrorCode = in.readInt();
        this.mOtaCheckForUpdateErrorDescription = in.readString();
        this.mOtaDownloadErrorCode = in.readInt();
        this.mOtaDownloadErrorDescription = in.readString();
        this.mInstallErrorCode = in.readInt();
        this.mInstallErrorDescription = in.readString();
        this.mActivationErrorCode = in.readInt();
        this.mActivationErrorDescription = in.readString();
        this.mSwUpdateErrorCode = in.readInt();
        this.mSwUpdateErrorDescription = in.readString();
        this.mUsbCheckForUpdateErrorCode = in.readInt();
        this.mUsbCheckForUpdateErrorDescription = in.readString();
        this.mUsbDownloadErrorCode = in.readInt();
        this.mUsbDownloadErrorDescription = in.readString();

    }

    @Override
    public int describeContents() {
        return (0);
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeInt(this.mDownloadProgressPercentage);
        dest.writeInt(this.mInstallationProgressPercentage);
        dest.writeInt(this.mActivationProgressPercentage);
        dest.writeInt(this.mOtaCheckForUpdateErrorCode);
        dest.writeString(this.mOtaCheckForUpdateErrorDescription);
        dest.writeInt(this.mOtaDownloadErrorCode);
        dest.writeString(this.mOtaDownloadErrorDescription);
        dest.writeInt(this.mInstallErrorCode);
        dest.writeString(this.mInstallErrorDescription);
        dest.writeInt(this.mActivationErrorCode);
        dest.writeString(this.mActivationErrorDescription);
        dest.writeInt(this.mSwUpdateErrorCode);
        dest.writeString(this.mSwUpdateErrorDescription);
        dest.writeInt(this.mUsbCheckForUpdateErrorCode);
        dest.writeString(this.mUsbCheckForUpdateErrorDescription);
        dest.writeInt(this.mUsbDownloadErrorCode);
        dest.writeString(this.mUsbDownloadErrorDescription);
    }

    public int getDownloadProgressPercentage() {
        return (mDownloadProgressPercentage);
    }

    public void setDownloadProgressPercentage(int downloadProgressPercentage) {
        this.mDownloadProgressPercentage = downloadProgressPercentage;
    }

    public int getInstallationProgressPercentage() {
        return (mInstallationProgressPercentage);
    }

    public void setInstallationProgressPercentage(int installationProgressPercentage) {
        this.mInstallationProgressPercentage = installationProgressPercentage;
    }

    public int setActivationProgressPercentage() {
        return (mActivationProgressPercentage);
    }

    public void setActivationProgressPercentage(int activationProgressPercentage) {
        this.mActivationProgressPercentage = activationProgressPercentage;
    }

    public int getOtaCheckForUpdateErrorCode() {
        return ( mOtaCheckForUpdateErrorCode );
    }
     
    public void setOtaCheckForUpdateErrorCode( int OtaCheckForUpdateErrorCode ) {
        this.mOtaCheckForUpdateErrorCode = OtaCheckForUpdateErrorCode;
    }

    public String getOtaCheckForUpdateErrorDescription() {
        return ( mOtaCheckForUpdateErrorDescription );
    }
     
    public void setOtaCheckForUpdateErrorDescription( String OtaCheckForUpdateErrorDescription ) {
        this.mOtaCheckForUpdateErrorDescription = OtaCheckForUpdateErrorDescription;
    }

    public int getOtaDownloadErrorCode() {
        return ( mOtaDownloadErrorCode );
    }
     
    public void setOtaDownloadErrorCode( int OtaDownloadErrorCode ) {
        this.mOtaDownloadErrorCode = OtaDownloadErrorCode;
    }

    public String getOtaDownloadErrorDescription() {
        return (mOtaDownloadErrorDescription);
    }

    public void setOtaDownloadErrorDescription(String OtaDownloadErrorDescription) {
        this.mOtaDownloadErrorDescription = OtaDownloadErrorDescription;
    }

    public int getInstallErrorCode() {
        return ( mInstallErrorCode );
    }
     
    public void setInstallErrorCode( int installErrorCode ) {
        this.mInstallErrorCode = installErrorCode;
    }

    public String getInstallErrorDescription() {
        return ( mInstallErrorDescription );
    }

    public void setInstallErrorDescription(String installErrorDescription) {
        this.mInstallErrorDescription = installErrorDescription;
    }

    public int getActivationErrorCode() {
        return ( mActivationErrorCode );
    }
     
    public void setActivationErrorCode( int activationErrorCode ) {
        this.mActivationErrorCode = activationErrorCode;
    }

    public String getActivationErrorDescription() {
        return ( mActivationErrorDescription );
    }

    public void setActivationErrorDescription(String activationErrorDescription) {
        this.mActivationErrorDescription = activationErrorDescription;
    }

    public int getSwUpdateErrorCode() {
        return ( mSwUpdateErrorCode );
    }
     
    public void setSwUpdateErrorCode( int SwUpdateErrorCode ) {
        this.mSwUpdateErrorCode = SwUpdateErrorCode;
    }

    public String getSwUpdateErrorDescription() {
        return ( mSwUpdateErrorDescription );
    }

    public void setSwUpdateErrorDescription(String SwUpdateErrorDescription) {
        this.mSwUpdateErrorDescription = SwUpdateErrorDescription;
    }

    public int getUsbCheckForUpdateErrorCode() {
        return ( mUsbCheckForUpdateErrorCode );
    }
     
    public void setUsbCheckForUpdateErrorCode( int UsbCheckForUpdateErrorCode ) {
        this.mUsbCheckForUpdateErrorCode = UsbCheckForUpdateErrorCode;
    }

    public String getUsbCheckForUpdateErrorDescription() {
        return ( mUsbCheckForUpdateErrorDescription );
    }

    public void setUsbCheckForUpdateErrorDescription(String UsbCheckForUpdateErrorDescription) {
        this.mUsbCheckForUpdateErrorDescription = UsbCheckForUpdateErrorDescription;
    }

    public int getUsbDownloadErrorCode() {
        return ( mUsbDownloadErrorCode );
    }
     
    public void setUsbDownloadErrorCode( int UsbDownloadErrorCode ) {
        this.mUsbDownloadErrorCode = UsbDownloadErrorCode;
    }

    public String getUsbDownloadErrorDescription() {
        return ( mUsbDownloadErrorDescription );
    }

    public void setUsbDownloadErrorDescription(String UsbDownloadErrorDescription) {
        this.mUsbDownloadErrorDescription = UsbDownloadErrorDescription;
    }

}

