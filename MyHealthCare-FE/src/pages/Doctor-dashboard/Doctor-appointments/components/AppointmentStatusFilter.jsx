// src/pages/Doctor-dashboard/Doctor-appointments/components/AppointmentStatusFilter.jsx
import React from "react";

const OPTIONS = [
  { id: "all", label: "All" },
  { id: "pending", label: "Pending" },
  { id: "approved", label: "Approved" },
  { id: "completed", label: "Completed" },
  { id: "canceled", label: "Canceled" },
];

export default function AppointmentStatusFilter({ value, onChange }) {
  return (
    <div className="appt-status-filter">
      {OPTIONS.map((opt) => (
        <button
          key={opt.id}
          type="button"
          className={
            "appt-status-pill" +
            (value === opt.id ? " appt-status-pill--active" : "")
          }
          onClick={() => onChange(opt.id)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
