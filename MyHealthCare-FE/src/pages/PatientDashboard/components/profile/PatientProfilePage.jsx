// src/pages/PatientDashboard/components/profile/PatientProfilePage.jsx
import React from "react";
import Header from "../../../../components/Header";
import Footer from "../../../../components/Footer";
import { useAuth } from "../../../../context/AuthContext";
import PatientProfileCard from "./PatientProfileCard";
import "../../PatientDashboard.css";

export default function PatientProfilePage() {
  const { user, loading } = useAuth();

  const initialProfile = {
    name: user?.full_name || user?.name || "",
    email: user?.email || "",
    phone: user?._num || "",
  };

  return (
    <>
      <Header />
      <main className="pd-page">
        <section className="pd-card" style={{ marginBottom: "1.5rem" }}>
          <h1 className="pd-hero-title" style={{ marginBottom: "0.25rem" }}>
            Edit profile
          </h1>
          <p className="pd-hero-subtitle">
            Update your name, phone number, and location. Your email address
            cannot be changed here.
          </p>
        </section>

        {loading && (
          <section className="pd-card pd-empty-tab">Loading profile...</section>
        )}

        {!loading && user && (
          <PatientProfileCard initialProfile={initialProfile} startEditing />
        )}

        {!loading && !user && (
          <section className="pd-card pd-empty-tab">
            You need to sign in to view your profile.
          </section>
        )}
      </main>
      <Footer />
    </>
  );
}
