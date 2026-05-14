// src/pages/Doctor-dashboard/hooks/useDoctorDashboard.js
import { useState, useEffect } from "react";
import { useAuth } from "../../../context/AuthContext";
import { getMyAppointments } from "../../../api/appointmentAPI";

export function useDoctorDashboard() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [appointments, setAppointments] = useState([]);
  const [error, setError] = useState(null);

  // Fetch real appointments from API
  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        setLoading(true);
        const data = await getMyAppointments({});
        // Handle both array and paginated response
        const list = Array.isArray(data) ? data : data.results || [];
        setAppointments(list);
      } catch (err) {
        console.error("Error fetching appointments:", err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  // Greeting with real doctor name
  const doctorName = user?.full_name || user?.name || "Doctor";
  const greeting = {
    name: doctorName,
    subText: "Have a nice day and don't forget to take care of your health!",
    quote: "Good things take time.",
  };

  // Calculate stats from real data
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth();

  // Today's appointments
  const today = now.toISOString().split("T")[0];
  const todayAppointments = appointments.filter(
    (apt) => apt.appointment_date === today
  );

  // This month's appointments
  const thisMonthAppointments = appointments.filter((apt) => {
    const aptDate = new Date(apt.appointment_date);
    return (
      aptDate.getFullYear() === currentYear &&
      aptDate.getMonth() === currentMonth
    );
  });

  // Upcoming appointments (status = upcoming)
  const upcomingAppointments = appointments.filter(
    (apt) => apt.status === "upcoming"
  );

  // Completed appointments
  const completedAppointments = appointments.filter(
    (apt) => apt.status === "completed"
  );

  // Unique patients
  const uniquePatientIds = new Set(
    appointments.map((apt) => apt.patient?.id).filter(Boolean)
  );

  const formatNumber = (n) =>
    Number(n || 0).toLocaleString("en-US", { maximumFractionDigits: 0 });

  const stats = [
    {
      id: "today",
      label: "Today's Appointments",
      value: formatNumber(todayAppointments.length),
      icon: "📅",
      color: "#3b82f6",
    },
    {
      id: "upcoming",
      label: "Upcoming",
      value: formatNumber(upcomingAppointments.length),
      icon: "⏰",
      color: "#f59e0b",
    },
    {
      id: "completed",
      label: "Completed",
      value: formatNumber(completedAppointments.length),
      icon: "✅",
      color: "#10b981",
    },
    {
      id: "patients",
      label: "Total Patients",
      value: formatNumber(uniquePatientIds.size),
      icon: "👥",
      color: "#8b5cf6",
    },
  ];

  // Build activity chart from last 6 months
  const buildMonthlyActivity = (appts, months = 6) => {
    const buckets = [];

    for (let offset = months - 1; offset >= 0; offset -= 1) {
      const monthDate = new Date(now.getFullYear(), now.getMonth() - offset, 1);
      const month = monthDate.getMonth();
      const year = monthDate.getFullYear();

      const count = appts.filter((appt) => {
        const d = new Date(appt.appointment_date);
        return (
          !Number.isNaN(d.getTime()) &&
          d.getFullYear() === year &&
          d.getMonth() === month
        );
      }).length;

      buckets.push({
        label: monthDate.toLocaleString("en-US", { month: "short" }),
        count,
      });
    }

    const maxValue = Math.max(...buckets.map((b) => b.count), 1);
    const points = buckets.map((bucket, idx) => {
      const x = buckets.length > 1 ? (idx / (buckets.length - 1)) * 100 : 0;
      const baseline = 35;
      const amplitude = 25;
      const normalizedY = baseline - (bucket.count / maxValue) * amplitude;
      return { x: Number(x.toFixed(2)), y: Number(normalizedY.toFixed(2)) };
    });

    return { points, labels: buckets.map((b) => b.label), buckets };
  };

  const activityData = buildMonthlyActivity(appointments, 6);
  const activity = { points: activityData.points, labels: activityData.labels };

  // Calendar data
  const monthLabel = now.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  const activeDay = now.getDate();

  // Get days that have appointments this month
  const dotDays = appointments
    .map((a) => new Date(a.appointment_date))
    .filter(
      (d) =>
        !Number.isNaN(d.getTime()) &&
        d.getFullYear() === currentYear &&
        d.getMonth() === currentMonth
    )
    .map((d) => d.getDate());

  const firstDayOfMonth = new Date(currentYear, currentMonth, 1);
  const firstWeekday = firstDayOfMonth.getDay();
  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

  const days = [];
  for (let i = 0; i < firstWeekday; i += 1) {
    days.push(null);
  }
  for (let d = 1; d <= daysInMonth; d += 1) {
    days.push(d);
  }
  while (days.length % 7 !== 0) {
    days.push(null);
  }

  const calendar = {
    monthLabel,
    activeDay,
    dotDays: [...new Set(dotDays)],
    days,
  };

  // Next upcoming appointment
  const sortedUpcoming = [...upcomingAppointments].sort((a, b) => {
    const dateA = new Date(`${a.appointment_date}T${a.appointment_time}`);
    const dateB = new Date(`${b.appointment_date}T${b.appointment_time}`);
    return dateA - dateB;
  });

  const nextAppointment = sortedUpcoming[0];
  const upcoming = nextAppointment
    ? {
        name: nextAppointment.patient?.full_name || "Unknown Patient",
        dateText: `${new Date(nextAppointment.appointment_date).toLocaleDateString("en-US", {
          day: "numeric",
          month: "long",
          year: "numeric",
        })} - ${nextAppointment.appointment_time?.slice(0, 5) || "N/A"}`,
        symptoms: nextAppointment.symptoms,
      }
    : null;

  // Today's appointment list for dashboard
  const todayList = todayAppointments.map((apt) => ({
    id: apt.id,
    patientName: apt.patient?.full_name || "Unknown",
    time: apt.appointment_time?.slice(0, 5) || "N/A",
    status: apt.status,
    symptoms: apt.symptoms,
  }));

  return {
    loading,
    error,
    greeting,
    stats,
    activity,
    calendar,
    upcoming,
    todayList,
    appointments,
  };
}
