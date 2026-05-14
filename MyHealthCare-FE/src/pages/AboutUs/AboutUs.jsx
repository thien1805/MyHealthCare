import React from "react";
import Logo from "../../components/Logo/Logo";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import { useTranslation } from "../../hooks/useTranslation";
import "./AboutUs.css";

const AboutUs = () => {
  const { t } = useTranslation();

  return (
    <div className="aboutus-page">
      <Header />
      
      <main>
        <div className="container">
          <h1>{t('aboutUs.pageTitle')}</h1>

          <section className="about-hospital">
            <h2>{t('aboutUs.welcomeTitle')}</h2>
            <div className="content-wrapper">
              <div className="text-content">
                <p dangerouslySetInnerHTML={{ __html: t('aboutUs.welcomeText1') }} />
                <p>{t('aboutUs.welcomeText2')}</p>
              </div>
              <div className="image-wrapper">
                <img
                  src="/aboutUs_img/doctors-team.png"
                  alt="Doctor teams in UIT Hospital"
                />
              </div>
            </div>
          </section>

          <section className="about-website">
            <h2>{t('aboutUs.websiteTitle')}</h2>
            <p>{t('aboutUs.websiteText1')}</p>
            <p>{t('aboutUs.websiteText2')}</p>
          </section>

          <section className="features">
            <h2>{t('aboutUs.featuresTitle')}</h2>
            <p>{t('aboutUs.featuresIntro')}</p>

            <div className="features-grid">
              <div className="feature-item">
                <h3>{t('aboutUs.feature1Title')}</h3>
                <p>{t('aboutUs.feature1Desc')}</p>
              </div>
              <div className="feature-item">
                <h3>{t('aboutUs.feature2Title')}</h3>
                <p>{t('aboutUs.feature2Desc')}</p>
              </div>
              <div className="feature-item">
                <h3>{t('aboutUs.feature3Title')}</h3>
                <p>{t('aboutUs.feature3Desc')}</p>
              </div>
              <div className="feature-item">
                <h3>{t('aboutUs.feature4Title')}</h3>
                <p>{t('aboutUs.feature4Desc')}</p>
              </div>
            </div>
          </section>

          <section className="commitment">
            <h2>{t('aboutUs.commitmentTitle')}</h2>
            <p>{t('aboutUs.commitmentText')}</p>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default AboutUs;