// src/pages/Doctor-dashboard/Doctor-patient/DoctorEditPatient.jsx
import React from "react";
import "./DoctorPatient.css";

import DoctorLayout from "../DoctorLayout";
import PatientForm from "./components/PatientForm";
import { useDoctorPatientForm } from "./hooks/useDoctorPatientForm";
import { useParams } from "react-router-dom";

export default function DoctorEditPatient() {
  const { id } = useParams(); // lấy patient id từ URL /doctor/patients/edit/:id

  const { formData, handleChange, handleSubmit, loading } =
    useDoctorPatientForm(id); // edit mode (có id)

  return (
    <DoctorLayout activeMenu="patients" activeSub="edit-patient">
      <div className="dd-content-card">
        <PatientForm
          title="Edit Patient Details"
          submitLabel="Save"
          formData={formData}
          onChange={handleChange}
          onSubmit={handleSubmit}
          loading={loading}
          showAvatar={true}
        />
      </div>
    </DoctorLayout>
  );
}
