import { AlertCircle } from "lucide-react";

export default function SignupMessages({ errors }) {
  if (!errors.general) return null;

  return (
    <div className="general-error">
      <AlertCircle className="error-icon" />
      <span>{errors.general}</span>
    </div>
  );
}

