import { CheckCircle2 } from "lucide-react";

export default function SignupSuccess({ onBack }) {
  return (
    <div className="signup-page success">
      <div className="success-box">
        <div className="success-icon">
          <CheckCircle2 className="icon" />
        </div>
        <h2>Welcome to MyHealthCare+</h2>
        <p>
          Your account has been created successfully. Please check your email to verify your
          account.
        </p>
        <button onClick={onBack} className="btn-primary">
          Back to Sign Up
        </button>
      </div>
    </div>
  );
}

