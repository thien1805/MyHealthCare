import React, { useRef } from "react";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import { useAuth } from "../../context/AuthContext";
import { useTranslation } from "../../hooks/useTranslation";
import "./Medical.css";
import Dashboard from "../Doctor-dashboard/DoctorDashboard";

const Services = () => {
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

  const services = [
    {
      image: "/homePage_images/whole-body-thumb.jpg",
      title: t('medical.generalCheckup'),
      description: t('medical.generalCheckupDesc'),
      details: t('medical.generalCheckupDetails')
    },
    {
      image: "/homePage_images/advancedCheckUp.png",
      title: t('medical.advancedCheckup'),
      description: t('medical.advancedCheckupDesc'),
      details: t('medical.advancedCheckupDetails')
    },
    {
      image: "/homePage_images/healthcheckup.jpeg",
      title: t('medical.basicCheckup'),
      description: t('medical.basicCheckupDesc'),
      details: t('medical.basicCheckupDetails')
    },
    {
      image: "/homePage_images/specifiedCheckUp.png",
      title: t('medical.specializedCheckup'),
      description: t('medical.specializedCheckupDesc'),
      details: t('medical.specializedCheckupDetails')
    },
    {
      image: "/homePage_images/radiologist.jpg",
      title: t('medical.imagingDiagnosis'),
      description: t('medical.imagingDiagnosisDesc'),
      details: t('medical.imagingDiagnosisDetails')
    },
    {
      image: "/homePage_images/the-basics-of-bone-joint-care-web.jpg",
      title: t('medical.boneJointCare'),
      description: t('medical.boneJointCareDesc'),
      details: t('medical.boneJointCareDetails')
    },
    {
      image: "/homePage_images/Pediatrics.jpeg",
      title: t('medical.pediatricsService'),
      description: t('medical.pediatricsServiceDesc'),
      details: t('medical.pediatricsServiceDetails')
    },
    {
      image: "/homePage_images/OB-GYN.jpg",
      title: t('medical.obgynService'),
      description: t('medical.obgynServiceDesc'),
      details: t('medical.obgynServiceDetails')
    },
    {
      image: "/homePage_images/bethesda-naval-medical-center.jpg",
      title: t('medical.entService'),
      description: t('medical.entServiceDesc'),
      details: t('medical.entServiceDetails')
    }
  ];

  const checkupPackages = services.slice(0, 4);
  const specialties = services.slice(4);
  const specialtiesRef = useRef(null);

  const scrollSpecialties = (direction) => {
    const container = specialtiesRef.current;
    if (!container) return;

    const scrollAmount = container.clientWidth * 0.8;
    container.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth"
    });
  };

  const serviceCategories = [
    {
      name: t('medical.preventiveCare'),
      description: t('medical.preventiveCareDesc'),
      icon: "🛡️"
    },
    {
      name: t('medical.diagnosticServices'),
      description: t('medical.diagnosticServicesDesc'),
      icon: "🔬"
    },
    {
      name: t('medical.specializedCare'),
      description: t('medical.specializedCareDesc'),
      icon: "⚕️"
    },
    {
      name: t('medical.emergencyServices'),
      description: t('medical.emergencyServicesDesc'),
      icon: "🚑"
    }
  ];

  return (
    <div className="services-page">
      <Header />

      <main className="services-main">
        {/* Hero Section */}
        <section className="services-hero">
          <div className="hero-content">
            <h1>{t('medical.pageTitle')}</h1>
            <p>{t('medical.pageSubtitle')}</p>
          </div>
        </section>

        {/* Service Categories */}
        <section className="categories-section">
          <div className="section-container">
            <h2 className="section-title">{t('medical.serviceCategories')}</h2>
            <div className="categories-grid">
              {serviceCategories.map((category, index) => (
                <div key={index} className="category-card">
                  <div className="category-icon">{category.icon}</div>
                  <h3>{category.name}</h3>
                  <p>{category.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* All Services */}
        <section className="all-services-section">
          <div className="section-container">
            <div className="section-header">
              <h2 className="section-title">{t('common.medicalServices')}</h2>
              <p className="section-subtitle">
                {t('medical.pageSubtitle')}
              </p>
            </div>

            <div className="checkup-section">
              <div className="subsection-header">
                <div>
                  <h3 className="subsection-title">{t('medical.checkupPackages')}</h3>

                </div>
              </div>

              <div className="services-grid checkup-grid">
                {checkupPackages.map((service, index) => (
                  <div key={index} className="service-card">
                    <div className="service-image-wrapper">
                      <img 
                        src={service.image} 
                        alt={service.title}
                        className="service-image"
                      />
                    </div>
                    <div className="service-content">
                      <h3 className="service-title">{service.title}</h3>
                      <p className="service-description">{service.description}</p>
                      <p className="service-details">{service.details}</p>
                      <Link to={bookingPath} className="service-link">
                        {t('home.bookAppointment')} <ArrowRight className="link-icon" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="specialties-section">
              <div className="specialties-top">
                <div>
                  <h3 className="subsection-title">{t('medical.specialties')}</h3>
                  <p className="subsection-subtitle">
                    {t('common.viewMore')}
                  </p>
                </div>
                <div className="slider-controls">
                  <button 
                    className="slider-btn" 
                    type="button" 
                    onClick={() => scrollSpecialties("left")}
                    aria-label="Scroll specialties left"
                  >
                    &lt;
                  </button>
                  <button 
                    className="slider-btn" 
                    type="button" 
                    onClick={() => scrollSpecialties("right")}
                    aria-label="Scroll specialties right"
                  >
                    &gt;
                  </button>
                </div>
              </div>

              <div className="specialties-track-wrapper">
                <div className="specialties-track" ref={specialtiesRef}>
                  {specialties.map((service, index) => (
                    <div key={index} className="service-card specialty-card">
                      <div className="service-image-wrapper">
                        <img 
                          src={service.image} 
                          alt={service.title}
                          className="service-image"
                        />
                      </div>
                      <div className="service-content">
                        <h3 className="service-title">{service.title}</h3>
                        <p className="service-description">{service.description}</p>
                        <p className="service-details">{service.details}</p>
                        <Link to={bookingPath} className="service-link">
                          {t('home.bookAppointment')} <ArrowRight className="link-icon" />
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="services-cta">
          <div className="cta-content">
            <h2>Need Help Choosing the Right Service?</h2>
            <p>Our healthcare advisors are here to guide you</p>
            <div className="cta-buttons">
              <a href="tel:+84765628670" className="btn-secondary">
                Call Us Now
              </a>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default Services;
