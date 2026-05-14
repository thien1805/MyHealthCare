import React, { useEffect } from "react";
import Header from "../../components/Header";
import Footer from "../../components/Footer";
import Carousel from "./Carousel";
import ServicesSection from "./components/ServicesSection";
import WhyChooseSection from "./components/WhyChooseSection";
import CTASection from "./components/CTASection";
import "./home.css";

const Home = () => {
  useEffect(() => {
    const reveals = document.querySelectorAll(".reveal-block");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );

    reveals.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="home-page">
      <Header />

      <main className="main-content">
        {/* Hero Section with Carousel */}
        <section className="hero-section">
          <div className="hero-container">
            <div className="carousel-wrapper">
              <Carousel />
            </div>
          </div>
        </section>

        {/* Our Services Section */}
        <div className="reveal-block reveal-fade-up">
          <ServicesSection />
        </div>

        {/* Why Choose MyHealthCare Section */}
        <div className="reveal-block reveal-slide-right">
          <WhyChooseSection />
        </div>

        {/* Ready to Get Started Section */}
        <div className="reveal-block reveal-zoom-in">
          <CTASection />
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Home;
