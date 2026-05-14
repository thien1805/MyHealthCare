import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { verifyResetToken } from "../../api/authAPI";
import Logo from "../../components/Logo/Logo";
import "./resetPassword.css";

const VerifyResetToken = () => {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState("pending"); // pending | success | error
  const [message, setMessage] = useState("Checking link...");

  useEffect(() => {
    const run = async () => {
      try {
        await verifyResetToken({ uid, token });
        setStatus("success");
        setMessage("Link is valid. You can now set a new password.");
      } catch (err) {
        setStatus("error");
        setMessage(err?.message || "Link is invalid or has expired.");
      }
    };
    run();
  }, [uid, token]);

  const goReset = () => navigate(`/reset-password/${uid}/${token}`);

  return (
    <div className="reset-page">
      <div className="reset-card">
        <Logo clickable={true} className="reset-logo" />
        <div className="reset-header">
          <p className="reset-subtitle">Verify Link</p>
          <h1 className="reset-title">Checking reset token</h1>
          <p className="reset-desc">
            The system is verifying the token in the link you just opened.
          </p>
        </div>

        <div className={`reset-alert ${status === "error" ? "error" : "success"}`}>
          {message}
        </div>

        <div style={{ marginTop: "12px", display: "flex", gap: "10px" }}>
          <button
            className="reset-button"
            onClick={goReset}
            disabled={status !== "success"}
            style={{ flex: 1 }}
          >
            Continue to reset
          </button>

          <button
            type="button"
            className="reset-link"
            onClick={() => navigate("/login")}
            style={{ flex: 1, textAlign: "center" }}
          >
            Back to login
          </button>
        </div>
      </div>
    </div>
  );
};

export default VerifyResetToken;
