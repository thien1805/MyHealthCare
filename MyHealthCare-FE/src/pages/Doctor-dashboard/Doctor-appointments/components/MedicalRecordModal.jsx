// src/pages/Doctor-dashboard/Doctor-appointments/components/MedicalRecordModal.jsx
import React, { useState } from "react";
import useTranslation from "../../../../hooks/useTranslation";
import { useLanguage } from "../../../../context/LanguageContext";

const initialForm = {
  diagnosis: "",
  prescription: "",
  treatment_plan: "",
  notes: "",
  follow_up_date: "",
  service_id: "",
  vital_signs: {
    blood_pressure: "",
    temperature: "",
    heart_rate: "",
    respiratory_rate: "",
    oxygen_saturation: "",
    weight: "",
    height: "",
  },
};

export default function MedicalRecordModal({
  appointment,
  services,
  loadingServices,
  onSubmit,
  onClose,
  submitting,
  toast,
}) {
  const [form, setForm] = useState(initialForm);
  const { t, formatDate, formatTime } = useTranslation();
  const { getLocalizedName } = useLanguage();

  if (!appointment) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleVitalSignChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      vital_signs: { ...prev.vital_signs, [name]: value },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!form.diagnosis.trim()) {
      toast?.error?.("Diagnosis is required");
      return;
    }
    
    const result = await onSubmit({
      ...form,
      service_id: form.service_id ? parseInt(form.service_id) : null,
    });
    
    if (result.success) {
      toast?.success?.("Medical record created successfully");
    } else {
      toast?.error?.(result.error || "Failed to create medical record");
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-content--large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Add Medical Record</h2>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Patient Info Summary */}
        <div className="modal-patient-info">
          <div className="modal-info-row">
            <span className="modal-info-label">Patient:</span>
            <span className="modal-info-value">
              {appointment.patient?.full_name || "Unknown"}
            </span>
          </div>
          <div className="modal-info-row">
            <span className="modal-info-label">Date:</span>
            <span className="modal-info-value">
              {formatDate(appointment.appointment_date)} at {formatTime(appointment.appointment_time)}
            </span>
          </div>
          <div className="modal-info-row">
            <span className="modal-info-label">Department:</span>
            <span className="modal-info-value">
              {getLocalizedName(appointment.department, "N/A")}
            </span>
          </div>
          <div className="modal-info-row">
            <span className="modal-info-label">Symptoms:</span>
            <span className="modal-info-value">
              {appointment.symptoms || appointment.reason || "Not provided"}
            </span>
          </div>
        </div>

        <form className="modal-form" onSubmit={handleSubmit}>
          {/* Service Selection */}
          <div className="modal-section">
            <h3>Service (Optional)</h3>
            <div className="modal-field">
              <label>Select Service</label>
              {loadingServices ? (
                <p>Loading services...</p>
              ) : (
                <select
                  name="service_id"
                  value={form.service_id}
                  onChange={handleChange}
                  className="modal-select"
                >
                  <option value="">-- No additional service --</option>
                  {services.map((svc) => (
                    <option key={svc.id} value={svc.id}>
                      {getLocalizedName(svc)} - {Number(svc.price).toLocaleString("vi-VN")} VND
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {/* Vital Signs */}
          <div className="modal-section">
            <h3>Vital Signs</h3>
            <div className="modal-grid modal-grid--3cols">
              <div className="modal-field">
                <label>Blood Pressure (mmHg)</label>
                <input
                  type="text"
                  name="blood_pressure"
                  value={form.vital_signs.blood_pressure}
                  onChange={handleVitalSignChange}
                  placeholder="e.g., 120/80"
                />
              </div>
              <div className="modal-field">
                <label>Temperature (°C)</label>
                <input
                  type="text"
                  name="temperature"
                  value={form.vital_signs.temperature}
                  onChange={handleVitalSignChange}
                  placeholder="e.g., 37.0"
                />
              </div>
              <div className="modal-field">
                <label>Heart Rate (bpm)</label>
                <input
                  type="text"
                  name="heart_rate"
                  value={form.vital_signs.heart_rate}
                  onChange={handleVitalSignChange}
                  placeholder="e.g., 72"
                />
              </div>
              <div className="modal-field">
                <label>Respiratory Rate</label>
                <input
                  type="text"
                  name="respiratory_rate"
                  value={form.vital_signs.respiratory_rate}
                  onChange={handleVitalSignChange}
                  placeholder="e.g., 18"
                />
              </div>
              <div className="modal-field">
                <label>Oxygen Saturation (%)</label>
                <input
                  type="text"
                  name="oxygen_saturation"
                  value={form.vital_signs.oxygen_saturation}
                  onChange={handleVitalSignChange}
                  placeholder="e.g., 98"
                />
              </div>
              <div className="modal-field">
                <label>Weight (kg)</label>
                <input
                  type="text"
                  name="weight"
                  value={form.vital_signs.weight}
                  onChange={handleVitalSignChange}
                  placeholder="e.g., 70"
                />
              </div>
              <div className="modal-field">
                <label>Height (cm)</label>
                <input
                  type="text"
                  name="height"
                  value={form.vital_signs.height}
                  onChange={handleVitalSignChange}
                  placeholder="e.g., 175"
                />
              </div>
            </div>
          </div>

          {/* Diagnosis & Treatment */}
          <div className="modal-section">
            <h3>Diagnosis & Treatment</h3>
            <div className="modal-field">
              <label>Diagnosis *</label>
              <textarea
                name="diagnosis"
                value={form.diagnosis}
                onChange={handleChange}
                rows={3}
                required
                placeholder="Enter diagnosis..."
              />
            </div>
            <div className="modal-field">
              <label>Prescription</label>
              <textarea
                name="prescription"
                value={form.prescription}
                onChange={handleChange}
                rows={3}
                placeholder="Enter prescription details..."
              />
            </div>
            <div className="modal-field">
              <label>Treatment Plan</label>
              <textarea
                name="treatment_plan"
                value={form.treatment_plan}
                onChange={handleChange}
                rows={3}
                placeholder="Enter treatment plan..."
              />
            </div>
            <div className="modal-field">
              <label>Notes</label>
              <textarea
                name="notes"
                value={form.notes}
                onChange={handleChange}
                rows={2}
                placeholder="Additional notes..."
              />
            </div>
            <div className="modal-field">
              <label>Follow-up Date</label>
              <input
                type="date"
                name="follow_up_date"
                value={form.follow_up_date}
                onChange={handleChange}
                min={new Date().toISOString().split("T")[0]}
              />
            </div>
          </div>

          {/* Actions */}
          <div className="modal-actions">
            <button
              type="button"
              className="modal-btn modal-btn--secondary"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="modal-btn modal-btn--primary"
              disabled={submitting}
            >
              {submitting ? "Saving..." : "Save Medical Record"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
