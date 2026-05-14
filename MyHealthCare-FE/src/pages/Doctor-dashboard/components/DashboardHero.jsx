// src/Doctor/components/DashboardHero.jsx
import React from "react";

export default function DashboardHero({ greeting }) {
  return (
    <div className="dd-hero-card">
      <div className="dd-hero-text">
        <p className="dd-hero-hello">
          Hello <span>Dr. {greeting.name}</span>,
        </p>
        <p className="dd-hero-sub">{greeting.subText}</p>
        <p className="dd-hero-quote">“{greeting.quote}”</p>
      </div>
      <div className="dd-hero-illustration">{/* hình minh hoạ sau */}</div>
    </div>
  );
}
