// src/pages/PatientDashboard/hooks/usePatientDashboard.js
import { useState, useEffect, useCallback } from "react";
import {
  getMyProfile,
  getMyAppointments,
} from "../../../api/patientAPI";
import { getMe } from "../../../api/authAPI";
import { useAuth } from "../../../context/AuthContext";
import { cancelAppointment } from "../../../api/appointmentAPI";

function buildStats(appointments = [], records = [], healthStatus = "Good") {
  const upcomingCount = appointments.filter((a) =>
    ["upcoming", "pending", "confirmed", "booked"].includes(a.status)
  ).length;
  const completedCount = appointments.filter(
    (a) => a.status === "completed"
  ).length;
  const medicalRecordCount = records.length;

  return [
    {
      id: "upcoming",
      label: "Upcoming appointments",
      value: upcomingCount,
      icon: "📅",
    },
    {
      id: "records",
      label: "Medical records",
      value: medicalRecordCount,
      icon: "📁",
    },
    {
      id: "visited",
      label: "Completed visits",
      value: completedCount,
      icon: "✅",
    },
    {
      id: "health",
      label: "Health status",
      value: healthStatus,
      icon: "❤️",
      highlight: true,
    },
  ];
}

export function usePatientDashboard() {
  const { user: authUser } = useAuth();
  const [activeTab, setActiveTab] = useState("appointments");

  const [user, setUser] = useState(null);
  const [stats, setStats] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [appointmentTotal, setAppointmentTotal] = useState(0);
  const [appointmentPage, setAppointmentPage] = useState(1);
  const [appointmentPageSize] = useState(5);
  const [records, setRecords] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const [activeStatus, setActiveStatus] = useState("all");

  // Khởi tạo user từ localStorage trước
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const parsed = JSON.parse(storedUser);
        setUser(parsed);
      } catch (e) {
        console.error("Failed to parse stored user:", e);
      }
    }
  }, []);

  const statusOptions = [
    { id: "all", label: "All" },
    { id: "upcoming", label: "Upcoming" },
    { id: "completed", label: "Completed" },
    { id: "cancelled", label: "Cancelled" },
  ];

  useEffect(() => {
    let cancelled = false;

    const isPastAppointment = (appt) => {
      if (!appt?.date || !appt?.time) return false;
      const dt = new Date(`${appt.date}T${appt.time}`);
      return Number.isFinite(dt.getTime()) && dt.getTime() < Date.now();
    };

    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [meRes, , appointmentsRes] =
          await Promise.all([
            getMe(),
            getMyProfile(),
            getMyAppointments({
              page: appointmentPage,
              page_size: appointmentPageSize,
            }),
          ]);

        if (cancelled) return;

        console.log("🔍 [usePatientDashboard] appointmentsRes:", appointmentsRes);

        // Merge user data from /user/me with patient profile
        const patientProfile = {
          // From /user/me response
          id: meRes.id,
          email: meRes.email,
          full_name: meRes.full_name,
          phone_num: meRes.phone_num,
          role: meRes.role,
          is_active: meRes.is_active,
          created_at: meRes.created_at,
          updated_at: meRes.updated_at,
          patient_profile: meRes.patient_profile,
          doctor_profile: meRes.doctor_profile,
          ...meRes, // include all fields from /user/me
        };
        
        console.log("🔍 Patient Profile:", patientProfile);
        console.log("🔍 Full Name:", patientProfile.full_name);
        console.log("🔍 Email:", patientProfile.email);
        
        // Nếu full_name rỗng, thử lấy từ localStorage
        if (!patientProfile.full_name?.trim()) {
          const storedUser = localStorage.getItem('user');
          if (storedUser) {
            try {
              const parsed = JSON.parse(storedUser);
              if (parsed.full_name) {
                patientProfile.full_name = parsed.full_name;
                patientProfile.name = parsed.full_name;
                console.log("🔍 Using full_name from localStorage:", parsed.full_name);
              }
            } catch (e) {
              console.error("Failed to parse stored user:", e);
            }
          }
        }
        
        setUser(patientProfile);

        const appointmentItems =
          appointmentsRes?.results ||
          appointmentsRes?.items ||
          appointmentsRes?.data ||
          appointmentsRes ||
          [];

        const totalAppointments =
          appointmentsRes?.count ??
          appointmentsRes?.total ??
          appointmentsRes?.pagination?.total ??
          appointmentItems.length;

        const mappedAppointments = appointmentItems.map((item) => {
          const rawStatus = (item.status || "").toLowerCase();
          // Normalize old statuses to new system: booked/pending/confirmed -> upcoming
          const normalizedStatus = ["booked", "pending", "confirmed"].includes(rawStatus) 
            ? "upcoming" 
            : rawStatus;
          return {
            id: item.id,  // Backend returns 'id', not 'appointment_id'
            date: item.appointment_date,
            time: item.appointment_time,
            status: normalizedStatus,
            notes: item.notes,
            symptoms: item.symptoms,
            reason: item.reason,
            doctorId: item.doctor?.id,
            doctorName: item.doctor?.full_name || "Unknown doctor",
            doctorTitle: item.doctor?.title || "",
            specialty: item.doctor?.specialization || "",
            department: item.department || null,  // Pass full object for localization
            departmentIcon: item.department?.icon || "",
            room: item.room?.room_number || "",
            estimatedFee: item.estimated_fee,
            location: item.room?.room_number 
              ? `Phòng ${item.room.room_number}` 
              : "MyHealthCare clinic",
            medicalRecord: item.medical_record || null,
          };
        });

        // Auto-cancel past appointments that are still pending/confirmed
        const expiredIds = [];
        const normalizedAppointments = mappedAppointments.map((appt) => {
          const shouldCancel =
            isPastAppointment(appt) &&
            ["pending", "confirmed"].includes(appt.status);
          if (shouldCancel) {
            expiredIds.push(appt.id);
            return { ...appt, status: "cancelled" };
          }
          return appt;
        });

        if (expiredIds.length > 0) {
          // Best effort update backend; ignore errors per item
          Promise.allSettled(
            expiredIds.map((id) =>
              cancelAppointment(id, "Auto-cancelled: appointment time passed.")
            )
          ).catch(() => {});
        }

        setAppointments(normalizedAppointments);
        setAppointmentTotal(totalAppointments || normalizedAppointments.length);

        // Extract medical records from appointments that have them
        const mappedRecords = appointmentItems
          .filter((item) => item.medical_record)
          .map((item) => {
            const rec = item.medical_record;
            return {
              id: rec.record_id || rec.id,
              appointmentId: item.id,
              doctorId: item.doctor?.id,
              patientId: rec.patient_id,
              diagnosis: rec.diagnosis,
              treatment: rec.treatment,
              notes: rec.notes,
              visitDate: rec.visit_date || item.appointment_date,
              healthStatus: rec.health_status || rec.healthStatus,
            };
          });
        setRecords(mappedRecords);

        // Health metrics - currently not available from backend, initialize empty
        const metricsObj = {};
        setMetrics(metricsObj);

        const sortedByDate = [...mappedRecords].sort((a, b) => {
          const da = new Date(a.visitDate || 0).getTime();
          const db = new Date(b.visitDate || 0).getTime();
          return db - da;
        });
        const latestHealthStatus =
          sortedByDate[0]?.healthStatus ||
          sortedByDate[0]?.diagnosis ||
          sortedByDate[0]?.treatment ||
          "Good";

        setStats(
          buildStats(normalizedAppointments, mappedRecords, latestHealthStatus)
        );
      } catch (err) {
        console.error("Failed to load patient dashboard:", err);

        const status = err?.response?.status;
        const message =
          status === 404
            ? null
            : err?.response?.data?.message ||
              err?.message ||
              "Cannot load data from server.";

        setError(message);

        if (!cancelled) {
          const existingUser = user;

          const fallbackUser = existingUser || (authUser
            ? {
                id: authUser.id,
                email: authUser.email,
                full_name: authUser.full_name,
                phone_num: authUser.phone_num,
                role: authUser.role,
                is_active: authUser.is_active,
                created_at: authUser.created_at,
                updated_at: authUser.updated_at,
            }
            : null
          );
          if (!existingUser || !existingUser.full_name){
            setUser(fallbackUser);
          }
          setAppointments([]);
          setRecords([]);
          setMetrics(null);
          setStats(buildStats([], [], "Good"));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, [authUser, appointmentPage, appointmentPageSize, refreshKey]);

  // Function to refresh appointments
  const refreshAppointments = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  const tabs = [
    { id: "appointments", label: "Appointments" }, // now history
    { id: "records", label: "Medical records" },
    { id: "profile", label: "Profile" },
  ];

  const filteredAppointments =
    activeStatus === "all"
      ? appointments
      : appointments.filter((a) => a.status === activeStatus);

  return {
    user,
    stats,
    tabs,
    appointments: filteredAppointments,
    rawAppointments: appointments,
    appointmentPage,
    appointmentTotal,
    appointmentPageSize,
    setAppointmentPage,
    records,
    metrics,
    activeTab,
    setActiveTab,
    statusOptions,
    activeStatus,
    setActiveStatus,
    loading,
    error,
    refreshAppointments,
  };
}
