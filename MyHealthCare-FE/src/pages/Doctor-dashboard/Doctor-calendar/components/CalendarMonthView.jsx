// src/pages/Doctor-dashboard/Doctor-calendar/components/CalendarMonthView.jsx
import React from "react";

const DAYS_HEADER = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function CalendarMonthView({
  monthLabel,
  days,
  eventsByDay,
  todayDay,
  onSelectDay,
  onPrev,
  onNext,
  onToday,
}) {
  return (
    <div className="cal-main-card">
      {/* HEADER: month + nút Today + prev/next */}
      <div className="cal-header">
        <div className="cal-header-left">
          <button
            type="button"
            className="cal-today-btn"
            onClick={onToday}
          >
            Today
          </button>
          <button
            type="button"
            className="cal-nav-btn"
            onClick={onPrev}
          >
            ‹
          </button>
          <span className="cal-month-label">{monthLabel}</span>
          <button
            type="button"
            className="cal-nav-btn"
            onClick={onNext}
          >
            ›
          </button>
        </div>
      </div>

      {/* GRID WEEKDAYS */}
      <div className="cal-grid">
        {DAYS_HEADER.map((d) => (
          <div key={d} className="cal-grid-header">
            {d}
          </div>
        ))}

        {/* DAYS + EVENTS */}
        {days.map((day, index) => {
          if (!day) {
            return (
              <div
                key={`empty-${index}`}
                className="cal-day-cell cal-day-cell--empty"
              />
            );
          }

          const isToday = todayDay === day;
          const dayEvents = eventsByDay[day] || [];

          return (
            <div
              key={`day-${day}-${index}`}
              className={
                "cal-day-cell" + (isToday ? " cal-day-cell--today" : "")
              }
              onClick={() => onSelectDay(day)}
            >
              <div className="cal-day-number">{day}</div>

              <div className="cal-day-events">
                {dayEvents.map((ev) => (
                  <div key={ev.id} className="cal-event">
                    <span className="cal-event-time">{ev.time}</span>
                    <span className="cal-event-name">
                      {ev.patientName}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
