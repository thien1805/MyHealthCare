// src/pages/PatientDashboard/components/records/PatientMedicalRecordDetailPage.jsx
import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Header from "../../../../components/Header";
import Footer from "../../../../components/Footer";
import { getMedicalRecordDetail } from "../../../../api/medicalRecordAPI";
import { cancelAppointment } from "../../../../api/appointmentAPI";

export default function PatientMedicalRecordDetailPage() {
  const { recordId } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!recordId) return;
    let cancelled = false;

    const fetchDetail = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await getMedicalRecordDetail(recordId);
        if (!cancelled) setRecord(res);
      } catch (err) {
        if (!cancelled) {
          console.error("Medical record detail error:", err);
          setError(
            typeof err === "string"
              ? err
              : err?.message || "Failed to load medical record."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchDetail();
    return () => {
      cancelled = true;
    };
  }, [recordId]);

  const fields = [
    { label: "Diagnosis", value: record?.diagnosis },
    { label: "Prescription", value: record?.prescription },
    { label: "Treatment plan", value: record?.treatment_plan },
    { label: "Notes", value: record?.notes },
    { label: "Follow-up date", value: record?.follow_up_date },
  ];

  const vitalSigns = record?.vital_signs || record?.vitals || {};
  const appointmentId = record?.appointment_id || record?.appointmentId;

  const handleCancelAppointment = async () => {
    if (!appointmentId) {
      alert("No appointment id found for this record.");
      return;
    }
    const ok = window.confirm(
      "Are you sure you want to cancel this appointment?"
    );
    if (!ok) return;
    try {
      setUpdating(true);
      await cancelAppointment(appointmentId, "Cancelled from medical record page");
      setRecord((prev) => ({ ...(prev || {}), status: "cancelled" }));
      alert("Appointment cancelled.");
    } catch (err) {
      console.error("Cancel appointment error:", err);
      alert(
        err?.message ||
          err?.error ||
          "Failed to cancel appointment. Please try again."
      );
    } finally {
      setUpdating(false);
    }
  };

  const handleReschedule = () => {
    navigate("/patient/appointments", {
      state: { appointmentId, action: "reschedule" },
    });
  };

  return (
    <>
      <Header />
      <main className="pd-page">
        <div className="pd-card" style={{ marginTop: "16px" }}>
          <div className="pd-profile-header" style={{ marginBottom: 12 }}>
            <div className="pd-profile-main">
              <div className="pd-profile-avatar">
                <span>ℹ️</span>
              </div>
              <div>
                <h3 className="pd-profile-name">
                  Medical record #{recordId || ""}
                </h3>
                <p className="pd-profile-email">
                  View the doctor&apos;s notes for this appointment.
                </p>
              </div>
            </div>
            <Link to="/patient/dashboard?tab=records" className="pd-outline-btn">
              Back to records
            </Link>
          </div>

          {loading && <div className="pd-section-subtitle">Loading...</div>}
          {error && (
            <div className="pd-section-subtitle" style={{ color: "red" }}>
              {error}
            </div>
          )}

          {!loading && !error && (
            <div className="pd-record-detail">
              {fields.map((f) => (
                <p key={f.label}>
                  <strong>{f.label}:</strong>{" "}
                  {f.value ? String(f.value) : "Not provided"}
                </p>
              ))}

              <div style={{ marginTop: 12 }}>
                <strong>Vital signs:</strong>
                <div className="pd-record-vitals">
                  <div>Blood pressure: {vitalSigns.blood_pressure || "N/A"}</div>
                  <div>Temperature: {vitalSigns.temperature || "N/A"}</div>
                  <div>Heart rate: {vitalSigns.heart_rate || "N/A"}</div>
                </div>
              </div>

              <div style={{ marginTop: 16, display: "flex", gap: 10 }}>
                <button
                  type="button"
                  className="pd-outline-btn"
                  onClick={handleReschedule}
                  disabled={!appointmentId || updating}
                >
                  Reschedule
                </button>
                <button
                  type="button"
                  className="pd-outline-btn"
                  onClick={handleCancelAppointment}
                  disabled={!appointmentId || updating}
                >
                  Cancel appointment
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
