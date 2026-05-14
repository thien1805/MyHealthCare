import { Link } from "react-router-dom";
import { useAuth } from "../../../context/AuthContext";
import { useTranslation } from "../../../hooks/useTranslation";
import "./CTASection.css";

export default function CTASection() {
  const { isAuth, user } = useAuth();
  const { t } = useTranslation();

  const role =
    user?.role || user?.accountType || user?.userType || "patient";
  const isPatient = role === "patient";

  const bookingPath = !isAuth
    ? "/signup"
    : isPatient
    ? "/patient/appointments"
    : "/doctor/dashboard";

  return (
    <section className="cta-section">
      <div className="cta-container">
        <h2 className="cta-title">{t('home.readyToStart')}</h2>
        <p className="cta-subtitle">
          {t('home.readyToStartSubtitle')}
        </p>
        <div className="cta-buttons">
          <Link to={bookingPath} className="btn-cta-primary">
            {t('home.bookAppointment')}
          </Link>
          <Link to="/medical" className="btn-cta-secondary">
            {t('home.learnMore')}
          </Link>
        </div>
      </div>
    </section>
  );
}
