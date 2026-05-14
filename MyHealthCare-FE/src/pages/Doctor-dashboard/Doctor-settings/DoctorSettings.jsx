// src/pages/Doctor-dashboard/Doctor-settings/DoctorSettings.jsx
import React from "react";
import "./DoctorSettings.css";

import DoctorLayout from "../DoctorLayout";
import { useDoctorProfile } from "./hooks/useDoctorProfile";
import ProfileForm from "./components/ProfileForm";

export default function DoctorSettings() {
  const { formData, handleChange, handleSave } = useDoctorProfile();
  const [theme, setTheme] = React.useState("light");

  return (
    <DoctorLayout activeMenu="settings" activeSub="settings">
      <div className="settings-layout">
        <div className="settings-card">
          <h2 className="settings-title">Appearance</h2>
          <p className="settings-subtitle">Choose light or dark mode.</p>
          <div className="settings-field">
            <label>Mode</label>
            <div className="settings-toggle">
              <button
                type="button"
                className={
                  "settings-toggle-btn" + (theme === "light" ? " active" : "")
                }
                onClick={() => setTheme("light")}
              >
                Light
              </button>
              <button
                type="button"
                className={
                  "settings-toggle-btn" + (theme === "dark" ? " active" : "")
                }
                onClick={() => setTheme("dark")}
              >
                Dark
              </button>
            </div>
          </div>
        </div>

        <ProfileForm
          formData={formData}
          onChange={handleChange}
          onSave={handleSave}
          isEditing={true}
          onStartEdit={() => {}}
          editableFields={["about"]}
          roleValue="Doctor"
        />
      </div>
    </DoctorLayout>
  );
}
