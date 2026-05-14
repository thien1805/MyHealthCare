// src/pages/Doctor-dashboard/DoctorDashboard.jsx
import React from "react";
import "./DoctorDashboard.css";

import { useDoctorDashboard } from "./hooks/useDoctorDashboard";
import DoctorLayout from "./DoctorLayout";

import DashboardHero from "./components/DashboardHero";
import DashboardStatsGrid from "./components/DashboardStatsGrid";
import DashboardActivity from "./components/DashboardActivity";
import DashboardCalendar from "./components/DashboardCalendar";

const DoctorDashboard = () => {
  const { loading, greeting, stats, activity, calendar, upcoming, todayList } = useDoctorDashboard();

  if (loading) {
    return (
      <DoctorLayout activeMenu="dashboard">
        <div className="dd-loading">
          <div className="dd-loading-spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </DoctorLayout>
    );
  }

  return (
    <DoctorLayout activeMenu="dashboard">
      <div className="dd-layout">
        {/* LEFT COLUMN */}
        <section className="dd-left">
          <DashboardHero greeting={greeting} />
          
          {/* Stats Grid */}
          <DashboardStatsGrid stats={stats} />
          
          {/* Today's Appointments */}
          {todayList && todayList.length > 0 && (
            <div className="dd-today-section">
              <h3 className="dd-section-title">Today's Appointments</h3>
              <div className="dd-today-list">
                {todayList.map((apt) => (
                  <div key={apt.id} className="dd-today-item">
                    <div className="dd-today-time">{apt.time}</div>
                    <div className="dd-today-info">
                      <span className="dd-today-patient">{apt.patientName}</span>
                      <span className="dd-today-symptoms">{apt.symptoms || "No symptoms"}</span>
                    </div>
                    <span className={`dd-today-status dd-today-status--${apt.status}`}>
                      {apt.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Activity Chart */}
          <div className="dd-bottom-row">
            <DashboardActivity activity={activity} />
          </div>
        </section>

        {/* RIGHT COLUMN */}
        <section className="dd-right">
          {/* Next Appointment */}
          {upcoming && (
            <div className="dd-next-appointment">
              <h3 className="dd-section-title">Next Appointment</h3>
              <div className="dd-next-card">
                <div className="dd-next-patient">{upcoming.name}</div>
                <div className="dd-next-date">{upcoming.dateText}</div>
                {upcoming.symptoms && (
                  <div className="dd-next-symptoms">
                    <span className="dd-next-label">Symptoms:</span>
                    <span>{upcoming.symptoms}</span>
                  </div>
                )}
              </div>
            </div>
          )}
          
          <DashboardCalendar calendar={calendar} />
        </section>
      </div>
    </DoctorLayout>
  );
};

export default DoctorDashboard;
