// src/pages/Doctor-dashboard/DoctorLayout.jsx
import React, { useState } from "react";
import { Menu, X } from "lucide-react";
import DoctorSidebar from "../../components/DoctorSidebar/DoctorSidebar";
import DashboardHeader from "./components/DashboardHeader";
import "./DoctorDashboard.css"; // dùng chung các class .doctor-layout, .dd-page, .dd-main,...

export default function DoctorLayout({ activeMenu, activeSub, children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="doctor-layout">
      {/* Mobile Menu Toggle */}
      <button
        className="mobile-sidebar-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div 
          className="sidebar-overlay" 
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar bên trái (cố định) */}
      <DoctorSidebar 
        activeMenu={activeMenu} 
        activeSub={activeSub} 
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Phần nền xanh + header giống Dashboard */}
      <div className="dd-page">
        <DashboardHeader />

        <main className="dd-main">
          {children}
        </main>
      </div>
    </div>
  );
}
