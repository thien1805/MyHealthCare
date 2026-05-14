import { Shield, CheckCircle2 } from "lucide-react";
import Logo from "../../../components/Logo/Logo";

export default function SignupLeft() {
  return (
    <div className="signup-left">
      <div>
        <Logo clickable={true} className="signup-logo" />
        <h2>Your Health, Our Priority</h2>
        <p>Join thousands of patients who trust us with their healthcare needs.</p>
      </div>
      <div className="left-info">
        <div className="info-item">
          <Shield className="icon" />
          <div>
            <h4>HIPAA Compliant</h4>
            <p>Your medical data is encrypted and secure.</p>
          </div>
        </div>
        <div className="info-item">
          <CheckCircle2 className="icon" />
          <div>
            <h4>24/7 Support</h4>
            <p>Our healthcare team is always here to help.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

