import { Link } from "react-router-dom";
import { useTranslation } from "../../../hooks/useTranslation";

export default function SignupFooter() {
  const { t } = useTranslation();
  
  return (
    <p className="signin-text">
      {t('auth.hasAccount')} <Link to="/login">{t('auth.loginNow')}</Link>
    </p>
  );
}

