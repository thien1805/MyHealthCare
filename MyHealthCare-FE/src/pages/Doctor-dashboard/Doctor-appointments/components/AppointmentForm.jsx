import React from "react";

export default function AppointmentForm({
  formData,
  onChange,
  onSubmit,
  loading,
}) {
  return (
    <div className="appt-form-card">
      <h2 className="appt-title">Book Appointment</h2>

      <form className="appt-form" onSubmit={onSubmit}>
        <div className="appt-form-grid">
          {/* Select patient */}
          <div className="appt-field">
            <label>
              Select Patient<span className="asterisk">*</span>
            </label>
            <div className="appt-input appt-input--select appt-input--error">
              <span>
                {formData.patient ? formData.patient : "Select Patient"}
              </span>
              <span className="appt-select-arrow">▾</span>
            </div>
          </div>

          <div className="appt-field" />

          {/* First / Last name */}
          <div className="appt-field">
            <label>First name</label>
            <input
              className="appt-input appt-input--readonly"
              placeholder="-"
              value={formData.firstName}
              onChange={(e) => onChange("firstName", e.target.value)}
            />
          </div>

          <div className="appt-field">
            <label>Last Name</label>
            <input
              className="appt-input appt-input--readonly"
              placeholder="-"
              value={formData.lastName}
              onChange={(e) => onChange("lastName", e.target.value)}
            />
          </div>

          {/* Date & time */}
          <div className="appt-field">
            <label>
              Date &amp; Time<span className="asterisk">*</span>
            </label>
            <div className="appt-input appt-input--select appt-input--success">
              <span>{formData.dateTime}</span>
              <span className="appt-select-arrow">▾</span>
            </div>
          </div>

          {/* Status */}
          <div className="appt-field">
            <label>
              Status<span className="asterisk">*</span>
            </label>
            <div className="appt-input appt-input--select appt-input--success">
              <span className="appt-status-text">Pending</span>
              <span className="appt-select-arrow">▾</span>
            </div>
          </div>

          {/* Notes full width */}
          <div className="appt-field appt-field--full">
            <label>Additional Notes</label>
            <textarea
              className="appt-textarea"
              placeholder="Write your Notes here..."
              value={formData.notes}
              onChange={(e) => onChange("notes", e.target.value)}
            />
          </div>
        </div>

        <div className="appt-form-footer">
          <button
            type="submit"
            className="appt-submit-btn"
            disabled={loading}
          >
            {loading ? "Booking..." : "Book now"}
          </button>
        </div>
      </form>
    </div>
  );
}
