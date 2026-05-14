import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { resetPassword } from "../../api/authAPI";
import Logo from "../../components/Logo/Logo";
import "./resetPassword.css";

const ResetPassword = () => {
  const { uid, token } = useParams();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!password || !confirmPassword) {
      setError("Please enter both password fields.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Password confirmation does not match.");
      return;
    }

    try {
      setLoading(true);
      await resetPassword({ uid, token, newPassword: password, confirmPassword });
      setSuccess("Password reset successfully. You can now log in with your new password.");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      setError(err?.message || "Failed to reset password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const disabled = loading;

  return (
    <div className="reset-page">
      <div className="reset-card">
        <Logo clickable={true} className="reset-logo" />
        <div className="reset-header">
          <p className="reset-subtitle">Reset Password</p>
          <h1 className="reset-title">Enter new password</h1>
          <p className="reset-desc">
            This link came from your email. Please set a new password to continue logging in.
          </p>
        </div>

        <form className="reset-form" onSubmit={handleSubmit}>
          <label className="reset-label" htmlFor="password">
            New password
          </label>
          <input
            id="password"
            type="password"
            className="reset-input"
            placeholder="Enter new password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
          />

          <label className="reset-label" htmlFor="confirmPassword">
            Confirm password
          </label>
          <input
            id="confirmPassword"
            type="password"
            className="reset-input"
            placeholder="Re-enter password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            minLength={8}
            required
          />

          {error && <div className="reset-alert error">{error}</div>}
          {success && <div className="reset-alert success">{success}</div>}

          <button type="submit" className="reset-button" disabled={disabled}>
            {loading ? "Processing..." : "Update password"}
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

export default ResetPassword;
