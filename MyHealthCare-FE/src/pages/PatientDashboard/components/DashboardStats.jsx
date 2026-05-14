import React from "react";
import { useTranslation } from "../../../hooks/useTranslation";

const labelKeys = {
  upcoming: "booking.upcomingAppointments",
  records: "patient.medicalRecords",
  visited: "patient.completedVisits",
  health: "patient.healthStatus",
};

const valueKeys = {
  health: {
    Good: "patient.good",
    Excellent: "patient.good",
    "Tốt": "patient.good",
  },
};

export default function DashboardStats({ stats }) {
  const { t } = useTranslation();

  return (
    <div className="pd-stats-grid">
      {stats.map((item) => {
        const translatedLabel = labelKeys[item.id] ? t(labelKeys[item.id]) : item.label;
        const translatedValue = valueKeys[item.id]?.[item.value] 
          ? t(valueKeys[item.id][item.value]) 
          : item.value;

        return (
          <div
            key={item.id}
            className={
              "pd-stat-card" + (item.highlight ? " pd-stat-card--highlight" : "")
            }
          >
            <div className="pd-stat-label">{translatedLabel}</div>
            <div className="pd-stat-value-wrapper">
              <span
                className={
                  "pd-stat-value" + (item.highlight ? " pd-stat-value--green" : "")
                }
              >
                {translatedValue}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
