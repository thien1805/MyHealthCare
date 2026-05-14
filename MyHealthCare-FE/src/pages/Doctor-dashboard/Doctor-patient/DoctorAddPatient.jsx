// src/pages/Doctor-dashboard/Doctor-patient/DoctorAddPatient.jsx
import React from "react";
import "./DoctorPatient.css";

import DoctorLayout from "../DoctorLayout";
import PatientForm from "./components/PatientForm";
import { useDoctorPatientForm } from "./hooks/useDoctorPatientForm";

export default function DoctorAddPatient() {
  const { formData, handleChange, handleSubmit, loading } =
    useDoctorPatientForm();

  return (
    <DoctorLayout activeMenu="patients" activeSub="add-patient">
      <div className="dd-content-card">
        <PatientForm
          title="Add New Patient"
          submitLabel="Add Now"
          formData={formData}
          onChange={handleChange}
          onSubmit={handleSubmit}
          loading={loading}
          showAvatar={false}
        />
      </div>
    </DoctorLayout>
  );
}
