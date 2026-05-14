import React, { useState } from "react";
import { updatePatientHealthStatus } from "../../../api/doctorPatientAPI";

export default function HealthStatusForm() {
  const [patientId, setPatientId] = useState("");
  const [status, setStatus] = useState("");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!patientId || !status) {
      setError("Please enter patient ID and health status.");
      setMessage(null);
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setMessage(null);

      await updatePatientHealthStatus(patientId, { status, note });
      setMessage("Health status saved and sent to patient.");
    } catch (err) {
      const msg =
        err?.response?.data?.message ||
        err?.message ||
        "Failed to update health status.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dd-health-card">
      <div className="dd-card-header dd-card-header--between">
        <h3>Patient health status</h3>
      </div>

      <form className="dd-health-form" onSubmit={handleSubmit}>
        <label className="dd-health-label">
          Patient ID
          <input
            className="dd-health-input"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            placeholder="Enter patient ID"
          />
        </label>

        <label className="dd-health-label">
          Health status
          <input
            className="dd-health-input"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            placeholder="e.g. Stable, Needs follow-up"
          />
        </label>

        <label className="dd-health-label">
          Note (optional)
          <textarea
            className="dd-health-textarea"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Short note for the patient"
            rows={3}
          />
        </label>

        <div className="dd-health-actions">
          <button type="submit" className="dd-primary-btn" disabled={loading}>
            {loading ? "Saving..." : "Save & notify"}
          </button>
        </div>

        {message && <div className="dd-health-success">{message}</div>}
        {error && <div className="dd-health-error">{error}</div>}
      </form>
    </div>
  );
}
