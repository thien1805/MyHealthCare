// src/pages/Doctor-dashboard/Doctor-calendar/DoctorCalendar.jsx
import React from "react";
import "./DoctorCalendar.css";

import DoctorLayout from "../DoctorLayout";
import CalendarMonthView from "./components/CalendarMonthView";
import { useDoctorCalendar } from "./hooks/useDoctorCalendar";

export default function DoctorCalendar() {
  const {
    monthLabel,
    days,
    eventsByDay,
    todayDay,
    selectedDate,
    goToToday,
    goPrevMonth,
    goNextMonth,
    handleSelectDay,
  } = useDoctorCalendar();

  return (
    <DoctorLayout activeMenu="calendar">
      <div className="cal-layout">
        <CalendarMonthView
          monthLabel={monthLabel}
          days={days}
          eventsByDay={eventsByDay}
          todayDay={todayDay}
          onSelectDay={handleSelectDay}
          onPrev={goPrevMonth}
          onNext={goNextMonth}
          onToday={goToToday}
        />
      </div>
    </DoctorLayout>
  );
}
