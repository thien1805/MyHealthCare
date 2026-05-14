// src/pages/Doctor-dashboard/Doctor-appointments/DoctorAppointmentLog.jsx
import React from "react";
import "./DoctorAppointment.css";

import DoctorLayout from "../DoctorLayout";
import AppointmentActivityTable from "./components/AppointmentActivityTable";
import MedicalRecordModal from "./components/MedicalRecordModal";
import { useDoctorAppointmentList } from "./hooks/useDoctorAppointmentList";
import { useToast } from "../../../hooks/useToast";

export default function DoctorAppointmentLog() {
  const hook = useDoctorAppointmentList();
  const toast = useToast();
  const { ToastContainer } = toast;

  return (
    <DoctorLayout activeMenu="appointments">
      <div className="dd-content-card">
        <AppointmentActivityTable 
          {...hook} 
          onAddRecord={hook.openMedicalRecordModal}
          toast={toast}
        />
      </div>

      {/* Medical Record Modal */}
      {hook.showMedicalRecordModal && (
        <MedicalRecordModal
          appointment={hook.selectedAppointment}
          services={hook.services}
          loadingServices={hook.loadingServices}
          onSubmit={hook.submitMedicalRecord}
          onClose={hook.closeMedicalRecordModal}
          submitting={hook.submitting}
          toast={toast}
        />
      )}
      
      <ToastContainer />
    </DoctorLayout>
  );
}
