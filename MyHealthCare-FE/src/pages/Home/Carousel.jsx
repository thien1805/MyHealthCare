import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useTranslation } from "../../hooks/useTranslation";
import "./Carousel.css";

// Import images
import homepage1 from "../../assets/homePage_images/homepage1.png";
import homepage2 from "../../assets/homePage_images/homepage2.png";
import homepage3 from "../../assets/homePage_images/homepage3.png";

export default function Carousel() {
  const [current, setCurrent] = useState(0);
  const { isAuth, user } = useAuth();
  const { t } = useTranslation();

  const slides = [
    {
      image: homepage1,
      title: t('home.slide1Title'),
      subtitle: t('home.slide1Subtitle'),
    },
    {
      image: homepage2,
      title: t('home.slide2Title'),
      subtitle: t('home.slide2Subtitle'),
    },
    {
      image: homepage3,
      title: t('home.slide3Title'),
      subtitle: t('home.slide3Subtitle'),
    },
  ];

  const role =
    user?.role || user?.accountType || user?.userType || "patient";
  const isPatient = role === "patient";

  const bookingPath = !isAuth
    ? "/signup"
    : isPatient
    ? "/patient/appointments"
    : "/doctor/dashboard";

  const nextSlide = () => setCurrent((prev) => (prev + 1) % slides.length);
  const prevSlide = () => setCurrent((prev) => (prev - 1 + slides.length) % slides.length);

  useEffect(() => {
    const interval = setInterval(nextSlide, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="carousel">
      {slides.map((slide, i) => (
        <div
          key={i}
          className={`carousel-slide ${i === current ? "active" : ""}`}
          style={{ backgroundImage: `url(${slide.image})` }}
        >
          <div className="slide-content">
            <h1 className="slide-title">{slide.title}</h1>
            <p className="slide-subtitle">{slide.subtitle}</p>
          </div>
        </div>
      ))}

      {/* Fixed Button */}
      <div className="slide-button-wrapper">
        <Link to={bookingPath} className="slide-button">
          {t('home.bookAppointment')}
        </Link>
      </div>

      {/* Navigation arrows */}
      <div className="carousel-nav">
        <button className="carousel-btn prev-btn" onClick={prevSlide}>
          ‹
        </button>
        <button className="carousel-btn next-btn" onClick={nextSlide}>
          ›
        </button>
      </div>

      {/* Dots indicator */}
      <div className="carousel-dots">
        {slides.map((_, i) => (
          <button
            key={i}
            className={`carousel-dot ${i === current ? "active" : ""}`}
            onClick={() => setCurrent(i)}
            aria-label={`Go to slide ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
