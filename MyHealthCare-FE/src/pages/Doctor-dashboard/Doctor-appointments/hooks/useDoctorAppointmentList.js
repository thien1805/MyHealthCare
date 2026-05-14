// src/pages/Doctor-dashboard/Doctor-appointments/hooks/useDoctorAppointmentList.js
import { useMemo, useState, useEffect, useCallback } from "react";
import { 
  getDoctorAppointments, 
  updateAppointmentStatus,
  getServices,
  assignServiceToAppointment 
} from "../../../../api/appointmentAPI";
import { createMedicalRecord } from "../../../../api/medicalRecordAPI";

const STATUS_CHOICES = [
  { value: "upcoming", label: "Upcoming" },
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
];

export function useDoctorAppointmentList() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("");
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  
  // Modal states
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showMedicalRecordModal, setShowMedicalRecordModal] = useState(false);
  const [services, setServices] = useState([]);
  const [loadingServices, setLoadingServices] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Fetch appointments from API
  const fetchAppointments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page,
        pageSize: 20,
      };
      
      if (statusFilter && statusFilter !== "all") {
        params.status = statusFilter;
      }
      
      if (dateFilter) {
        params.dateFrom = dateFilter;
        params.dateTo = dateFilter;
      }
      
      const data = await getDoctorAppointments(params);
      
      // Handle paginated response
      if (data.results) {
        setAppointments(data.results);
        setTotalCount(data.count || 0);
      } else if (Array.isArray(data)) {
        setAppointments(data);
        setTotalCount(data.length);
      } else {
        setAppointments([]);
        setTotalCount(0);
      }
    } catch (err) {
      console.error("Error fetching appointments:", err);
      setError(err?.message || "Failed to load appointments");
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter, dateFilter]);

  useEffect(() => {
    fetchAppointments();
  }, [fetchAppointments]);

  // Fetch services when opening modal
  const fetchServices = async (departmentId) => {
    try {
      setLoadingServices(true);
      const data = await getServices({ departmentId });
      setServices(data.results || data || []);
    } catch (err) {
      console.error("Error fetching services:", err);
      setServices([]);
    } finally {
      setLoadingServices(false);
    }
  };

  // Update status via API
  const updateStatus = async (id, newStatus) => {
    try {
      await updateAppointmentStatus(id, newStatus);
      // Refresh the list
      fetchAppointments();
      return { success: true };
    } catch (err) {
      console.error("Error updating status:", err);
      return { success: false, error: err?.message || "Failed to update status" };
    }
  };

  // Open medical record modal
  const openMedicalRecordModal = (appointment) => {
    setSelectedAppointment(appointment);
    setShowMedicalRecordModal(true);
    // Fetch services for the department
    if (appointment.department?.id) {
      fetchServices(appointment.department.id);
    }
  };

  // Close medical record modal
  const closeMedicalRecordModal = () => {
    setSelectedAppointment(null);
    setShowMedicalRecordModal(false);
    setServices([]);
  };

  // Submit medical record
  const submitMedicalRecord = async (formData) => {
    if (!selectedAppointment) return { success: false, error: "No appointment selected" };
    
    try {
      setSubmitting(true);
      
      // If a service is selected, assign it first
      if (formData.service_id) {
        try {
          await assignServiceToAppointment(selectedAppointment.id, formData.service_id);
        } catch (err) {
          console.error("Error assigning service:", err);
          // Continue even if service assignment fails
        }
      }
      
      // Create medical record
      const recordData = {
        diagnosis: formData.diagnosis,
        prescription: formData.prescription,
        treatment_plan: formData.treatment_plan,
        notes: formData.notes,
        follow_up_date: formData.follow_up_date || null,
        vital_signs: formData.vital_signs || {},
      };
      
      const result = await createMedicalRecord(selectedAppointment.id, recordData);
      
      // Refresh appointments list
      await fetchAppointments();
      closeMedicalRecordModal();
      
      return { success: true, data: result };
    } catch (err) {
      console.error("Error creating medical record:", err);
      return { success: false, error: err?.message || "Failed to create medical record" };
    } finally {
      setSubmitting(false);
    }
  };

  // Filter appointments locally for search
  const rows = useMemo(() => {
    return appointments.filter((appt) => {
      const patientName = appt.patient?.full_name || appt.patient_name || "";
      const matchSearch =
        !search ||
        patientName.toLowerCase().includes(search.trim().toLowerCase());
      return matchSearch;
    }).map((appt) => ({
      id: appt.id,
      patient: appt.patient?.full_name || appt.patient_name || "Unknown",
      patientEmail: appt.patient?.email || "",
      status: appt.status,
      notes: appt.notes || appt.symptoms || appt.reason || "",
      date: appt.appointment_date,
      time: appt.appointment_time,
      department: appt.department,
      service: appt.service,
      estimatedFee: appt.estimated_fee,
      medicalRecord: appt.medical_record,
      createdAt: appt.created_at,
      // Keep full appointment for modal
      _raw: appt,
    }));
  }, [appointments, search]);

  return {
    rows,
    loading,
    error,
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    dateFilter,
    setDateFilter,
    statusChoices: STATUS_CHOICES,
    updateStatus,
    page,
    setPage,
    totalCount,
    refresh: fetchAppointments,
    // Modal related
    selectedAppointment,
    showMedicalRecordModal,
    openMedicalRecordModal,
    closeMedicalRecordModal,
    services,
    loadingServices,
    submitMedicalRecord,
    submitting,
  };
}
