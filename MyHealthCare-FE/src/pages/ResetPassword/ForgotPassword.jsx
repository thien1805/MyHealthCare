import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { requestPasswordReset } from "../../api/authAPI";
import Logo from "../../components/Logo/Logo";
import "./resetPassword.css";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!email) {
      setError("Please enter your email");
      return;
    }

    try {
      setLoading(true);
      await requestPasswordReset({ email });
      setSuccess("Reset link sent. Please check your inbox.");
    } catch (err) {
      setError(err?.message || "Failed to send email. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-page">
      <div className="reset-card">
        <Logo clickable={true} className="reset-logo" />
        <div className="reset-header">
          <p className="reset-subtitle">Forgot Password</p>
          <h1 className="reset-title">Get your reset link</h1>
          <p className="reset-desc">
            Enter the email associated with your account. If it exists, we will send you a password reset link.
          </p>
        </div>

        <form className="reset-form" onSubmit={handleSubmit}>
          <label className="reset-label" htmlFor="email">
            Email address
          </label>
          <input
            id="email"
            type="email"
            className="reset-input"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          {error && <div className="reset-alert error">{error}</div>}
          {success && <div className="reset-alert success">{success}</div>}

          <button type="submit" className="reset-button" disabled={loading}>
            {loading ? "Sending..." : "Send reset link"}
          </button>

          <button
            type="button"
            className="reset-link"
            onClick={() => navigate("/login")}
          >
            Back to login
          </button>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword;
