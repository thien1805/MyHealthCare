// src/pages/Doctor-dashboard/Doctor-appointments/components/MedicalRecordQuickAdd.jsx
import React, { useState, forwardRef } from "react";

const initialForm = {
  name: "",
  age: "",
  email: "",
  bloodGroup: "",
  weight: "",
  height: "",
  diagnosis: "",
  reminder: "",
};

const MedicalRecordQuickAdd = forwardRef(function MedicalRecordQuickAdd(_, ref) {
  const [form, setForm] = useState(initialForm);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      // TODO: call backend to add medical record & notify patient
      console.log("Submitting medical record:", form);
      alert(
        "Medical record sent to patient. (Hook up to backend to save + notify.)"
      );
      setForm(initialForm);
    } catch (err) {
      console.error("Submit record error:", err);
      alert("Failed to send medical record.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="appt-record-card" ref={ref}>
      <div className="appt-record-header">
        <div>
          <h3 className="appt-title">Add medical record</h3>
          <p className="appt-subtitle">
            Send record to patient (only completed appointments should be used).
          </p>
        </div>
      </div>

      <form className="appt-record-form" onSubmit={handleSubmit}>
        <div className="appt-record-grid">
          <label className="appt-record-field">
            <span>Name</span>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              required
            />
          </label>
          <label className="appt-record-field">
            <span>Age</span>
            <input
              name="age"
              value={form.age}
              onChange={handleChange}
              type="number"
              min="0"
            />
          </label>
          <label className="appt-record-field">
            <span>Email address</span>
            <input
              name="email"
              value={form.email}
              onChange={handleChange}
              type="email"
            />
          </label>
          <label className="appt-record-field">
            <span>Blood group</span>
            <input
              name="bloodGroup"
              value={form.bloodGroup}
              onChange={handleChange}
              placeholder="e.g. A+, O-"
            />
          </label>
          <label className="appt-record-field">
            <span>Weight (kg)</span>
            <input
              name="weight"
              value={form.weight}
              onChange={handleChange}
              type="number"
              min="0"
              step="0.1"
            />
          </label>
          <label className="appt-record-field">
            <span>Height (cm)</span>
            <input
              name="height"
              value={form.height}
              onChange={handleChange}
              type="number"
              min="0"
              step="0.1"
            />
          </label>
        </div>

        <label className="appt-record-field">
          <span>Doctor&apos;s diagnosis</span>
          <textarea
            name="diagnosis"
            value={form.diagnosis}
            onChange={handleChange}
            rows={3}
            required
          />
        </label>

        <label className="appt-record-field">
          <span>Reminder / Notes to patient</span>
          <textarea
            name="reminder"
            value={form.reminder}
            onChange={handleChange}
            rows={2}
          />
        </label>

        <div className="appt-record-actions">
          <button
            type="submit"
            className="appt-record-send-btn"
            disabled={submitting}
          >
            {submitting ? "Sending..." : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
});

export default MedicalRecordQuickAdd;
