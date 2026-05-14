import React, { useState, useMemo } from "react";
import AppointmentItem from "./AppointmentItem";
import AppointmentStatusFilter from "./AppointmentStatusFilter";
import { cancelAppointment } from "../../../../api/appointmentAPI";
import { useTranslation } from "../../../../hooks/useTranslation";

export default function AppointmentList({
  appointments,
  records = [],
  statusOptions,
  activeStatus,
  onStatusChange,
  page = 1,
  pageSize = 5,
  total = 0,
  onPageChange,
  toast,
  onRefresh,
}) {
  const [cancellingId, setCancellingId] = useState(null);
  const [sortOrder, setSortOrder] = useState("date-desc"); // default: newest first
  const { t } = useTranslation();

  // Sort function - handle both 'date'/'time' and 'appointment_date'/'appointment_time' field names
  const sortAppointments = (apps) => {
    if (!apps || apps.length === 0) return [];
    
    return [...apps].sort((a, b) => {
      // Handle both field naming conventions
      const dateStrA = a.appointment_date || a.date || "";
      const timeStrA = a.appointment_time || a.time || "00:00";
      const dateStrB = b.appointment_date || b.date || "";
      const timeStrB = b.appointment_time || b.time || "00:00";
      
      // Parse time to ensure proper format (handle HH:MM:SS)
      const timeA = timeStrA.slice(0, 5);
      const timeB = timeStrB.slice(0, 5);
      
      const dateA = new Date(`${dateStrA}T${timeA}:00`);
      const dateB = new Date(`${dateStrB}T${timeB}:00`);
      
      // Check for invalid dates
      if (isNaN(dateA.getTime())) return 1;
      if (isNaN(dateB.getTime())) return -1;
      
      switch (sortOrder) {
        case "date-asc":
          return dateA - dateB;
        case "date-desc":
          return dateB - dateA;
        default:
          return dateB - dateA;
      }
    });
  };

  const filtered =
    activeStatus === "all"
      ? appointments
      : (appointments || []).filter((a) => a.status === activeStatus);

  // Separate appointments into upcoming and history, then sort
  const upcomingAppointments = sortAppointments(
    (filtered || []).filter((a) => 
      ["upcoming", "pending", "booked", "confirmed"].includes(a.status?.toLowerCase())
    )
  );
  const historyAppointments = sortAppointments(
    (filtered || []).filter((a) => 
      ["completed", "cancelled"].includes(a.status?.toLowerCase())
    )
  );

  const totalPages = Math.max(1, Math.ceil((total || 0) / pageSize));
  const showPagination = totalPages > 1 && filtered.length > 0;

  const handlePrev = () => {
    if (page > 1 && onPageChange) onPageChange(page - 1);
  };

  const handleNext = () => {
    if (page < totalPages && onPageChange) onPageChange(page + 1);
  };

  const handleCancelAppointment = async (appointmentId, reason = "Cancelled by patient") => {
    if (!appointmentId) return;
    
    setCancellingId(appointmentId);
    try {
      const result = await cancelAppointment(appointmentId, reason);
      
      if (result?.success) {
        toast?.success(result.message || t("patient.cancelSuccess") || "Appointment cancelled successfully!", 4000);
        // Refresh the appointments list
        if (onRefresh) onRefresh();
      } else {
        toast?.error(result?.error || result?.message || t("patient.cancelFailed") || "Failed to cancel appointment", 5000);
      }
    } catch (err) {
      console.error("Cancel appointment error:", err);
      // Extract error message from backend response
      const errorMessage = 
        err?.message || 
        err?.error || 
        err?.detail ||
        (typeof err === 'string' ? err : t("patient.cancelFailed") || "Failed to cancel appointment. Please try again.");
      toast?.error(errorMessage, 5000);
    } finally {
      setCancellingId(null);
    }
  };

  const startIdx = (page - 1) * pageSize + 1;
  const endIdx = Math.min(total, page * pageSize);

  return (
    <div className="pd-card pd-appointments-card">
      <div className="pd-filter-row">
        <AppointmentStatusFilter
          statusOptions={statusOptions}
          activeStatus={activeStatus}
          onChange={onStatusChange}
        />
        
        <div className="pd-sort-filter">
          <label className="pd-sort-label">{t("patient.sortBy") || "Sắp xếp:"}</label>
          <select
            className="pd-sort-select"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <option value="date-desc">{t("patient.newestFirst") || "Mới nhất"}</option>
            <option value="date-asc">{t("patient.oldestFirst") || "Cũ nhất"}</option>
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="pd-empty-tab">
          {activeStatus === "all" 
            ? t("patient.noAppointmentsYet")
            : t("patient.noAppointmentsInCategory")}
        </div>
      ) : (
        <>
          {/* Upcoming Appointments Section */}
          {upcomingAppointments.length > 0 && (
            <div className="pd-appointments-section">
              <h3 className="pd-section-title">{t("patient.upcomingAppointments")}</h3>
              <p className="pd-section-subtitle">{t("patient.upcomingSubtitle") || "Các cuộc hẹn khám sắp tới của bạn"}</p>
              
              <div className="pd-appointments-list">
                {upcomingAppointments.map((appt) => {
                  const recordForAppt =
                    records.find((r) => r.appointmentId === appt.id) || null;
                  return (
                    <AppointmentItem
                      key={appt.id}
                      appt={appt}
                      recordId={recordForAppt?.id}
                      onCancel={handleCancelAppointment}
                      isCancelling={cancellingId === appt.id}
                    />
                  );
                })}
              </div>
            </div>
          )}

          {/* History Section */}
          {historyAppointments.length > 0 && (
            <div className="pd-appointments-section">
              <h3 className="pd-section-title">{t("patient.appointmentHistory")}</h3>
              <p className="pd-section-subtitle">{t("patient.historySubtitle") || "Các lần khám đã hoàn thành"}</p>
              
              <div className="pd-appointments-list">
                {historyAppointments.map((appt) => {
                  const recordForAppt =
                    records.find((r) => r.appointmentId === appt.id) || null;
                  return (
                    <AppointmentItem
                      key={appt.id}
                      appt={appt}
                      recordId={recordForAppt?.id}
                      onCancel={handleCancelAppointment}
                      isCancelling={cancellingId === appt.id}
                    />
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}

      {showPagination && (
        <div className="pd-pagination">
          <button
            type="button"
            className="pd-secondary-btn"
            onClick={handlePrev}
            disabled={page <= 1}
          >
            ← {t("patient.previous")}
          </button>
          <div className="pd-pagination-meta">
            {t("patient.showingPage")} {page} {t("patient.of")} {totalPages} · {startIdx}-{endIdx} / {total}
          </div>
          <button
            type="button"
            className="pd-secondary-btn"
            onClick={handleNext}
            disabled={page >= totalPages}
          >
            {t("patient.next")} →
          </button>
        </div>
      )}
    </div>
  );
}
