import React from "react";
import "./DoctorPatient.css";

import DoctorSidebar from "../../../components/DoctorSidebar/DoctorSidebar";
import BillTopBar from "../Doctor-billList/components/BillTopBar";
import PatientViewInfo from "./components/PatientViewInfo";
import PatientHistoryTable from "./components/PatientHistoryTable";
import { useDoctorViewPatient } from "./hook/useDoctorViewPatient";

export default function DoctorViewPatient() {
  const { patient, history } = useDoctorViewPatient();

  return (
    <div className="bill-page">
      <DoctorSidebar activeMenu="patients" activeSub="patient-list" />

      <div className="bill-main">
        <BillTopBar />

        <div className="bill-content">
          <div className="patient-view-card">
            <PatientViewInfo patient={patient} />
            <PatientHistoryTable history={history} />
          </div>
        </div>
      </div>
    </div>
  );
}
