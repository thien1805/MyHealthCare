// src/pages/Doctor-dashboard/Doctor-patient/hooks/useDoctorPatientForm.js
import { useState } from "react";
import {
  createDoctorPatient,
  updateDoctorPatient,
} from "../../../../api/doctorPatientAPI";

/**
 * Hook dùng chung cho Add / Edit patient.
 * - Nếu truyền initialData → chế độ Edit
 * - Nếu không truyền → chế độ Add
 */
export function useDoctorPatientForm(initialData = null) {
  const isEditMode = !!initialData?.id;

  const [formData, setFormData] = useState({
    firstName: initialData?.firstName || "",
    lastName: initialData?.lastName || "",
    email: initialData?.email || "",
    phone: initialData?.phone || "",
    age: initialData?.age || "",
    gender: initialData?.gender || "Male",
    address: initialData?.address || "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Map form → payload đúng format backend
      const payload = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone_num: formData.phone,
        age: formData.age,
        gender: formData.gender,
        address: formData.address,
      };

      if (isEditMode) {
        // Edit patient
        await updateDoctorPatient(initialData.id, payload);
        alert("Patient updated successfully (API).");
      } else {
        // Create new patient
        await createDoctorPatient(payload);
        alert("Patient created successfully (API).");
      }
    } catch (err) {
      console.error("Save patient failed:", err);
      setError("Failed to save patient.");
    } finally {
      setLoading(false);
    }
  };

  return {
    formData,
    handleChange,
    handleSubmit,
    loading,
    error,
  };
}
