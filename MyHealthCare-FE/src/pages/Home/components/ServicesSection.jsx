import { Stethoscope, Calendar, User, Clock } from "lucide-react";
import { useTranslation } from "../../../hooks/useTranslation";
import "./ServicesSection.css";

export default function ServicesSection() {
  const { t } = useTranslation();

  const services = [
    {
      icon: Stethoscope,
      title: t('home.generalConsultation'),
      description: t('home.generalConsultationDesc'),
    },
    {
      icon: Calendar,
      title: t('home.easyBooking'),
      description: t('home.easyBookingDesc'),
    },
    {
      icon: User,
      title: t('home.patientPortal'),
      description: t('home.patientPortalDesc'),
    },
    {
      icon: Clock,
      title: t('home.support247'),
      description: t('home.support247Desc'),
    },
  ];

  return (
    <section id="services" className="services-section">
      <div className="section-container">
        <div className="section-header">
          <h2 className="section-title">{t('home.ourServices')}</h2>
          <p className="section-subtitle">
            {t('home.ourServicesSubtitle')}
          </p>
        </div>

        <div className="services-grid">
          {services.map((service, index) => {
            const IconComponent = service.icon;
            return (
              <div key={index} className="service-card">
                <div className="service-icon-wrapper">
                  <IconComponent className="service-icon" />
                </div>
                <div className="service-content">
                  <h3 className="service-title">{service.title}</h3>
                  <p className="service-description">{service.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

