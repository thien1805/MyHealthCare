import React from "react";
import { Link } from "react-router-dom";
import "./Logo.css";

const Logo = ({ clickable = true, className = "", to = "/" }) => {
  const logoContent = (
    <h1 className={`logo ${className}`}>
      <span className="logo-my">My</span>
      <span className="logo-health">Health</span>
      <span className="logo-care">Care</span>
      <span className="logo-plus">+</span>
    </h1>
  );

  return clickable ? (
    <Link to={to} className="logo-container">
      {logoContent}
    </Link>
  ) : (
    <div className="logo-container">
      {logoContent}
    </div>
  );
};

export default Logo;
