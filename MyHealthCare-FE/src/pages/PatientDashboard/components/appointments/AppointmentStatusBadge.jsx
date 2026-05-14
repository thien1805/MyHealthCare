// src/pages/PatientDashboard/appointments/AppointmentStatusBadge.jsx
import React from "react";

const STATUS_CONFIG = {
  // status từ backend
  booked:    { label: "Pending",   className: "pd-status--pending" }, // map booked -> Pending
  pending:   { label: "Pending",   className: "pd-status--pending" },
  confirmed: { label: "Confirmed", className: "pd-status--confirmed" },
  completed: { label: "Completed", className: "pd-status--completed" },
  cancelled: { label: "Cancelled", className: "pd-status--cancelled" },
  no_show:   { label: "No-show",   className: "pd-status--noshow" },   // thêm status no_show
};

export default function AppointmentStatusBadge({ status }) {
  const key = typeof status === "string" ? status.toLowerCase() : "";
  const cfg =
    STATUS_CONFIG[key] ||
    {
      label: status || "Unknown",
      className: "pd-status--unknown",
    };

  return (
    <span className={`pd-status-badge ${cfg.className}`}>
      {cfg.label}
    </span>
  );
}
