// src/pages/Doctor-dashboard/Doctor-calendar/hooks/useDoctorCalendar.js
import { useMemo, useState } from "react";

// tạm thời dùng data giả – sau này sẽ thay bằng API
const demoAppointments = [
  {
    id: 1,
    date: "2025-11-29",
    time: "09:00",
    patientName: "Nguyen Van A",
    status: "approved",
  },
  {
    id: 2,
    date: "2025-11-29",
    time: "14:30",
    patientName: "Tran Thi B",
    status: "pending",
  },
  {
    id: 3,
    date: "2025-11-30",
    time: "08:15",
    patientName: "Le Van C",
    status: "completed",
  },
];

function getMonthInfo(current) {
  const year = current.getFullYear();
  const month = current.getMonth(); // 0-11

  // ngày đầu / cuối tháng
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  // thứ của ngày đầu tháng (0 = Sun)
  const startWeekday = firstDay.getDay();

  const totalDays = lastDay.getDate();

  // tạo mảng 42 ô (7x6) giống calendar
  const cells = [];
  for (let i = 0; i < startWeekday; i++) {
    cells.push(null);
  }
  for (let d = 1; d <= totalDays; d++) {
    cells.push(d);
  }
  while (cells.length < 42) {
    cells.push(null);
  }

  const monthLabel = firstDay.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  return { cells, monthLabel, year, month };
}

export function useDoctorCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);

  const { cells, monthLabel, year, month } = useMemo(
    () => getMonthInfo(currentDate),
    [currentDate]
  );

  // tạm: dùng demoAppointments; sau này dùng data từ API
  const eventsByDay = useMemo(() => {
    const map = {};
    demoAppointments.forEach((ev) => {
      const evDate = new Date(ev.date);
      if (
        evDate.getFullYear() === year &&
        evDate.getMonth() === month
      ) {
        const day = evDate.getDate();
        if (!map[day]) map[day] = [];
        map[day].push(ev);
      }
    });
    return map;
  }, [year, month]);

  const today = new Date();
  const todayKey =
    today.getFullYear() === year && today.getMonth() === month
      ? today.getDate()
      : null;

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const goPrevMonth = () => {
    setCurrentDate(
      (prev) => new Date(prev.getFullYear(), prev.getMonth() - 1, 1)
    );
  };

  const goNextMonth = () => {
    setCurrentDate(
      (prev) => new Date(prev.getFullYear(), prev.getMonth() + 1, 1)
    );
  };

  const handleSelectDay = (day) => {
    if (!day) return;
    const dateObj = new Date(year, month, day);
    setSelectedDate(dateObj);
  };

  return {
    // cho CalendarMonthView
    monthLabel,
    days: cells,              // mảng 42 ô (null hoặc day number)
    eventsByDay,              // { 29: [event1, event2], ... }
    todayDay: todayKey,       // ngày hôm nay trong tháng
    selectedDate,

    // actions
    goToToday,
    goPrevMonth,
    goNextMonth,
    handleSelectDay,
  };
}
