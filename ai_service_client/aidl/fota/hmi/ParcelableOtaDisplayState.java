/**
  * @swcomponent OTA
  * @{
  * @file        ParcelableOtaDisplayState.java
  * @brief       This file has definitions/implementations for ParcelableOtaDisplayState.java
  * @authors     unn5hc, bcd2kor
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

public class ParcelableOtaDisplayState implements Parcelable
{
public static final Parcelable.Creator < ParcelableOtaDisplayState > CREATOR = new Parcelable.Creator < ParcelableOtaDisplayState >() {
   @Override
   public ParcelableOtaDisplayState createFromParcel( Parcel source ) {
      return ( new ParcelableOtaDisplayState( source ) );
   }

   @Override
   public ParcelableOtaDisplayState [] newArray( int size ) {
      return ( new ParcelableOtaDisplayState[size] );
   }

};
private EnOtaDisplayState mOtaDisplayState;
private EnOtaNotificationAlerts mOtaNotificationAlerts;

public ParcelableOtaDisplayState( EnOtaDisplayState otaDisplayState, EnOtaNotificationAlerts otaAlert ) {
   this.mOtaDisplayState = otaDisplayState;
   this.mOtaNotificationAlerts = otaAlert;
}

protected ParcelableOtaDisplayState( Parcel in ) {
   int tOtaDisplayState = in.readInt();
   int tOtaNotificationAlerts = in.readInt();


   this.mOtaDisplayState = tOtaDisplayState == - 1 ? null : EnOtaDisplayState.values()[tOtaDisplayState];
   this.mOtaNotificationAlerts = tOtaNotificationAlerts == - 1 ? null : EnOtaNotificationAlerts.values()[tOtaNotificationAlerts];
}

@Override
public int describeContents() {
   return ( 0 );
}

@Override
public void writeToParcel( Parcel dest,
                           int    flags ) {
   dest.writeInt( this.mOtaDisplayState == null ? - 1 : this.mOtaDisplayState.ordinal() );
   dest.writeInt( this.mOtaNotificationAlerts == null ? - 1 : this.mOtaNotificationAlerts.ordinal() );
}

public EnOtaDisplayState getOtaDisplayState() {
   return ( mOtaDisplayState );
}

public void setOtaDisplayState( EnOtaDisplayState otaDisplayState ) {
   this.mOtaDisplayState = otaDisplayState;
}

public EnOtaNotificationAlerts getOtaNotificationAlerts() {
   return ( mOtaNotificationAlerts );
}

public void setOtaNotificationAlerts( EnOtaNotificationAlerts OtaNotificationAlerts ) {
   this.mOtaNotificationAlerts = OtaNotificationAlerts;
}

public enum EnOtaDisplayState
{
   Idle,
   NoUpdateAvailable,
   UpdateAvailable,
   CheckForUpdateFail,
   DownloadInProgress,
   DownloadFailure,
   DownloadComplete,
   DownloadCancelSuccess,
   InstallInProgress,
   InstallFailure,
   InstallSuccess,          // HMI does not need any action on this enum
   ReadyToActivate,         // this is for wait Activation consent
   ActivationPostponed,
   ActivationConditionsMet, // HMI does not need any action on this enum
   ActivationConditionsNotMet,
   ActivationInProgress,
   ActivationFailure,
   ActivationRebootRequired, //Not Used
   ActivationSuccess,
   ValidUsbNotConnected,
   ValidUsbConnected,     //Not used 
   USBInvCopyResult,     //Check Error code, for Success of Failure 
   AutomaticUpdateViaOTA,
   AutomaticUpdateViaUSB,
   DownloadInterrupt_waitingToReConnect
}

public enum EnOtaNotificationAlerts
{
   None,
   OTAUpdateAvailable,
   USBUpdateAvailable
}

}

