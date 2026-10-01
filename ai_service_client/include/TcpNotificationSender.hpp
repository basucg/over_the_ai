#pragma once

#include <string>
#include <mutex>
#include <queue>
#include <thread>
#include <condition_variable>
#include <atomic>
#include <memory>
#include <functional>

namespace bosch {
namespace aiservice {

class TcpNotificationSender {
public:
    using MessageHandler = std::function<void(const std::string&)>;

    TcpNotificationSender(const std::string& host = "192.168.1.100", int port = 9000);
    ~TcpNotificationSender();

    void start();
    void stop();
    void sendNotification(const std::string& jsonPayload);

    void setMessageHandler(MessageHandler handler);

    bool isConnected() const { return m_connected.load(); }
    void updateServerEndpoint(const std::string& host, int port);

private:
    void workerLoop();
    void receiverLoop();
    bool connectToServer();
    void closeSocket();

    std::string m_host;
    int m_port;
    int m_sockfd{-1};
    std::atomic<bool> m_running{false};
    std::atomic<bool> m_connected{false};

    std::queue<std::string> m_queue;
    std::mutex m_mutex;
    std::condition_variable m_cv;
    std::thread m_workerThread;
    std::thread m_receiverThread;

    MessageHandler m_messageHandler;
    std::mutex m_handlerMutex;
};

} // namespace aiservice
} // namespace bosch
