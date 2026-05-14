import React from "react";
import {
  Facebook,
  Twitter,
  Instagram,
  Linkedin,
  Mail,
  Phone,
  MapPin,
} from "lucide-react";
import { Link } from "react-router-dom";
import Logo from "./Logo/Logo";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "../hooks/useTranslation";
import "./Footer.css";

const Footer = () => {
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
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-grid">
          {/* About */}
          <div className="footer-section">
            <Logo clickable={false} className="footer-logo-custom" />
            <p className="footer-description">
              {t('footer.trustedPartner')}
            </p>
            <div className="social-links">
              <a href="#" className="social-link">
                <Facebook className="social-icon" />
              </a>
              <a href="#" className="social-link">
                <Twitter className="social-icon" />
              </a>
              <a href="#" className="social-link">
                <Instagram className="social-icon" />
              </a>
              <a href="#" className="social-link">
                <Linkedin className="social-icon" />
              </a>
            </div>
          </div>

          <div className="footer-section">
            <h4 className="footer-title">{t('footer.quickLinks')}</h4>
            <ul className="footer-list">
              <li><Link to="#" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('common.home')}</Link></li>
              <li><Link to="/about" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('common.aboutUs')}</Link></li>
              <li><Link to="/medical" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('footer.services')}</Link></li>
              <li><Link to={bookingPath} className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('common.booking')}</Link></li>
            </ul>
          </div>

          {/* Services */}
          <div className="footer-section">
            <h4 className="footer-title">{t('footer.services')}</h4>
            <ul className="footer-list">
              <li><a href="/medical" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('medical.generalCheckup')}</a></li>
              <li><a href="/medical" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('departments.internalMedicine')}</a></li>
              <li><a href="/medical" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('departments.orthopedics')}</a></li>
              <li><a href="/medical" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('departments.pediatrics')}</a></li>
              <li><a href="/medical" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('departments.gynecology')}</a></li>
              <li><a href="/medical" className="footer-link" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>{t('departments.ent')}</a></li>

            </ul>
          </div>

          {/* Contact Info */}
          <div className="footer-section">
            <h4 className="footer-title">{t('footer.contact')}</h4>
            <ul className="contact-list">
              <li className="contact-item">
                <Phone className="contact-icon" />
                <a href="tel:+84765628670" className="contact-text">+84 765 628 670</a>
              </li>
              <li className="contact-item">
                <Mail className="contact-icon" />
                <a href="mailto:myhealthcare@gmail.com" target="_blank" rel="noopener noreferrer" className="contact-text">myhealthcare@gmail.com</a>
              </li>
              <li className="contact-item">
                <MapPin className="contact-icon" />
                <a href='https://www.google.com/maps/place/University+of+Information+Technology+-+VNUHCM/@10.8700142,106.8004792,814m/data=!3m2!1e3!4b1!4m6!3m5!1s0x317527587e9ad5bf:0xafa66f9c8be3c91!8m2!3d10.8700089!4d106.8030541!16s%2Fm%2F02qqlmm?entry=ttu&g_ep=EgoyMDI1MTExOC4wIKXMDSoASAFQAw%3D%3D' target="_blank" rel="noopener noreferrer" className="contact-text">6 Han Thuyen, Thu Duc</a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p className="copyright">
              {t('footer.copyright')}
            </p>
            <div className="footer-links">
              <a href="#" className="footer-bottom-link">{t('footer.privacyPolicy')}</a>
              <a href="#" className="footer-bottom-link">{t('footer.termsOfService')}</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
