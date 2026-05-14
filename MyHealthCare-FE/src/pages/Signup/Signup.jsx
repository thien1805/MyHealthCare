import "./signup.css";
import { useSignup } from "./hooks/useSignup";
import { useTranslation } from "../../hooks/useTranslation";
import SignupLeft from "./components/SignupLeft";
import SignupHeader from "./components/SignupHeader";
import SignupMessages from "./components/SignupMessages";
import SignupForm from "./components/SignupForm";
import SignupFooter from "./components/SignupFooter";
import SignupSuccess from "./components/SignupSuccess";

export default function Signup() {
  const {
    formData,
    loading,
    errors,
    submitted,
    setSubmitted,
    handleChange,
    handleSubmit,
  } = useSignup();
  const { t } = useTranslation();

  if (submitted) {
    return <SignupSuccess onBack={() => setSubmitted(false)} />;
  }

  return (
    <div className="signup-page">
      <div className="signup-container">
        <SignupLeft />

        <div className="signup-right">
          <SignupHeader />

          <h2>{t('auth.signupTitle')}</h2>
          <p>{t('auth.signupSubtitle')}</p>

          <SignupMessages errors={errors} />

          <SignupForm
            formData={formData}
            errors={errors}
            loading={loading}
            onChange={handleChange}
            onSubmit={handleSubmit}
          />

          <SignupFooter />
        </div>
      </div>
    </div>
  );
}
