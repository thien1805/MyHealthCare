// src/pages/Doctor-dashboard/Doctor-patient/hooks/useDoctorPatientList.js
import { useState, useEffect } from "react";
import { getDoctorPatients } from "../../../../api/doctorPatientAPI";

export function useDoctorPatientList() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await getDoctorPatients();
        // Tuỳ backend trả về:
        //  - Array: [ {...}, {...} ]
        //  - Hoặc object có results: { results: [...], count: ... }
        const rawList = Array.isArray(data) ? data : data.results || [];

        // Chỉ giữ bệnh nhân có appointment đã completed
        const confirmedPatients = rawList.filter((item) => {
          const appts =
            item.appointments ||
            item.appointment_list ||
            item.appointment_history ||
            [];
          return appts.some(
            (a) => (a.status || "").toLowerCase() === "completed"
          );
        });

        // Map dữ liệu API → dữ liệu UI (dựa trên ERD Users + Patient)
        const mapped = confirmedPatients.map((item, index) => ({
          id: item.patient_id || item.id || index,
          name:
            item.full_name ||
            item.name ||
            `${item.first_name || ""} ${item.last_name || ""}`.trim(),
          gender: item.gender || "Unknown",
          number: item.phone_num || item.phone || item.phone_number || "-",
          age: item.age || item.age_years || "-", // nếu backend có tuổi
          email: item.email || "-",
          avatarColor: "#4ba8dd",
          medicalRecords: item.medical_records || [],
        }));

        setPatients(mapped);
      } catch (err) {
        console.error("Failed to load patients:", err);
        setError("Failed to load patients.");
        setPatients([]); // không dùng mock nữa
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  const filteredPatients = patients.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  return {
    search,
    setSearch,
    page,
    setPage,
    patients: filteredPatients,
    loading,
    error,
  };
}
