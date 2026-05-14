// src/pages/PatientDashboard/components/profile/PatientProfileCard.jsx
import React, { useEffect, useState } from "react";
import { useAuth } from "../../../../context/AuthContext";
import { useToast } from "../../../../hooks/useToast";
import { useTranslation } from "../../../../hooks/useTranslation";
import { getMe, updateProfile } from "../../../../api/authAPI";

const EMPTY_PROFILE = {
  full_name: "",
  email: "",
  phone_num: "",
  date_of_birth: "",
  gender: "",
  address: "",
  insurance_id: "",
  emergency_contact: "",
  emergency_contact_phone: "",
};

export default function PatientProfileCard({ user, initialProfile, startEditing }) {
  const { updateUser } = useAuth();
  const { success: showSuccess, error: showError } = useToast();
  const { t } = useTranslation();
  
  console.log("🔍 [PatientProfileCard] Received props - user:", user);
  console.log("🔍 [PatientProfileCard] Received props - initialProfile:", initialProfile);

  const [profile, setProfile] = useState(initialProfile || EMPTY_PROFILE);
  const [originalProfile, setOriginalProfile] = useState(
    initialProfile || EMPTY_PROFILE
  );
  const [isEditing, setIsEditing] = useState(!!startEditing);
  const [loading, setLoading] = useState(!initialProfile && !user);
  const [error, setError] = useState(null);

  const normalizeProfile = (data) => {
    // Handle both API response format and user object from props
    console.log("🔍 [PatientProfileCard] normalizeProfile input:", data);
    console.log("🔍 [PatientProfileCard] patient_profile:", data?.patient_profile);
    
    const patientData = data?.patient_profile || data || {};
    
    const result = {
      full_name: data?.full_name || "",
      email: data?.email || "",
      phone_num: data?.phone_num || data?.phone || "",
      date_of_birth: patientData?.date_of_birth || "",
      gender: patientData?.gender || "",
      address: patientData?.address || "",
      insurance_id: patientData?.insurance_id || "",
      emergency_contact: patientData?.emergency_contact || "",
      emergency_contact_phone: patientData?.emergency_contact_phone || "",
    };
    
    console.log("🔍 [PatientProfileCard] normalizeProfile output:", result);
    return result;
  };

  // Nếu nhận được user từ props, sử dụng luôn
  useEffect(() => {
    if (user) {
      const norm = normalizeProfile(user);
      setProfile(norm);
      setOriginalProfile(norm);
      setLoading(false);
      return;
    }

    // Nếu không có user từ props, gọi API
    let cancelled = false;

    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await getMe();
        if (cancelled) return;

        const norm = normalizeProfile(data);
        setProfile(norm);
        setOriginalProfile(norm);

        // Cập nhật AuthContext cho header/avatar
        updateUser?.({
          ...(user || {}),
          full_name: norm.full_name,
          email: norm.email,
        });
      } catch (err) {
        if (!cancelled) {
          console.error("Load profile error:", err);
          setError(
            typeof err === "string"
              ? err
              : err?.message || "Failed to load profile."
          );
          if (!initialProfile) {
            setProfile(EMPTY_PROFILE);
            setOriginalProfile(EMPTY_PROFILE);
          }
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchProfile();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialProfile]);

  const initialLetter =
    profile?.full_name?.charAt(0)?.toUpperCase() ||
    user?.full_name?.charAt(0)?.toUpperCase() ||
    "?";

  const handleCancelEdit = () => {
    setProfile(originalProfile);
    setIsEditing(false);
  };

  const handleSaveProfile = async (updatedProfile) => {
    try {
      const payload = {
        full_name: updatedProfile.full_name,
        phone_num: updatedProfile.phone_num,
        patient_profile: {
          date_of_birth: updatedProfile.date_of_birth,
          gender: updatedProfile.gender,
          address: updatedProfile.address,
          insurance_id: updatedProfile.insurance_id,
          emergency_contact: updatedProfile.emergency_contact,
          emergency_contact_phone: updatedProfile.emergency_contact_phone,
        },
      };

      const res = await updateProfile(payload);
      
      // Merge response với dữ liệu hiện tại để giữ lại các trường không được update
      const mergedProfile = {
        ...updatedProfile,  // Giữ lại tất cả dữ liệu form
        ...(res || {}),     // Override với response từ API
      };
      
      const norm = normalizeProfile(mergedProfile);

      setProfile(norm);
      setOriginalProfile(norm);

      updateUser?.({
        ...(user || {}),
        full_name: norm.full_name,
        email: norm.email,
      });

      showSuccess("Profile updated successfully!");
      setIsEditing(false);
    } catch (err) {
      console.error("Update profile error:", err);
      let msg = "Failed to update profile.";
      if (typeof err === "string") msg = err;
      else if (err?.message) msg = err.message;
      else if (err?.detail) msg = err.detail;
      showError(msg);
    }
  };

  if (loading) {
    return (
      <section className="pd-card pd-profile-card">
        <div className="pd-profile-header">
          <div className="pd-profile-main">
            <div className="pd-profile-avatar">
              <span>…</span>
            </div>
            <div>
              <h3 className="pd-profile-name">{t("patient.loading")}</h3>
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="pd-card pd-profile-card">
        <div className="pd-profile-header">
          <div className="pd-profile-main">
            <div className="pd-profile-avatar">
              <span>!</span>
            </div>
            <div>
              <h3 className="pd-profile-name">{t("patient.profile")}</h3>
              <p className="pd-profile-email" style={{ color: "red" }}>
                {typeof error === "string" && error.includes("<")
                  ? t("patient.error")
                  : error}
              </p>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="pd-card pd-profile-card" style={{ minHeight: "auto", width: "100%" }}>
      <div className="pd-profile-header">
        <div className="pd-profile-main">
          <div className="pd-profile-avatar">
            <span>{initialLetter}</span>
          </div>
          <div>
            <h3 className="pd-profile-name">{profile?.full_name || t("patient.noName")}</h3>
            <p className="pd-profile-email">
              {profile?.email || t("patient.noEmail")}
            </p>
          </div>
        </div>

        {!isEditing && (
          <button
            type="button"
            className="pd-outline-btn"
            onClick={() => setIsEditing(true)}
          >
            {t("patient.editProfile")}
          </button>
        )}
      </div>

      {!isEditing && (
        <div className="pd-profile-info-grid" style={{ gridTemplateColumns: "repeat(2, 1fr)", gap: "30px" }}>
          <div className="pd-profile-info-item">
            <span className="pd-profile-label">{t("patient.fullName")}</span>
            <span className="pd-profile-value">
              {profile.full_name?.trim() || t("patient.notProvided")}
            </span>
          </div>
          <div className="pd-profile-info-item">
            <span className="pd-profile-label">{t("patient.email")}</span>
            <span className="pd-profile-value">
              {profile.email?.trim() || t("patient.notProvided")}
            </span>
          </div>
          <div className="pd-profile-info-item">
            <span className="pd-profile-label">{t("patient.phone")}</span>
            <span className="pd-profile-value">
              {profile.phone_num?.trim() || t("patient.notProvided")}
            </span>
          </div>
          <div className="pd-profile-info-item">
            <span className="pd-profile-label">{t("patient.dateOfBirth")}</span>
            <span className="pd-profile-value">
              {profile.date_of_birth?.trim() || t("patient.notProvided")}
            </span>
          </div>
          <div className="pd-profile-info-item">
            <span className="pd-profile-label">{t("patient.gender")}</span>
            <span className="pd-profile-value" style={{ textTransform: "capitalize" }}>
              {profile.gender?.trim() || t("patient.notProvided")}
            </span>
          </div>
          <div className="pd-profile-info-item">
            <span className="pd-profile-label">{t("patient.insuranceId")}</span>
            <span className="pd-profile-value">
              {profile.insurance_id?.trim() || t("patient.notProvided")}
            </span>
          </div>
          <div className="pd-profile-info-item" style={{ gridColumn: "1 / -1" }}>
            <span className="pd-profile-label">{t("patient.address")}</span>
            <span className="pd-profile-value">
              {profile.address?.trim() || t("patient.notProvided")}
            </span>
          </div>
          <div className="pd-profile-info-item">
            <span className="pd-profile-label">{t("patient.emergencyContact")}</span>
            <span className="pd-profile-value">
              {profile.emergency_contact?.trim() || t("patient.notProvided")}
            </span>
          </div>
          <div className="pd-profile-info-item">
            <span className="pd-profile-label">{t("patient.emergencyContactPhone")}</span>
            <span className="pd-profile-value">
              {profile.emergency_contact_phone?.trim() || t("patient.notProvided")}
            </span>
          </div>
        </div>
      )}

      {isEditing && (
        <PatientProfileForm
          initialProfile={profile}
          onSave={handleSaveProfile}
          onCancel={handleCancelEdit}
        />
      )}
    </section>
  );
}

function PatientProfileForm({ initialProfile, onSave, onCancel }) {
  const { t } = useTranslation();
  const [profileForm, setProfileForm] = useState(
    initialProfile || EMPTY_PROFILE
  );
  const [errors, setErrors] = useState({});

  useEffect(() => {
    setProfileForm(initialProfile || EMPTY_PROFILE);
    setErrors({});
  }, [initialProfile]);

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileForm((prev) => ({ ...prev, [name]: value }));
    
    // Validate email in real-time
    if (name === "email" && value && !validateEmail(value)) {
      setErrors((prev) => ({ ...prev, email: "Invalid email format" }));
    } else {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate email before submit
    if (profileForm.email && !validateEmail(profileForm.email)) {
      setErrors((prev) => ({ ...prev, email: "Invalid email format" }));
      return;
    }
    
    onSave(profileForm);
  };

  return (
    <form className="pd-profile-form" onSubmit={handleSubmit}>
      <div className="pd-profile-form-row" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div className="pd-profile-form-field">
          <label>{t("patient.fullName")} *</label>
          <input
            type="text"
            name="full_name"
            value={profileForm.full_name}
            onChange={handleProfileChange}
            required
          />
        </div>
        <div className="pd-profile-form-field">
          <label>{t("patient.email")} *</label>
          <input
            type="email"
            name="email"
            value={profileForm.email}
            disabled
            style={{ backgroundColor: "#f0f0f0", cursor: "not-allowed" }}
          />
          <small style={{ color: "#999", fontSize: "12px" }}>{t("patient.emailCannotChange")}</small>
        </div>
      </div>

      <div className="pd-profile-form-row" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div className="pd-profile-form-field">
          <label>{t("patient.phone")}</label>
          <input
            type="text"
            name="phone_num"
            value={profileForm.phone_num}
            onChange={handleProfileChange}
          />
        </div>
        <div className="pd-profile-form-field">
          <label>{t("patient.dateOfBirth")}</label>
          <input
            type="date"
            name="date_of_birth"
            value={profileForm.date_of_birth}
            onChange={handleProfileChange}
          />
        </div>
      </div>

      <div className="pd-profile-form-row" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div className="pd-profile-form-field">
          <label>{t("patient.gender")}</label>
          <select
            name="gender"
            value={profileForm.gender}
            onChange={handleProfileChange}
          >
            <option value="">{t("patient.selectGender")}</option>
            <option value="male">{t("patient.male")}</option>
            <option value="female">{t("patient.female")}</option>
            <option value="other">{t("patient.other")}</option>
          </select>
        </div>
        <div className="pd-profile-form-field">
          <label>{t("patient.insuranceId")}</label>
          <input
            type="text"
            name="insurance_id"
            value={profileForm.insurance_id}
            onChange={handleProfileChange}
          />
        </div>
      </div>

      <div className="pd-profile-form-row" style={{ display: "grid", gridTemplateColumns: "1fr", gap: "20px" }}>
        <div className="pd-profile-form-field">
          <label>{t("patient.address")}</label>
          <input
            name="address"
            value={profileForm.address}
            onChange={handleProfileChange}
            rows="3"
            style={{ resize: "vertical" }}
          />
        </div>
      </div>

      <div className="pd-profile-form-row" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div className="pd-profile-form-field">
          <label>{t("patient.emergencyContact")}</label>
          <input
            type="text"
            name="emergency_contact"
            value={profileForm.emergency_contact}
            onChange={handleProfileChange}
          />
        </div>
        <div className="pd-profile-form-field">
          <label>{t("patient.emergencyContactPhone")}</label>
          <input
            type="text"
            name="emergency_contact_phone"
            value={profileForm.emergency_contact_phone}
            onChange={handleProfileChange}
          />
        </div>
        <div className="pd-profile-form-field">
          <label>{t("patient.role")}</label>
          <input type="text" value={t("common.patient")} disabled readOnly />
        </div>
      </div>

      <div className="pd-profile-actions">
        <button type="button" className="pd-ghost-btn" onClick={onCancel}>
          {t("patient.cancelEdit")}
        </button>
        <button type="submit" className="pd-primary-btn">
          {t("patient.saveChanges")}
        </button>
      </div>
    </form>
  );
}
