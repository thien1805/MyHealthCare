// src/Doctor/components/DashboardStatsGrid.jsx
import React from "react";

export default function DashboardStatsGrid({ stats }) {
  return (
    <div className="dd-stats-grid">
      {stats.map((item) => (
        <div className="dd-stat-card" key={item.id}>
          <div className="dd-stat-header">
            <span className="dd-stat-icon" style={{ backgroundColor: item.color + "20", color: item.color }}>
              {item.icon}
            </span>
          </div>
          <div className="dd-stat-value">{item.value}</div>
          <div className="dd-stat-label">{item.label}</div>
        </div>
      ))}
    </div>
  );
}
