import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useToast } from "../../../../hooks/useToast";
import { useTranslation } from "../../../../hooks/useTranslation";
import "./MedicalRecordDetail.css";
import Header from "../../../../components/Header";
import Footer from "../../../../components/Footer";

export default function MedicalRecordDetail() {
  const { recordId } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { success, error: showError } = useToast();
  const [record, setRecord] = useState(null);
  const [appointment, setAppointment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecord = async () => {
      try {
        setLoading(true);
        // Mock: get record from localStorage or API
        const allRecords = JSON.parse(
          localStorage.getItem("medicalRecords") || "[]"
        );
        const rec = allRecords.find((r) => r.id === recordId);

        if (rec) {
          setRecord(rec);

          // Try to find corresponding appointment
          const allAppointments = JSON.parse(
            localStorage.getItem("appointments") || "[]"
          );
          const appt = allAppointments.find(
            (a) => a.id === rec.appointmentId
          );
          if (appt) {
            setAppointment(appt);
          }
        } else {
          showError("Medical record not found");
          navigate(-1);
        }
      } catch (err) {
        console.error("Error fetching record:", err);
        showError("Failed to load medical record");
      } finally {
        setLoading(false);
      }
    };

    fetchRecord();
  }, [recordId, navigate, showError]);

  if (loading) {
    return (
      <>
        <Header />
        <main className="rec-detail-page">
          <div className="rec-detail-loading">Loading...</div>
        </main>
        <Footer />
      </>
    );
  }

  if (!record) {
    return (
      <>
        <Header />
        <main className="rec-detail-page">
          <div className="rec-detail-error">Medical record not found</div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="rec-detail-page">
        <div className="rec-detail-container">
          <button
            type="button"
            className="rec-detail-back"
            onClick={() => navigate(-1)}
          >
            ← Back
          </button>

          <div className="rec-detail-card">
            <h2 className="rec-detail-title">Medical Record Detail</h2>

            {appointment && (
              <div className="rec-detail-appointment-info">
                <h3 className="rec-detail-subtitle">Appointment Information</h3>
                <div className="rec-detail-grid">
                  <div className="rec-detail-item">
                    <span className="rec-detail-label">Doctor:</span>
                    <span className="rec-detail-value">
                      {appointment.doctorName || "—"}
                    </span>
                  </div>
                  <div className="rec-detail-item">
                    <span className="rec-detail-label">Specialty:</span>
                    <span className="rec-detail-value">
                      {appointment.specialty || "—"}
                    </span>
                  </div>
                  <div className="rec-detail-item">
                    <span className="rec-detail-label">Date:</span>
                    <span className="rec-detail-value">
                      {appointment.date || "—"}
                    </span>
                  </div>
                  <div className="rec-detail-item">
                    <span className="rec-detail-label">Time:</span>
                    <span className="rec-detail-value">
                      {appointment.time || "—"}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="rec-detail-medical-info">
              <h3 className="rec-detail-subtitle">Medical Information</h3>

              <div className="rec-detail-section">
                <label className="rec-detail-section-label">Diagnosis:</label>
                <p className="rec-detail-section-content">
                  {record.diagnosis || "—"}
                </p>
              </div>

              <div className="rec-detail-section">
                <label className="rec-detail-section-label">Treatment:</label>
                <p className="rec-detail-section-content">
                  {record.treatment || "—"}
                </p>
              </div>

              <div className="rec-detail-section">
                <label className="rec-detail-section-label">Health Status:</label>
                <div className="rec-detail-status">
                  <span
                    className={`rec-detail-status-badge rec-detail-status-${
                      (record.healthStatus || "good").toLowerCase()
                    }`}
                  >
                    {record.healthStatus || "Good"}
                  </span>
                </div>
              </div>

              <div className="rec-detail-section">
                <label className="rec-detail-section-label">Doctor's Notes:</label>
                <p className="rec-detail-section-content">
                  {record.notes || "—"}
                </p>
              </div>

              <div className="rec-detail-section">
                <label className="rec-detail-section-label">Doctor's Comment:</label>
                <div className="rec-detail-comment-box">
                  {record.doctorComment || "No comment"}
                </div>
              </div>
            </div>

            <div className="rec-detail-actions">
              <button
                type="button"
                className="rec-detail-btn rec-detail-btn-primary"
                onClick={() => {
                  // Download/Print functionality
                  window.print();
                }}
              >
                🖨️ Print Record
              </button>
              <button
                type="button"
                className="rec-detail-btn rec-detail-btn-secondary"
                onClick={() => navigate("/patient/dashboard?tab=records")}
              >
                Back to Medical Records
              </button>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
