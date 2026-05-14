// src/pages/PatientDashboard/components/appointments/PatientAppointmentDetailPage.jsx
import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Header from "../../../../components/Header";
import Footer from "../../../../components/Footer";
import { getAppointmentDetail, cancelAppointment, rescheduleAppointment } from "../../../../api/appointmentAPI";
import { useTranslation } from "../../../../hooks/useTranslation";
import { useLanguage } from "../../../../context/LanguageContext";
import { useToast } from "../../../../hooks/useToast";
import "../../PatientDashboard.css";

const STATUS_COLORS = {
  upcoming: { bg: "#dbeafe", border: "#3b82f6", text: "#2563eb" },
  pending: { bg: "#dbeafe", border: "#3b82f6", text: "#2563eb" },
  booked: { bg: "#dbeafe", border: "#3b82f6", text: "#2563eb" },
  confirmed: { bg: "#dbeafe", border: "#3b82f6", text: "#2563eb" },
  completed: { bg: "#dcfce7", border: "#22c55e", text: "#166534" },
  cancelled: { bg: "#fee2e2", border: "#f87171", text: "#b91c1c" },
};

export default function PatientAppointmentDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t, formatDate: tFormatDate, formatTime: tFormatTime, formatDateTime: tFormatDateTime, getLocale } = useTranslation();
  const { getLocalizedName } = useLanguage();
  const toast = useToast();
  const { ToastContainer } = toast;
  const [appointment, setAppointment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState("");
  const [cancelling, setCancelling] = useState(false);
  const [rescheduleData, setRescheduleData] = useState({ newDate: "", newTime: "", reason: "" });
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [rescheduling, setRescheduling] = useState(false);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getAppointmentDetail(id);
        setAppointment(data);
      } catch (err) {
        console.error("Error fetching appointment:", err);
        setError(err?.message || "Failed to load appointment details");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchDetail();
    }
  }, [id]);

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleDateString(getLocale(), {
        weekday: "long",
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return "N/A";
    if (/^\d{2}:\d{2}:\d{2}$/.test(timeStr)) return timeStr.slice(0, 5);
    return timeStr;
  };

  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return "N/A";
    try {
      return new Date(dateTimeStr).toLocaleString(getLocale(), {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateTimeStr;
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return "N/A";
    return `${Number(amount).toLocaleString("vi-VN")} VND`;
  };

  const handleCancel = async () => {
    if (!cancelReason.trim()) {
      toast.error(t("patient.cancelReasonRequired") || "Vui lòng nhập lý do hủy");
      return;
    }

    setCancelling(true);
    try {
      const result = await cancelAppointment(id, cancelReason);
      if (result?.success) {
        toast.success(t("patient.cancelSuccess") || "Hủy hẹn thành công");
        setShowCancelModal(false);
        // Refresh detail
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } else {
        toast.error(result?.message || result?.error || t("patient.cancelFailed") || "Hủy hẹn thất bại");
      }
    } catch (err) {
      console.error("Cancel error:", err);
      toast.error(err?.message || t("patient.cancelFailed") || "Hủy hẹn thất bại");
    } finally {
      setCancelling(false);
    }
  };

  const handleReschedule = async () => {
    if (!rescheduleData.newDate || !rescheduleData.newTime) {
      toast.error(t("patient.fillAllFields") || "Vui lòng chọn ngày và giờ mới");
      return;
    }

    // Validate date is not in the past
    const selectedDate = new Date(rescheduleData.newDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (selectedDate < today) {
      toast.error(t("patient.dateInPast") || "Không thể chọn ngày trong quá khứ");
      return;
    }

    setRescheduling(true);
    try {
      const result = await rescheduleAppointment(id, {
        new_date: rescheduleData.newDate,
        new_time: rescheduleData.newTime,
        reason: rescheduleData.reason || "",
      });
      if (result?.success) {
        toast.success(t("patient.rescheduleSuccess") || "Dời hẹn thành công");
        setShowRescheduleModal(false);
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } else {
        // Handle specific error messages from backend
        const errorMsg = result?.error || result?.message || result?.new_date?.[0] || result?.new_time?.[0];
        toast.error(errorMsg || t("patient.rescheduleFailed") || "Dời hẹn thất bại");
      }
    } catch (err) {
      console.error("Reschedule error:", err);
      // Handle validation errors from backend
      let errorMessage = t("patient.rescheduleFailed") || "Dời hẹn thất bại";
      if (err?.new_date) {
        errorMessage = Array.isArray(err.new_date) ? err.new_date[0] : err.new_date;
      } else if (err?.new_time) {
        errorMessage = Array.isArray(err.new_time) ? err.new_time[0] : err.new_time;
      } else if (err?.error) {
        errorMessage = err.error;
      } else if (err?.message) {
        errorMessage = err.message;
      }
      toast.error(errorMessage);
    } finally {
      setRescheduling(false);
    }
  };

  const getStatusStyle = (status) => {
    const colors = STATUS_COLORS[status?.toLowerCase()] || STATUS_COLORS.pending;
    return {
      backgroundColor: colors.bg,
      borderColor: colors.border,
      color: colors.text,
    };
  };

  const getStatusLabel = (status) => {
    const labels = {
      upcoming: t("patient.upcoming"),
      pending: t("patient.upcoming"),
      booked: t("patient.upcoming"),
      confirmed: t("patient.upcoming"),
      completed: t("patient.completed"),
      cancelled: t("patient.cancelled"),
    };
    return labels[status?.toLowerCase()] || status;
  };

  if (loading) {
    return (
      <>
        <Header />
        <main className="pd-page">
          <div className="pd-container">
            <div className="pd-loading">Loading...</div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  if (error || !appointment) {
    return (
      <>
        <Header />
        <main className="pd-page">
          <div className="pd-container">
            <div className="pd-error">
              <h2>{error || "Appointment not found"}</h2>
              <button
                type="button"
                className="pd-primary-btn"
                onClick={() => navigate("/patient/dashboard?tab=appointments")}
              >
                ← {t("common.back")}
              </button>
            </div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  const status = appointment.status?.toLowerCase();

  return (
    <>
      <Header />
      <main className="pd-page">
        <div className="pd-container pd-detail-container">
          {/* Back button */}
          <button
            type="button"
            className="pd-back-btn"
            onClick={() => navigate("/patient/dashboard?tab=appointments")}
          >
            ← {t("common.back")}
          </button>

          {/* Header */}
          <div className="pd-detail-header">
            <div className="pd-detail-header-top">
              <h1>{t("patient.appointmentDetail")}</h1>
              <span
                className="pd-detail-status"
                style={getStatusStyle(status)}
              >
                {getStatusLabel(status)}
              </span>
            </div>
            {/* Action Buttons - only show for upcoming appointments */}
            {["upcoming", "pending", "booked", "confirmed"].includes(status) && (
              <div className="pd-detail-actions">
                <button
                  type="button"
                  className="pd-btn pd-btn--primary pd-detail-action"
                  onClick={() => setShowRescheduleModal(true)}
                >
                  {t("patient.reschedule") || "Dời lịch hẹn"}
                </button>
                <button
                  type="button"
                  className="pd-btn pd-btn--danger pd-detail-action"
                  onClick={() => setShowCancelModal(true)}
                >
                  {t("patient.cancelAppointment") || "Hủy lịch hẹn"}
                </button>
              </div>
            )}
          </div>

          {/* Main Info Card */}
          <div className="pd-detail-card">
            <div className="pd-detail-section">
              <h3 className="pd-detail-section-title">{t("patient.scheduleInfo")}</h3>
              <div className="pd-detail-grid">
                <div className="pd-detail-item">
                  <span className="pd-detail-label">{t("patient.date")}</span>
                  <span className="pd-detail-value">
                    {formatDate(appointment.appointment_date)}
                  </span>
                </div>
                <div className="pd-detail-item">
                  <span className="pd-detail-label">{t("patient.time")}</span>
                  <span className="pd-detail-value">
                    {formatTime(appointment.appointment_time)}
                  </span>
                </div>
                <div className="pd-detail-item">
                  <span className="pd-detail-label">{t("patient.createdAt")}</span>
                  <span className="pd-detail-value">
                    {formatDateTime(appointment.created_at)}
                  </span>
                </div>
              </div>
            </div>

            <div className="pd-detail-section">
              <h3 className="pd-detail-section-title">{t("patient.doctorInfo")}</h3>
              <div className="pd-detail-grid">
                <div className="pd-detail-item">
                  <span className="pd-detail-label">{t("patient.doctor")}</span>
                  <span className="pd-detail-value">
                    {appointment.doctor?.title} {appointment.doctor?.full_name || "N/A"}
                  </span>
                </div>
                <div className="pd-detail-item">
                  <span className="pd-detail-label">{t("patient.specialty")}</span>
                  <span className="pd-detail-value">
                    {getLocalizedName(appointment.department) || appointment.doctor?.specialization || "N/A"}
                  </span>
                </div>
                {appointment.room && (
                  <div className="pd-detail-item">
                    <span className="pd-detail-label">{t("patient.room")}</span>
                    <span className="pd-detail-value">
                      {appointment.room.room_number}, {t("patient.floor")} {appointment.room.floor}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="pd-detail-section">
              <h3 className="pd-detail-section-title">{t("patient.feeInfo")}</h3>
              <div className="pd-detail-grid">
                <div className="pd-detail-item">
                  <span className="pd-detail-label">{t("patient.consultationFee")}</span>
                  <span className="pd-detail-value pd-detail-value--price">
                    {formatCurrency(appointment.estimated_fee)}
                  </span>
                </div>
                {appointment.service && (
                  <div className="pd-detail-item">
                    <span className="pd-detail-label">{t("patient.service")}</span>
                    <span className="pd-detail-value">
                      {getLocalizedName(appointment.service)} - {formatCurrency(appointment.service.price)}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {(appointment.symptoms || appointment.reason || appointment.notes) && (
              <div className="pd-detail-section">
                <h3 className="pd-detail-section-title">{t("patient.notes")}</h3>
                {appointment.symptoms && (
                  <div className="pd-detail-item pd-detail-item--full">
                    <span className="pd-detail-label">{t("patient.symptoms")}</span>
                    <span className="pd-detail-value">{appointment.symptoms}</span>
                  </div>
                )}
                {appointment.reason && (
                  <div className="pd-detail-item pd-detail-item--full">
                    <span className="pd-detail-label">{t("patient.reason")}</span>
                    <span className="pd-detail-value">{appointment.reason}</span>
                  </div>
                )}
                {appointment.notes && (
                  <div className="pd-detail-item pd-detail-item--full">
                    <span className="pd-detail-label">{t("patient.additionalNotes")}</span>
                    <span className="pd-detail-value">{appointment.notes}</span>
                  </div>
                )}
              </div>
            )}

            {status === "cancelled" && appointment.cancellation_reason && (
              <div className="pd-detail-section pd-detail-section--warning">
                <h3 className="pd-detail-section-title">{t("patient.cancellationInfo")}</h3>
                <div className="pd-detail-item pd-detail-item--full">
                  <span className="pd-detail-label">{t("patient.reason")}</span>
                  <span className="pd-detail-value">{appointment.cancellation_reason}</span>
                </div>
                {appointment.cancelled_at && (
                  <div className="pd-detail-item">
                    <span className="pd-detail-label">{t("patient.cancelledAt")}</span>
                    <span className="pd-detail-value">{formatDateTime(appointment.cancelled_at)}</span>
                  </div>
                )}
              </div>
            )}

            {/* Medical Record if exists */}
            {appointment.medical_record && (
              <div className="pd-detail-section pd-detail-section--success">
                <h3 className="pd-detail-section-title">{t("patient.medicalRecord")}</h3>
                {appointment.medical_record.diagnosis && (
                  <div className="pd-detail-item pd-detail-item--full">
                    <span className="pd-detail-label">{t("patient.diagnosis")}</span>
                    <span className="pd-detail-value">{appointment.medical_record.diagnosis}</span>
                  </div>
                )}
                {appointment.medical_record.prescription && (
                  <div className="pd-detail-item pd-detail-item--full">
                    <span className="pd-detail-label">{t("patient.prescription")}</span>
                    <span className="pd-detail-value pd-detail-value--pre">
                      {appointment.medical_record.prescription}
                    </span>
                  </div>
                )}
                {appointment.medical_record.treatment_plan && (
                  <div className="pd-detail-item pd-detail-item--full">
                    <span className="pd-detail-label">{t("patient.treatmentPlan")}</span>
                    <span className="pd-detail-value">{appointment.medical_record.treatment_plan}</span>
                  </div>
                )}
                {appointment.medical_record.follow_up_date && (
                  <div className="pd-detail-item">
                    <span className="pd-detail-label">{t("patient.followUpDate")}</span>
                    <span className="pd-detail-value">
                      {formatDate(appointment.medical_record.follow_up_date)}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Cancel Modal */}
      {showCancelModal && (
        <div className="pd-modal-overlay" onClick={() => setShowCancelModal(false)}>
          <div className="pd-modal" onClick={(e) => e.stopPropagation()}>
            <div className="pd-modal-header">
              <h2>{t("patient.cancelAppointment") || "Hủy lịch hẹn"}</h2>
              <button
                type="button"
                className="pd-modal-close"
                onClick={() => setShowCancelModal(false)}
              >
                ×
              </button>
            </div>
            <div className="pd-modal-body">
              <p className="pd-modal-description">
                {t("patient.cancelConfirmMessage") || "Bạn có chắc chắn muốn hủy lịch hẹn này không?"}
              </p>
              <div className="pd-form-group">
                <label htmlFor="cancelReason">
                  {t("patient.cancelReason") || "Lý do hủy"} <span className="required">*</span>
                </label>
                <textarea
                  id="cancelReason"
                  className="pd-textarea"
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                  placeholder={t("patient.enterCancelReason") || "Nhập lý do hủy..."}
                  rows={4}
                />
              </div>
            </div>
            <div className="pd-modal-footer">
              <button
                type="button"
                className="pd-btn pd-btn--secondary"
                onClick={() => setShowCancelModal(false)}
                disabled={cancelling}
              >
                {t("common.close") || "Đóng"}
              </button>
              <button
                type="button"
                className="pd-btn pd-btn--danger"
                onClick={handleCancel}
                disabled={cancelling}
              >
                {cancelling 
                  ? (t("common.processing") || "Đang xử lý...") 
                  : (t("patient.confirmCancel") || "Xác nhận hủy")}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reschedule Modal */}
      {showRescheduleModal && (
        <div className="pd-modal-overlay" onClick={() => setShowRescheduleModal(false)}>
          <div className="pd-modal" onClick={(e) => e.stopPropagation()}>
            <div className="pd-modal-header">
              <h2>{t("patient.reschedule") || "Dời lịch hẹn"}</h2>
              <button
                type="button"
                className="pd-modal-close"
                onClick={() => setShowRescheduleModal(false)}
              >
                ×
              </button>
            </div>
            <div className="pd-modal-body">
              <p className="pd-modal-description">
                {t("patient.rescheduleMessage") || "Chọn ngày và giờ mới cho lịch hẹn của bạn."}
              </p>
              <div className="pd-form-group">
                <label htmlFor="newDate">
                  {t("patient.newDate") || "Ngày mới"} <span className="required">*</span>
                </label>
                <input
                  type="date"
                  id="newDate"
                  className="pd-input"
                  value={rescheduleData.newDate}
                  onChange={(e) => setRescheduleData(prev => ({ ...prev, newDate: e.target.value }))}
                  min={new Date().toISOString().split("T")[0]}
                />
              </div>
              <div className="pd-form-group">
                <label htmlFor="newTime">
                  {t("patient.newTime") || "Giờ mới"} <span className="required">*</span>
                </label>
                <input
                  type="time"
                  id="newTime"
                  className="pd-input"
                  value={rescheduleData.newTime}
                  onChange={(e) => setRescheduleData(prev => ({ ...prev, newTime: e.target.value }))}
                />
              </div>
              <div className="pd-form-group">
                <label htmlFor="rescheduleReason">
                  {t("patient.rescheduleReason") || "Lý do dời hẹn"}
                </label>
                <textarea
                  id="rescheduleReason"
                  className="pd-textarea"
                  value={rescheduleData.reason}
                  onChange={(e) => setRescheduleData(prev => ({ ...prev, reason: e.target.value }))}
                  placeholder={t("patient.enterRescheduleReason") || "Nhập lý do dời hẹn (không bắt buộc)..."}
                  rows={3}
                />
              </div>
            </div>
            <div className="pd-modal-footer">
              <button
                type="button"
                className="pd-btn pd-btn--secondary"
                onClick={() => setShowRescheduleModal(false)}
                disabled={rescheduling}
              >
                {t("common.close") || "Đóng"}
              </button>
              <button
                type="button"
                className="pd-btn pd-btn--primary"
                onClick={handleReschedule}
                disabled={rescheduling}
              >
                {rescheduling 
                  ? (t("common.processing") || "Đang xử lý...") 
                  : (t("patient.confirmReschedule") || "Xác nhận dời hẹn")}
              </button>
            </div>
          </div>
        </div>
      )}

      <ToastContainer />
      <Footer />
    </>
  );
}
