// src/pages/Doctor-dashboard/components/DashboardCalendar.jsx
import React from "react";
import { useNavigate } from "react-router-dom";

export default function DashboardCalendar({ calendar }) {
  const navigate = useNavigate();

  const daysHeader = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];

  const handleClick = () => {
    navigate("/doctor/calendar");
  };

  const {
    monthLabel = "",
    activeDay,
    dotDays = [],
    days = [],
  } = calendar || {};

  return (
    <div
      className="dd-calendar-card dd-calendar-card--clickable"
      onClick={handleClick}
    >
      <div className="dd-card-header dd-card-header--between">
        <h3>Calendar</h3>
        <span className="dd-calendar-month">{monthLabel}</span>
      </div>

      <div className="dd-calendar-grid">
        {/* hàng thứ trong tuần */}
        {daysHeader.map((d) => (
          <div key={d} className="dd-calendar-day dd-calendar-day--muted">
            {d}
          </div>
        ))}

        {/* các ô ngày */}
        {days.map((day, index) => {
          if (!day) {
            return (
              <div
                key={`empty-${index}`}
                className="dd-calendar-day dd-calendar-day--muted"
              />
            );
          }

          const isActive = day === activeDay;
          const hasDot = dotDays.includes(day);

          let className = "dd-calendar-day";
          if (isActive) className += " dd-calendar-day--active";
          if (hasDot) className += " dd-calendar-day--dot";

          return (
            <div key={day} className={className}>
              {day}
            </div>
          );
        })}
      </div>
    </div>
  );
}
