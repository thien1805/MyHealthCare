// src/pages/Doctor-dashboard/Doctor-appointments/components/AppointmentActivityTable.jsx
import React from "react";
import useTranslation from "../../../../hooks/useTranslation";
import { useLanguage } from "../../../../context/LanguageContext";

// Define valid status transitions (matching backend)
const VALID_TRANSITIONS = {
  upcoming: ["completed", "cancelled"],
  completed: [],  // Cannot change completed
  cancelled: [],  // Cannot change cancelled
};

export default function AppointmentActivityTable({
  rows,
  loading,
  error,
  search,
  setSearch,
  statusFilter,
  setStatusFilter,
  dateFilter,
  setDateFilter,
  statusChoices,
  updateStatus,
  onAddRecord,
  toast,
}) {
  const { t, formatDate, formatTime } = useTranslation();
  const { getLocalizedName } = useLanguage();

  const renderStatusLabel = (value) => {
    const found = statusChoices.find((s) => s.value === value);
    return found ? found.label : value;
  };

  // Get valid next statuses for current status
  const getValidStatusOptions = (currentStatus) => {
    const allowedTransitions = VALID_TRANSITIONS[currentStatus] || [];
    // Include current status + allowed transitions
    return statusChoices.filter(
      (s) => s.value === currentStatus || allowedTransitions.includes(s.value)
    );
  };

  const handleStatusChange = async (id, newStatus, currentStatus) => {
    // Don't update if same status
    if (newStatus === currentStatus) return;
    
    const result = await updateStatus(id, newStatus);
    if (result.success) {
      toast?.success?.(`Status updated to ${renderStatusLabel(newStatus)}`);
    } else {
      toast?.error?.(result.error || "Failed to update status");
    }
  };

  return (
    <div className="appt-card">
      {/* HEADER + FILTERS */}
      <div className="appt-header-row">
        <div>
          <h2 className="appt-title">Appointments</h2>
          <p className="appt-subtitle">
            Search and update your patients&apos; appointment status.
          </p>
        </div>

        <div className="appt-header-right">
          {/* search patient */}
          <div className="appt-search-input">
            <span role="img" aria-label="search">
              🔍
            </span>
            <input
              type="text"
              placeholder="Search patient…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* status pills */}
      <div className="appt-status-filter">
        <button
          type="button"
          className={
            "appt-status-pill" +
            (statusFilter === "all" ? " appt-status-pill--active" : "")
          }
          onClick={() => setStatusFilter("all")}
        >
          All
        </button>

        {statusChoices.map((st) => (
          <button
            key={st.value}
            type="button"
            className={
              "appt-status-pill" +
              (statusFilter === st.value ? " appt-status-pill--active" : "")
            }
            onClick={() => setStatusFilter(st.value)}
          >
            {renderStatusLabel(st.value)}
          </button>
        ))}
      </div>

      {/* date filter */}
      <div className="appt-filter-bar">
        <div className="appt-filter-item">
          <span className="appt-filter-label">Date</span>
          <input
            type="date"
            className="appt-date-input"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
          />
        </div>

        <button
          type="button"
          className="appt-reset-btn"
          onClick={() => {
            setSearch("");
            setStatusFilter("all");
            setDateFilter("");
          }}
        >
          Reset filter
        </button>
      </div>

      {/* Loading / Error states */}
      {loading && (
        <div className="appt-loading">Loading appointments...</div>
      )}
      
      {error && (
        <div className="appt-error">{error}</div>
      )}

      {/* TABLE */}
      {!loading && !error && (
        <div className="appt-table-wrapper">
          <table className="appt-table">
            <thead>
              <tr>
                <th>Patient</th>
                <th>Status</th>
                <th>Department</th>
                <th>Notes</th>
                <th>Time</th>
                <th>Date</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 && (
                <tr>
                  <td colSpan={7} className="appt-empty">
                    No appointments found.
                  </td>
                </tr>
              )}

              {rows.map((row) => (
                <tr key={row.id}>
                  <td className="appt-patient-cell">
                    <div className="appt-avatar">
                      {row.patient.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="appt-patient-name">{row.patient}</div>
                      {row.patientEmail && (
                        <div className="appt-patient-email">{row.patientEmail}</div>
                      )}
                    </div>
                  </td>

                  {/* STATUS: select có thể đổi trạng thái */}
                  <td>
                    <select
                      className={`appt-status-select appt-status-select--${row.status}`}
                      value={row.status}
                      onChange={(e) => handleStatusChange(row.id, e.target.value, row.status)}
                      disabled={!VALID_TRANSITIONS[row.status]?.length}
                    >
                      {getValidStatusOptions(row.status).map((st) => (
                        <option key={st.value} value={st.value}>
                          {st.label}
                        </option>
                      ))}
                    </select>
                  </td>

                  <td>{getLocalizedName(row.department, "N/A")}</td>
                  <td>{row.notes || "-"}</td>
                  <td>{formatTime(row.time)}</td>
                  <td>{formatDate(row.date)}</td>
                  <td style={{ textAlign: "right" }}>
                    <button
                      type="button"
                      className={
                        "appt-record-btn" +
                        (["upcoming", "completed", "confirmed"].includes(row.status)
                          ? ""
                          : " appt-record-btn--disabled")
                      }
                      disabled={!["upcoming", "completed", "confirmed"].includes(row.status)}
                      onClick={() => {
                        if (!["upcoming", "completed", "confirmed"].includes(row.status)) return;
                        onAddRecord?.(row._raw || row);
                      }}
                    >
                      {row.medicalRecord ? "View Record" : "Add Record"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
