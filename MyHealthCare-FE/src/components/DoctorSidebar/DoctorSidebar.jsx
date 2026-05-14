// src/components/DoctorSidebar/DoctorSidebar.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./DoctorSidebar.css";
import { useAuth } from "../../context/AuthContext";

export default function DoctorSidebar({ activeMenu, isOpen = false, onClose }) {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [confirmLogoutOpen, setConfirmLogoutOpen] = useState(false);
  const [profileModalOpen, setProfileModalOpen] = useState(false);

  // Compute initials for avatar
  const getInitials = (name) => {
    if (!name) return "D";
    const parts = name.trim().split(" ");
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name[0]?.toUpperCase() || "D";
  };

  const doctorName = user?.full_name || user?.name || "Doctor";
  const initials = getInitials(doctorName);

  const getItemClass = (menuId) =>
    "nav-item" + (activeMenu === menuId ? " nav-item--active" : "");

  const handleLogoutConfirm = async () => {
    try {
      await logout();
      setConfirmLogoutOpen(false);
      navigate("/login");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const handleNavClick = () => {
    if (onClose) onClose();
  };

  return (
    <aside className={`doctor-sidebar ${isOpen ? 'sidebar--open' : ''}`}>
      {/* Doctor profile - quick view */}
      <div
        className="doctor-sidebar-profile doctor-sidebar-profile--clickable"
        onClick={() => setProfileModalOpen(true)}
        title="View Profile"
      >
        <div className="doctor-sidebar-avatar">{initials}</div>
        <div className="doctor-sidebar-info">
          <span className="doctor-sidebar-name">{doctorName}</span>
          <span className="doctor-sidebar-role">Doctor</span>
        </div>
      </div>

      {/* Main menu */}
      <nav className="doctor-sidebar-nav">
        {/* Dashboard */}
        <Link to="/doctor/dashboard" className={getItemClass("dashboard")} onClick={handleNavClick}>
          <span className="nav-icon">📊</span>
          <span>Dashboard</span>
        </Link>

        {/* Appointments */}
        <Link
          to="/doctor/appointments"
          className={getItemClass("appointments")}
          onClick={handleNavClick}
        >
          <span className="nav-icon">📅</span>
          <span>Appointments</span>
        </Link>

        {/* Calendar */}
        <Link to="/doctor/calendar" className={getItemClass("calendar")} onClick={handleNavClick}>
          <span className="nav-icon">🗓</span>
          <span>Calendar</span>
        </Link>
      </nav>
      
      {/* Bottom section: logout only */}
      <div className="doctor-sidebar-bottom">
        <button
          type="button"
          className="nav-item nav-item--logout"
          onClick={() => setConfirmLogoutOpen(true)}
        >
          <span className="nav-icon">🔒</span>
          <span>Logout</span>
        </button>
      </div>

      {/* Profile Modal - View Only */}
      {profileModalOpen && (
        <div
          className="header-modal-backdrop"
          onClick={() => setProfileModalOpen(false)}
        >
          <div
            className="profile-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <div className="profile-modal-header">
              <h2>Doctor Profile</h2>
              <button
                type="button"
                className="profile-modal-close"
                onClick={() => setProfileModalOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="profile-modal-body">
              <div className="profile-modal-avatar">
                {initials}
              </div>
              <div className="profile-modal-info">
                <div className="profile-info-row">
                  <span className="profile-label">Full name:</span>
                  <span className="profile-value">{user?.full_name || "N/A"}</span>
                </div>
                <div className="profile-info-row">
                  <span className="profile-label">Email:</span>
                  <span className="profile-value">{user?.email || "N/A"}</span>
                </div>
                <div className="profile-info-row">
                  <span className="profile-label">Phone:</span>
                  <span className="profile-value">{user?.phone_num || user?.phone || "N/A"}</span>
                </div>
                <div className="profile-info-row">
                  <span className="profile-label">Role:</span>
                  <span className="profile-value profile-value--badge">Doctor</span>
                </div>
              </div>
              <p className="profile-modal-note">
                * Contact admin to update your profile information.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Logout Confirmation Modal */}
      {confirmLogoutOpen && (
        <div
          className="header-modal-backdrop"
          onClick={() => setConfirmLogoutOpen(false)}
        >
          <div
            className="header-modal"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="logout-modal-title"
          >
            <div className="header-modal-title" id="logout-modal-title">
              Are you sure to log out?
            </div>
            <div className="header-modal-actions">
              <button
                type="button"
                className="header-modal-btn header-modal-btn--secondary"
                onClick={() => setConfirmLogoutOpen(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="header-modal-btn header-modal-btn--danger"
                onClick={handleLogoutConfirm}
              >
                Log out
              </button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
