import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useToast } from "../../../../hooks/useToast";
import { useTranslation } from "../../../../hooks/useTranslation";
import "./AppointmentTicket.css";
import Header from "../../../../components/Header";
import Footer from "../../../../components/Footer";

export default function AppointmentTicket() {
  const { appointmentId } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { success, error: showError } = useToast();
  const [appointment, setAppointment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAppointment = async () => {
      try {
        setLoading(true);
        // Mock: get appointment from localStorage or API
        const allAppointments = JSON.parse(
          localStorage.getItem("appointments") || "[]"
        );
        const appt = allAppointments.find((a) => a.id === appointmentId);

        if (appt) {
          setAppointment(appt);
        } else {
          showError("Appointment not found");
          navigate(-1);
        }
      } catch (err) {
        console.error("Error fetching appointment:", err);
        showError("Failed to load appointment");
      } finally {
        setLoading(false);
      }
    };

    fetchAppointment();
  }, [appointmentId, navigate, showError]);

  if (loading) {
    return (
      <>
        <Header />
        <main className="apt-ticket-page">
          <div className="apt-ticket-loading">Loading...</div>
        </main>
        <Footer />
      </>
    );
  }

  if (!appointment) {
    return (
      <>
        <Header />
        <main className="apt-ticket-page">
          <div className="apt-ticket-error">Appointment not found</div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main className="apt-ticket-page">
        <div className="apt-ticket-container">
          <button
            type="button"
            className="apt-ticket-back"
            onClick={() => navigate(-1)}
          >
            ← Back
          </button>

          <div className="apt-ticket-card">
            <h2 className="apt-ticket-title">Appointment Booking Ticket</h2>

            <div className="apt-ticket-content">
              <div className="apt-ticket-row">
                <span className="apt-ticket-label">Patient:</span>
                <span className="apt-ticket-value">{appointment.patientName || "Patient"}</span>
              </div>

              <div className="apt-ticket-row">
                <span className="apt-ticket-label">Symptoms:</span>
                <span className="apt-ticket-value">{appointment.notes || "—"}</span>
              </div>

              <div className="apt-ticket-row">
                <span className="apt-ticket-label">Specialty:</span>
                <span className="apt-ticket-value">{appointment.specialty || "—"}</span>
              </div>

              <div className="apt-ticket-row">
                <span className="apt-ticket-label">Doctor:</span>
                <span className="apt-ticket-value">{appointment.doctorName || "—"}</span>
              </div>

              <div className="apt-ticket-row">
                <span className="apt-ticket-label">Date:</span>
                <span className="apt-ticket-value">{appointment.date || "—"}</span>
              </div>

              <div className="apt-ticket-row">
                <span className="apt-ticket-label">Time:</span>
                <span className="apt-ticket-value">{appointment.time || "—"}</span>
              </div>

              <div className="apt-ticket-row">
                <span className="apt-ticket-label">Consultation fee:</span>
                <span className="apt-ticket-value apt-ticket-fee">230.961 VND</span>
              </div>
            </div>

            <div className="apt-ticket-notice">
              Please bring this booking ticket when going to the appointment.
            </div>

            <div className="apt-ticket-actions">
              <button
                type="button"
                className="apt-ticket-btn apt-ticket-btn-primary"
                onClick={() => {
                  // Print functionality
                  window.print();
                }}
              >
                🖨️ Print Ticket
              </button>
              <button
                type="button"
                className="apt-ticket-btn apt-ticket-btn-secondary"
                onClick={() => navigate("/patient/dashboard?tab=appointments")}
              >
                Back to Appointments
              </button>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
