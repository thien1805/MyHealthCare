// src/pages/Doctor-dashboard/Doctor-patient/DoctorPatientList.jsx
import React from "react";
import "./DoctorPatient.css";

import DoctorLayout from "../DoctorLayout";
import PatientListTable from "./components/PatientListTable";
import { useDoctorPatientList } from "./hooks/useDoctorPatientList";

export default function DoctorPatientList() {
  const { patients, search, setSearch } = useDoctorPatientList();

  return (
    <DoctorLayout activeMenu="patients" activeSub="patient-list">
      <div className="dd-content-card">
        <PatientListTable
          patients={patients}
          search={search}
          onSearchChange={setSearch}
        />
      </div>
    </DoctorLayout>
  );
}
