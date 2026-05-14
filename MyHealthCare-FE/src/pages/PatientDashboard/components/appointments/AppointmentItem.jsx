import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "../../../../hooks/useTranslation";

const STATUS_COLORS = {
  upcoming: "pd-status--upcoming",
  pending: "pd-status--upcoming",
  booked: "pd-status--upcoming",
  confirmed: "pd-status--upcoming",
  completed: "pd-status--completed",
  cancelled: "pd-status--cancelled",
};

export default function AppointmentItem({ appt, recordId, onCancel, isCancelling }) {
  const navigate = useNavigate();
  const { t, getLocale } = useTranslation();
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState("");

  const STATUS_LABELS = {
    upcoming: t("patient.upcoming"),
    booked: t("patient.upcoming"),
    pending: t("patient.upcoming"),
    confirmed: t("patient.upcoming"),
    completed: t("patient.completed"),
    cancelled: t("patient.cancelled"),
  };

  const handleViewRecord = () => {
    // Navigate to appointment detail page
    navigate(`/patient/appointment/${appt.id}`);
  };

  const status = appt.status?.toLowerCase?.() || "upcoming";
  const statusLabel = STATUS_LABELS[status] || appt.status || "Unknown";
  const statusColor = STATUS_COLORS[status] || "";

  // Can only cancel upcoming appointments
  const canCancel = ["upcoming", "pending", "confirmed", "booked"].includes(status);

  const handleCancelClick = () => {
    setShowCancelModal(true);
  };

  const handleConfirmCancel = () => {
    if (onCancel) {
      onCancel(appt.id, cancelReason || "Cancelled by patient");
    }
    setShowCancelModal(false);
    setCancelReason("");
  };

  const handleCloseModal = () => {
    setShowCancelModal(false);
    setCancelReason("");
  };

  // Format date for display - use current language
  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(getLocale(), {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  // Format time for display
  const formatTime = (timeStr) => {
    if (!timeStr) return "N/A";
    // If already in HH:MM format, return as is
    if (/^\d{2}:\d{2}$/.test(timeStr)) return timeStr;
    // If HH:MM:SS format, remove seconds
    if (/^\d{2}:\d{2}:\d{2}$/.test(timeStr)) return timeStr.slice(0, 5);
    return timeStr;
  };

  const isHistory = ["completed", "cancelled"].includes(status);

  return (
    <>
      <div className={`pd-appointment-card ${status === 'cancelled' ? 'pd-appointment-card--cancelled' : ''}`}>
        <div className="pd-appointment-left">
          <div className="pd-avatar-circle">
            <span>{appt.doctorName?.charAt(0) || "?"}</span>
          </div>
          <div className="pd-appointment-doctor-info">
            <div className="pd-doc-name">{appt.doctorName || "Unknown Doctor"}</div>
            <div className="pd-doc-specialty">{t("patient.doctorAt")} {appt.specialty || "General"}</div>
            {isHistory && appt.reason && (
              <div className="pd-appointment-reason">{appt.reason}</div>
            )}
          </div>
        </div>

        <div className="pd-appointment-info">
          <div className="pd-appointment-meta">
            <span className="pd-appointment-label">{t("patient.date")}:</span>
            <span className="pd-appointment-value">{formatDate(appt.date)}</span>
          </div>
          {!isHistory && (
            <div className="pd-appointment-meta">
              <span className="pd-appointment-label">{t("patient.time")}:</span>
              <span className="pd-appointment-value">{formatTime(appt.time)}</span>
            </div>
          )}
        </div>

        <div className="pd-appointment-actions">
          <span className={`pd-status-badge ${statusColor}`}>
            {statusLabel}
          </span>
          
          <button
            type="button"
            className="pd-detail-btn"
            onClick={handleViewRecord}
          >
            {t("patient.viewDetail")}
          </button>

          {canCancel && (
            <button
              type="button"
              className="pd-cancel-btn-small"
              onClick={handleCancelClick}
              disabled={isCancelling}
            >
              {isCancelling ? "..." : "✕"}
            </button>
          )}
        </div>
      </div>

      {/* Cancel Confirmation Modal */}
      {showCancelModal && (
        <div className="pd-modal-overlay" onClick={handleCloseModal}>
          <div className="pd-modal" onClick={(e) => e.stopPropagation()}>
            <h3 className="pd-modal-title">{t("patient.cancelAppointment")}</h3>
            <p className="pd-modal-text">
              {t("patient.cancelConfirmText")} <strong>{appt.doctorName}</strong> - <strong>{formatDate(appt.date)}</strong> - <strong>{formatTime(appt.time)}</strong>?
            </p>
            
            <label className="pd-modal-label">
              {t("patient.cancelReason")}
            </label>
            <textarea
              className="pd-modal-textarea"
              placeholder={t("patient.enterReason")}
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              rows={3}
            />

            <div className="pd-modal-actions">
              <button
                type="button"
                className="pd-secondary-btn"
                onClick={handleCloseModal}
              >
                {t("patient.keepAppointment")}
              </button>
              <button
                type="button"
                className="pd-danger-btn"
                onClick={handleConfirmCancel}
                disabled={isCancelling}
              >
                {isCancelling ? t("common.loading") : t("patient.yesCancel")}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
