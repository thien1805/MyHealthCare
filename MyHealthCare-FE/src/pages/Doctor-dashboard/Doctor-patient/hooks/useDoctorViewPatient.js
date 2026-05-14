// src/pages/Doctor-dashboard/Doctor-patient/hooks/useDoctorViewPatient.js
import { useEffect, useState } from "react";
import { getPatientById } from "../../../../api/doctorPatientAPI";

export function useDoctorViewPatient(patientId) {
  const [patient, setPatient] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Map data từ API -> object patient cho UI
  const mapPatient = (data) => {
    const firstName = data.first_name || data.firstName || "";
    const lastName = data.last_name || data.lastName || "";

    return {
      firstName,
      lastName,
      email: data.email || "",
      phone: data.phone_num || data.phone || "",
      age: data.age ? String(data.age) : "",
      gender: data.gender || "",
      records: "No files attached", // TODO: map từ field real (ví dụ attachments_count, medical_records...)
    };
  };

  // TODO: sau này thay bằng API history cho patient (appointments, bills, prescriptions)
  const buildMockHistory = () => {
    return [
      {
        id: 1,
        type: "Appointment",
        billType: "-",
        title: "Checkup",
        date: "14 Feb 2019",
        invoice: "-",
        status: "Pending",
        statusType: "pending",
      },
      {
        id: 2,
        type: "Transaction",
        billType: "Cash",
        title: "-",
        date: "14 Feb 2019",
        invoice: "#126234",
        status: "Cancelled",
        statusType: "cancelled",
      },
      {
        id: 3,
        type: "Transaction",
        billType: "Cash",
        title: "-",
        date: "14 Feb 2019",
        invoice: "#143243",
        status: "Complete",
        statusType: "complete",
      },
      {
        id: 4,
        type: "Prescription",
        billType: "-",
        title: "Severe Fever",
        date: "14 Feb 2019",
        invoice: "-",
        status: "-",
        statusType: "none",
      },
    ];
  };

  useEffect(() => {
    const fetchPatient = async () => {
      if (!patientId) {
        setLoading(false);
        setError("Missing patient id");
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const data = await getPatientById(patientId);
        const mappedPatient = mapPatient(data);
        setPatient(mappedPatient);

        // tạm thời dùng mock, sau này đổi sang API lịch sử khám/hoá đơn
        setHistory(buildMockHistory());
      } catch (err) {
        console.error("Failed to load patient detail:", err);
        const message =
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load patient detail.";
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchPatient();
  }, [patientId]);

  return {
    patient,
    history,
    loading,
    error,
  };
}
