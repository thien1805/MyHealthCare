// src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import "./App.css";

// ==== PROTECTED ROUTES ====
import ProtectedRoute from "./components/ProtectedRoute";
import DoctorRoute from "./components/DoctorRoute";

// ==== GLOBAL COMPONENTS ====
import AIChatbot from "./components/AIChatbot/AIChatbot";

// ==== PUBLIC PAGES ====
import Home from "./pages/Home/Home";
import Login from "./pages/Login/Login";
import Signup from "./pages/Signup/Signup";
import AboutUs from "./pages/AboutUs/AboutUs";
import Medical from "./pages/Medical/Medical";
import ResetPassword from "./pages/ResetPassword/ResetPassword";
import ForgotPassword from "./pages/ResetPassword/ForgotPassword";
import VerifyResetToken from "./pages/ResetPassword/VerifyResetToken";

// ==== PATIENT SIDE ====
import PatientDashboard from "./pages/PatientDashboard/PatientDashboard";
import PatientProfilePage from "./pages/PatientDashboard/components/profile/PatientProfilePage";
import PatientAppointmentsPage from "./pages/PatientDashboard/components/appointments/PatientAppointmentsPage";
import PatientAppointmentDetailPage from "./pages/PatientDashboard/components/appointments/PatientAppointmentDetailPage";
import PatientMedicalRecordDetailPage from "./pages/PatientDashboard/components/records/PatientMedicalRecordDetailPage";
// ==== DOCTOR SIDE ====
import DoctorDashboard from "./pages/Doctor-dashboard/DoctorDashboard";
import DoctorPatientList from "./pages/Doctor-dashboard/Doctor-patient/DoctorPatientList";
import DoctorAppointmentLog from "./pages/Doctor-dashboard/Doctor-appointments/DoctorAppointmentLog";
import DoctorCalendar from "./pages/Doctor-dashboard/Doctor-calendar/DoctorCalendar";
import DoctorProfile from "./pages/Doctor-dashboard/Doctor-settings/DoctorProfile";
import DoctorSettings from "./pages/Doctor-dashboard/Doctor-settings/DoctorSettings";

const App = () => {
  return (
    <Router>
      <Routes>
        {/* ===== PUBLIC PAGES ===== */}
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/about" element={<AboutUs />} />
        <Route path="/medical" element={<Medical />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/verify-reset-token/:uid/:token" element={<VerifyResetToken />} />
        <Route path="/reset-password/:uid/:token" element={<ResetPassword />} />

        {/* ===== PROTECTED: PATIENT SIDE ===== */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/patient/dashboard"
          element={
            <ProtectedRoute>
              <PatientDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/patient/profile"
          element={
            <ProtectedRoute>
              <PatientProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/patient/appointments"
          element={
            <ProtectedRoute>
              <PatientAppointmentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/patient/appointment/:id"
          element={
            <ProtectedRoute>
              <PatientAppointmentDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/patient/medical-record/:recordId"
          element={
            <ProtectedRoute>
              <PatientMedicalRecordDetailPage />
            </ProtectedRoute>
          }
        />
        {/* ===== PROTECTED: DOCTOR SIDE ===== */}
        <Route
          path="/doctor/dashboard"
          element={
            <DoctorRoute>
              <DoctorDashboard />
            </DoctorRoute>
          }
        />
        <Route
          path="/doctor/patients"
          element={
            <DoctorRoute>
              <DoctorPatientList />
            </DoctorRoute>
          }
        />
        <Route
          path="/doctor/appointments"
          element={
            <DoctorRoute>
              <DoctorAppointmentLog />
            </DoctorRoute>
          }
        />
        <Route
          path="/doctor/calendar"
          element={
            <DoctorRoute>
              <DoctorCalendar />
            </DoctorRoute>
          }
        />
        <Route
          path="/doctor/settings/profile"
          element={
            <DoctorRoute>
              <DoctorProfile />
            </DoctorRoute>
          }
        />
        <Route
          path="/doctor/settings/preferences"
          element={
            <DoctorRoute>
              <DoctorSettings />
            </DoctorRoute>
          }
        />
      </Routes>
      
      {/* AI Chatbot - Global floating component */}
      <AIChatbot />
    </Router>
  );
};
  
  export default App;
