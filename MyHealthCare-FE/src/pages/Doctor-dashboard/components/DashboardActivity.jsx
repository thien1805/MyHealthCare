import React from "react";

export default function DashboardActivity({ activity }) {
  const labels = activity?.labels || [];
  const points = activity?.points || [];

  const polyPoints =
    points.length > 0
      ? points.map((p) => `${p.x},${p.y}`).join(" ")
      : "0,35 100,35";

  return (
    <div className="dd-activity-card">
      <div className="dd-card-header">
        <h3>Recent Activity</h3>
      </div>
      <div className="dd-activity-chart">
        <svg viewBox="0 0 100 40" preserveAspectRatio="none">
          <polyline
            points={polyPoints}
            fill="none"
            strokeWidth="2"
            className="dd-chart-line"
          />
          <line
            x1="0"
            y1="35"
            x2="100"
            y2="35"
            className="dd-chart-axis"
          />
        </svg>
        <div className="dd-chart-labels">
          {labels.map((label) => (
            <span key={label}>{label}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
