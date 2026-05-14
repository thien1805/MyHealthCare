import React from "react";
import { useTranslation } from "../../../../hooks/useTranslation";

const statusKeys = {
  all: "patient.all",
  pending: "patient.pending",
  confirmed: "patient.confirmed",
  completed: "patient.completed",
  cancelled: "patient.cancelled",
};

export default function AppointmentStatusFilter({
  statusOptions,
  activeStatus,
  onChange,
}) {
  const { t } = useTranslation();

  return (
    <div className="pd-status-filter">
      {statusOptions.map((opt) => (
        <button
          key={opt.id}
          type="button"
          className={
            "pd-status-filter-pill" +
            (activeStatus === opt.id ? " pd-status-filter-pill--active" : "")
          }
          onClick={() => onChange(opt.id)}
        >
          {statusKeys[opt.id] ? t(statusKeys[opt.id]) : opt.label}
        </button>
      ))}
    </div>
  );
}
