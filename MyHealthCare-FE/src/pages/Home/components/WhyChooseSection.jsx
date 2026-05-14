import { CheckCircle2 } from "lucide-react";
import { useTranslation } from "../../../hooks/useTranslation";
import "./WhyChooseSection.css";

export default function WhyChooseSection() {
  const { t } = useTranslation();

  const whyChoose = [
    {
      title: t('home.expertTeam'),
      description: t('home.expertTeamDesc'),
    },
    {
      title: t('home.modernFacilities'),
      description: t('home.modernFacilitiesDesc'),
    },
    {
      title: t('home.patientCare'),
      description: t('home.patientCareDesc'),
    },
  ];

  return (
    <section className="why-choose-section">
      <div className="section-container">
        <div className="why-choose-content">
          <div className="why-choose-text">
            <h2 className="section-title">{t('home.whyChooseUs')}</h2>
            <div className="why-choose-list">
              {whyChoose.map((item, index) => (
                <div key={index} className="why-choose-item">
                  <CheckCircle2 className="check-icon" />
                  <div>
                    <h3 className="why-choose-item-title">{item.title}</h3>
                    <p className="why-choose-item-description">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="why-choose-image">
            <img 
              src="/homePage_images/medical-equipment.jpg" 
              alt="Modern medical facilities"
              className="why-choose-img"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

