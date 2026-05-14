import React from "react";
import { useTranslation } from "../../../hooks/useTranslation";

const tabKeys = {
  appointments: "patient.appointments",
  records: "patient.medicalRecords",
  profile: "patient.profile",
};

export default function DashboardTabs({ tabs, activeTab, onChange }) {
  const { t } = useTranslation();

  return (
    <div className="pd-tabs-wrapper">
      <div className="pd-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={
              "pd-tab" + (activeTab === tab.id ? " pd-tab--active" : "")
            }
            onClick={() => onChange(tab.id)}
          >
            {tabKeys[tab.id] ? t(tabKeys[tab.id]) : tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}
