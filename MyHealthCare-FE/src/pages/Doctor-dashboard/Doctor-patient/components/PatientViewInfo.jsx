// src/pages/Doctor-dashboard/Doctor-patient/DoctorViewPatient.jsx
import React from "react";
import "./DoctorPatient.css";

import { useParams } from "react-router-dom";
import DoctorLayout from "../DoctorLayout";

import PatientViewInfo from "./components/PatientViewInfo";
import PatientHistoryTable from "./components/PatientHistoryTable";
import { useDoctorViewPatient } from "./hooks/useDoctorViewPatient";

export default function DoctorViewPatient() {
  const { id } = useParams(); 
  const { patient, history, loading, error } = useDoctorViewPatient(id);

  return (
    <DoctorLayout activeMenu="patients" activeSub="patient-list">
      <div className="dd-content-card">
        {loading && <p>Loading...</p>}
        {error && <p className="error-text">{error}</p>}

        {patient && (
          <div className="patient-view-card">
            <PatientViewInfo patient={patient} />
            <PatientHistoryTable history={history} />
          </div>
        )}
      </div>
    </DoctorLayout>
  );
}
