#pragma once

#include <binder/IBinder.h>
#include <binder/IServiceManager.h>
#include <utils/RefBase.h>
#include <utils/StrongPointer.h>
#include <fota/hmi/BnOtaHmiServiceCallback.h>
#include <fota/hmi/IOtaHmiService.h>
#include "TcpNotificationSender.hpp"

#include <atomic>
#include <memory>
#include <string>

namespace bosch {
namespace aiservice {

class FotaHmiNotificationClient : public android::RefBase {
public:
    explicit FotaHmiNotificationClient(const std::string& serviceName = "fota.hmi.HmiService",
                                       std::shared_ptr<TcpNotificationSender> tcpSender = nullptr);
    virtual ~FotaHmiNotificationClient();

    bool connect(int maxRetries = 5, int retryDelayMs = 1000);
    void disconnect();
    bool isConnected() const;

    void setTcpSender(std::shared_ptr<TcpNotificationSender> tcpSender);
    std::shared_ptr<TcpNotificationSender> getTcpSender() const;

    void handleServiceDied();
    void reconnectInBackground();

    /** Handles the server's request_ota_logs command; returns false for any other message. */
    bool handleServerMessage(const std::string& jsonMessage);

private:
    class FotaHmiCallback;

    bool sendOtaLogs();

    class ServiceDeathRecipient : public android::IBinder::DeathRecipient {
    public:
        explicit ServiceDeathRecipient(FotaHmiNotificationClient* client) : m_client(client) {}
        void binderDied(const android::wp<android::IBinder>& who) override {
            (void)who;
            if (m_client) {
                m_client->handleServiceDied();
            }
        }
    private:
        FotaHmiNotificationClient* m_client;
    };

    static std::string string16ToStdString(const android::String16& value);
    static std::string escapeJson(const std::string& input);
    static uint32_t m_otaCheckForUpdateErrorCode;
    std::string m_serviceName;
    std::shared_ptr<TcpNotificationSender> m_tcpSender;
    android::sp<android::IBinder> m_binder;
    android::sp<fota::hmi::IOtaHmiService> m_service;
    android::sp<fota::hmi::IOtaHmiServiceCallback> m_callback;
    android::sp<ServiceDeathRecipient> m_deathRecipient;
    std::atomic<bool> m_connected{false};
    std::atomic<bool> m_reconnecting{false};
};

} // namespace aiservice
} // namespace bosch
