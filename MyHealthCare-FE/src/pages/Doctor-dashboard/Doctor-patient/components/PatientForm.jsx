import React from "react";

export default function PatientForm({
  title,
  submitLabel,
  formData,
  onChange,
  onSubmit,
  loading,
  showAvatar,
}) {
  return (
    <div className="patient-form-card">
      <h2 className="patient-title">{title}</h2>

      <form className="patient-form" onSubmit={onSubmit}>
        <div className="patient-form-header">
          <div className="patient-photo-circle">
            {showAvatar ? "😊" : "📷"}
          </div>
          <button type="button" className="upload-link">
            Upload Photo
          </button>
        </div>

        <div className="patient-form-grid">
          <div className="patient-field">
            <label>
              First Name<span className="asterisk">*</span>
            </label>
            <input
              className="patient-input"
              placeholder="Enter your first name"
              value={formData.firstName}
              onChange={(e) => onChange("firstName", e.target.value)}
            />
          </div>

          <div className="patient-field">
            <label>
              Last Name<span className="asterisk">*</span>
            </label>
            <input
              className="patient-input"
              placeholder="Enter your last name"
              value={formData.lastName}
              onChange={(e) => onChange("lastName", e.target.value)}
            />
          </div>

          <div className="patient-field">
            <label>Your email</label>
            <input
              className="patient-input"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) => onChange("email", e.target.value)}
            />
          </div>

          <div className="patient-field">
            <label>Phone Number</label>
            <input
              className="patient-input"
              placeholder="Enter your phone number"
              value={formData.phone}
              onChange={(e) => onChange("phone", e.target.value)}
            />
          </div>

          <div className="patient-field">
            <label>Age</label>
            <input
              className="patient-input"
              placeholder="Enter your Age"
              value={formData.age}
              onChange={(e) => onChange("age", e.target.value)}
            />
          </div>

          <div className="patient-field">
            <label>Gender</label>
            <select
              className="patient-input"
              value={formData.gender}
              onChange={(e) => onChange("gender", e.target.value)}
            >
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>

          {/* ô Records chỉ dùng cho Edit – có thể thêm sau nếu cần */}
        </div>

        <div className="patient-form-footer">
          <button
            type="submit"
            className="patient-submit-btn"
            disabled={loading}
          >
            {loading ? "Saving..." : submitLabel}
          </button>
        </div>
      </form>
    </div>
  );
}
