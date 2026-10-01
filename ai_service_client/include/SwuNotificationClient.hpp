#pragma once

#include <binder/IBinder.h>
#include <binder/IServiceManager.h>
#include <utils/RefBase.h>
#include <utils/StrongPointer.h>
#include <swu/FcSwUpdateSrv/IFcSwUpdateSrv.h>
#include "SwuUpdateCallback.hpp"
#include "TcpNotificationSender.hpp"

#include <atomic>
#include <memory>
#include <string>
#include <vector>

namespace bosch {
namespace aiservice {

struct SystemDetails {
    std::string productClass;
    std::string primaryOs;
    std::vector<std::string> secondaryOs;
};

class SwuNotificationClient : public android::RefBase {
public:
    explicit SwuNotificationClient(const std::string& serviceName = "FcSwUpdateSrv",
                                   std::shared_ptr<TcpNotificationSender> tcpSender = nullptr);
    virtual ~SwuNotificationClient();

    // Connection lifecycle
    bool connect(int maxRetries = 5, int retryDelayMs = 1000);
    void disconnect();
    bool isConnected() const;

    // =========================================================================
    // AI Diagnostic APIs (Server-driven Request / Response)
    // =========================================================================

    /**
     * @brief API 1: Collects system details (product_class, primary_os, secondary_os).
     * @return SystemDetails structure containing target platform information.
     */
    SystemDetails getSystemInformation() const;

    /**
     * @brief API 1 Helper: Collects system details and transmits them to the server over TCP.
     * @return true if payload queued for transmission, false otherwise.
     */
    bool sendSystemInformation();

    /**
     * @brief API 2: Retrieves and packages required log files based on requested artifact tags.
     * Runs `logcat -d -s <tag>` for each requested artifact tag, packages them into an archive,
     * base64-encodes the archive, and transmits it to the AI server over TCP.
     *
     * @param requestedArtifacts List of artifact/log tag names (e.g. "update_engine_logs", "logcat_logs").
     * @return true if logs collected and archive dispatched successfully, false otherwise.
     */
    bool getRequiredFiles(const std::vector<std::string>& requestedArtifacts);

    /**
     * @brief Handles incoming command/event messages received from the AI Diagnostic Server.
     * @param jsonMessage Raw JSON message string received over TCP.
     */
    void handleServerMessage(const std::string& jsonMessage);

    // Callback management
    void setUpdateCallback(android::sp<SwuUpdateCallback> callback);
    android::sp<SwuUpdateCallback> getUpdateCallback() const;

    // TCP Sender management
    void setTcpSender(std::shared_ptr<TcpNotificationSender> tcpSender);
    std::shared_ptr<TcpNotificationSender> getTcpSender() const;

    // Internal death handling
    void handleServiceDied();

private:
    class ServiceDeathRecipient : public android::IBinder::DeathRecipient {
    public:
        explicit ServiceDeathRecipient(SwuNotificationClient* client) : m_client(client) {}
        void binderDied(const android::wp<android::IBinder>& who) override {
            if (m_client) {
                m_client->handleServiceDied();
            }
        }
    private:
        SwuNotificationClient* m_client;
    };

    static std::string readFileBytes(const std::string& path, size_t maxBytes);
    static std::string base64Encode(const std::string& input);

    std::string m_serviceName;
    std::shared_ptr<TcpNotificationSender> m_tcpSender;
    android::sp<android::IBinder> m_binder;
    android::sp<swu::FcSwUpdateSrv::IFcSwUpdateSrv> m_service;
    android::sp<SwuUpdateCallback> m_callback;
    android::sp<ServiceDeathRecipient> m_deathRecipient;
    std::atomic<bool> m_connected{false};
};

} // namespace aiservice
} // namespace bosch
