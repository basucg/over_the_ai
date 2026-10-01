#pragma once

#include <binder/Status.h>
#include <swu/FcSwUpdateSrv/BnUpdateCallback.h>
#include <swu/FcSwUpdateSrv/trUpdState.h>
#include <swu/FcSwUpdateSrv/trUpdProgress.h>
#include <swu/FcSwUpdateSrv/trErrorIds.h>
#include <swu/FcSwUpdateSrv/tenUpdState.h>
#include <swu/FcSwUpdateSrv/tenSwUpdateError.h>
#include "TcpNotificationSender.hpp"

#include <functional>
#include <memory>
#include <string>

namespace bosch {
namespace aiservice {

class SwuUpdateCallback : public swu::FcSwUpdateSrv::BnUpdateCallback {
public:
    using StateCallback = std::function<void(const swu::FcSwUpdateSrv::trUpdState&)>;
    using ProgressCallback = std::function<void(const swu::FcSwUpdateSrv::trUpdProgress&)>;
    using ErrorCallback = std::function<void(const swu::FcSwUpdateSrv::trErrorIds&)>;
    using ResultCallback = std::function<void(const swu::FcSwUpdateSrv::trErrorIds&)>;

    SwuUpdateCallback(std::shared_ptr<TcpNotificationSender> tcpSender = nullptr);
    virtual ~SwuUpdateCallback() = default;

    // Binder callback overrides from IFcSwUpdateSrv
    android::binder::Status onUpdateState(const swu::FcSwUpdateSrv::trUpdState& state) override;
    android::binder::Status onUpdateProgress(const swu::FcSwUpdateSrv::trUpdProgress& progress) override;
    android::binder::Status onUpdateError(const swu::FcSwUpdateSrv::trErrorIds& errors) override;
    android::binder::Status onCancelUpdResult(const swu::FcSwUpdateSrv::trErrorIds& errors) override;
    android::binder::Status onCompleteUpdResult(const swu::FcSwUpdateSrv::trErrorIds& errors) override;

    // Optional event listener hooks
    void setStateListener(StateCallback cb) { m_stateCb = std::move(cb); }
    void setProgressListener(ProgressCallback cb) { m_progressCb = std::move(cb); }
    void setErrorListener(ErrorCallback cb) { m_errorCb = std::move(cb); }
    void setCancelListener(ResultCallback cb) { m_cancelCb = std::move(cb); }
    void setCompleteListener(ResultCallback cb) { m_completeCb = std::move(cb); }

    // TCP Notification Sender configuration
    void setTcpSender(std::shared_ptr<TcpNotificationSender> tcpSender) { m_tcpSender = tcpSender; }

    // Helpers to convert enums to human-readable strings
    static std::string stateToString(swu::FcSwUpdateSrv::tenUpdState state);
    static std::string errorToString(swu::FcSwUpdateSrv::tenSwUpdateError error);
    static std::string string16ToStdString(const android::String16& s);
    static std::string escapeJson(const std::string& input);

private:
    void sendJsonToRemote(const std::string& jsonStr);

    swu::FcSwUpdateSrv::tenUpdState m_previousState;
    swu::FcSwUpdateSrv::tenUpdState m_currentState;

    std::shared_ptr<TcpNotificationSender> m_tcpSender;

    StateCallback m_stateCb;
    ProgressCallback m_progressCb;
    ErrorCallback m_errorCb;
    ResultCallback m_cancelCb;
    ResultCallback m_completeCb;
};

} // namespace aiservice
} // namespace bosch
