// src/pages/Doctor-dashboard/components/DashboardHeader.jsx
import React from "react";
import Logo from "../../../components/Logo/Logo";

export default function DashboardHeader() {
  return (
    <header className="dd-header">
      <div className="dd-header-inner">
        {/* Left: logo */}
        <div className="dd-header-left dd-header-left--logo">
          <Logo to="/doctor/dashboard" />
        </div>

        {/* Right: empty for now - user info is in sidebar */}
        <div className="dd-header-right">
          {/* User info moved to sidebar */}
        </div>
      </div>
    </header>
  );
}
