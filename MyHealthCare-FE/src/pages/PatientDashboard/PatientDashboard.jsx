// src/pages/PatientDashboard/PatientDashboard.jsx
import React, { useEffect, useCallback } from "react";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useToast } from "../../hooks/useToast";
import { useTranslation } from "../../hooks/useTranslation";

import "./PatientDashboard.css";
import { usePatientDashboard } from "./hooks/usePatientDashboard";

// top-level widgets
import DashboardStats from "./components/DashboardStats";
import DashboardTabs from "./components/DashboardTabs";

// tab: appointments
import AppointmentList from "./components/appointments/AppointmentList";

// tab: profile
import PatientProfileCard from "./components/profile/PatientProfileCard";

// tab: records
import MedicalRecordList from "./components/records/MedicalRecordList";

export default function PatientDashboard() {
  // 🔹 TẤT CẢ HOOK PHẢI Ở ĐÂY
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const toast = useToast();
  const { ToastContainer } = toast;
  const { t } = useTranslation();

  const {
    user,
    stats,
    tabs,
    appointments,
    records,
    statusOptions,
    activeTab,
    setActiveTab,
    activeStatus,
    setActiveStatus,
    appointmentPage,
    appointmentPageSize,
    appointmentTotal,
    setAppointmentPage,
    loading,
    error,
    refreshAppointments,
  } = usePatientDashboard();
  
  console.log("🔍 [PatientDashboard] user object:", user);
  console.log("🔍 [PatientDashboard] user.full_name:", user?.full_name);
  console.log("🔍 [PatientDashboard] user.name:", user?.name);
  console.log("🔍 [PatientDashboard] user.email:", user?.email);

  // 🔹 Sync URL params -> state (on mount and URL change)
  useEffect(() => {
    const tabFromUrl = searchParams.get("tab");
    const statusFromUrl = searchParams.get("status");
    const pageFromUrl = searchParams.get("page");

    if (tabFromUrl && tabFromUrl !== activeTab) {
      setActiveTab(tabFromUrl);
    }
    if (statusFromUrl && statusFromUrl !== activeStatus) {
      setActiveStatus(statusFromUrl);
    }
    if (pageFromUrl) {
      const pageNum = parseInt(pageFromUrl, 10);
      if (!isNaN(pageNum) && pageNum !== appointmentPage) {
        setAppointmentPage(pageNum);
      }
    }
  }, [searchParams]);

  // 🔹 Update URL when state changes
  const updateUrlParams = useCallback((newParams) => {
    setSearchParams((prev) => {
      const updated = new URLSearchParams(prev);
      Object.entries(newParams).forEach(([key, value]) => {
        if (value && value !== "all" && value !== 1) {
          updated.set(key, value);
        } else {
          updated.delete(key);
        }
      });
      return updated;
    }, { replace: true });
  }, [setSearchParams]);

  // 🔹 Handle tab change with URL sync
  const handleTabChange = useCallback((newTab) => {
    setActiveTab(newTab);
    updateUrlParams({ 
      tab: newTab !== "appointments" ? newTab : null,
      status: null,
      page: null 
    });
  }, [setActiveTab, updateUrlParams]);

  // 🔹 Handle status filter change with URL sync
  const handleStatusChange = useCallback((newStatus) => {
    setActiveStatus(newStatus);
    setAppointmentPage(1);
    updateUrlParams({ 
      tab: activeTab !== "appointments" ? activeTab : null,
      status: newStatus !== "all" ? newStatus : null,
      page: null 
    });
  }, [setActiveStatus, setAppointmentPage, activeTab, updateUrlParams]);

  // 🔹 Handle page change with URL sync
  const handlePageChange = useCallback((newPage) => {
    setAppointmentPage(newPage);
    updateUrlParams({ 
      tab: activeTab !== "appointments" ? activeTab : null,
      status: activeStatus !== "all" ? activeStatus : null,
      page: newPage > 1 ? newPage : null 
    });
  }, [setAppointmentPage, activeTab, activeStatus, updateUrlParams]);

  // 🔹 sau khi gọi hook MỚI được if/return
  if (loading && !user) {
    return (
      <>
        <Header />
        <main className="pd-page">
          <div className="pd-card pd-empty-tab">{t("patient.loading")}</div>
        </main>
      </>
    );
  }

  if (!loading && !user) {
    return (
      <>
        <Header />
        <main className="pd-page">
          <div className="pd-card pd-empty-tab">
            {error || t("patient.error")}
          </div>
        </main>
      </>
    );
  }

  const initialLetter = user?.full_name?.charAt(0)?.toUpperCase() ?? "?";

  const handleHeroBookClick = () => {
    navigate("/patient/appointments");
  };

  return (
    <>
      <Header />
      <ToastContainer />

      <main className="pd-page">
        {/* HERO */}
        <section className="pd-hero-card">
          <div className="pd-hero-left">
            <div className="pd-hero-avatar">
              <div className="pd-hero-avatar-inner">{initialLetter}</div>
            </div>
            <div>
              <h1 className="pd-hero-title">
                {t("patient.hello")}, {user?.full_name?.trim() || user?.name?.trim() || user?.email?.split('@')[0] || "Patient"}!
              </h1>
              <p className="pd-hero-subtitle">
                {t("patient.welcomePortal")}
              </p>
            </div>
          </div>

          <div className="pd-hero-right">
            <button
              type="button"
              className="pd-primary-btn"
              onClick={handleHeroBookClick}
            >
              {t("patient.bookNewAppointment")}
            </button>
          </div>
        </section>

        {/* Note: error messages intentionally hidden in UI; developer logs preserved */}

        {/* STATS */}
        <DashboardStats stats={stats} />

        {/* TABS */}
        <DashboardTabs
          tabs={tabs}
          activeTab={activeTab}
          onChange={handleTabChange}
        />

        {/* TAB CONTENT */}
        {activeTab === "appointments" && (
          <AppointmentList
            appointments={appointments}
            records={records}
            statusOptions={statusOptions}
            activeStatus={activeStatus}
            onStatusChange={handleStatusChange}
            page={appointmentPage}
            pageSize={appointmentPageSize}
            total={appointmentTotal}
            onPageChange={handlePageChange}
            toast={toast}
            onRefresh={refreshAppointments}
          />
        )}

        {activeTab === "records" && <MedicalRecordList 
          records={records}
          appointments={appointments}
          toast={toast}
          onRefresh={refreshAppointments}
        />}

        {activeTab === "profile" && (
          <PatientProfileCard user={user} />
        )}
      </main>

      <Footer />
    </>
  );
}
