// src/pages/Doctor-dashboard/Doctor-settings/DoctorProfile.jsx
import React, { useState } from "react";
import "./DoctorSettings.css";

import DoctorLayout from "../DoctorLayout";
import ProfileForm from "./components/ProfileForm";
import { useDoctorProfile } from "./hooks/useDoctorProfile";

export default function DoctorProfile() {
  const { formData, handleChange, handleSave } = useDoctorProfile();

  const [isEditing, setIsEditing] = useState(false);

  const handleSaveProfile = async () => {
    // gọi logic lưu profile (gọi API) trong hook
    await handleSave();
    // sau khi lưu xong thì tắt chế độ edit
    setIsEditing(false);
  };

  return (
    <DoctorLayout activeMenu="settings" activeSub="profile">
      <div className="settings-layout">
        <ProfileForm
          formData={formData}
          onChange={handleChange}
          onSave={handleSaveProfile}
          isEditing={isEditing}
          onStartEdit={() => setIsEditing(true)}
        />
      </div>
    </DoctorLayout>
  );
}
