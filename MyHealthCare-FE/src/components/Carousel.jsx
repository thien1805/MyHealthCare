// 

import React, { useState, useEffect } from "react";
import "./Carousel.css";

export default function Carousel({ 
  slides = [], 
  height = "500px",
  autoPlayInterval = 5000,
  showNav = true,
  showText = true,
  showDots = false,
  className = ""
}) {
  const [current, setCurrent] = useState(0);

  const nextSlide = () => setCurrent((prev) => (prev + 1) % slides.length);
  const prevSlide = () => setCurrent((prev) => (prev - 1 + slides.length) % slides.length);

  useEffect(() => {
    if (autoPlayInterval > 0 && slides.length > 0) {
      const interval = setInterval(nextSlide, autoPlayInterval);
      return () => clearInterval(interval);
    }
  }, [autoPlayInterval, slides.length]);

  if (!slides || slides.length === 0) {
    return <div className="carousel-empty">No slides available</div>;
  }

  return (
    <div className={`carousel ${className}`} style={{ height }}>
      {slides.map((slide, i) => (
        <div
          key={i}
          className={`carousel-slide ${i === current ? "active" : ""}`}
          style={{ backgroundImage: `url(${slide.image})` }}
        >
          {showText && slide.text && (
            <div className="slide-content">
              {slide.text.split("\n").map((line, idx) => (
                <div key={idx}>{line}</div>
              ))}
            </div>
          )}
        </div>
      ))}

      {showNav && slides.length > 1 && (
        <div className="carousel-nav">
          <button className="carousel-btn prev-btn" onClick={prevSlide} aria-label="Previous slide">
            ‹
          </button>
          <button className="carousel-btn next-btn" onClick={nextSlide} aria-label="Next slide">
            ›
          </button>
        </div>
      )}

      {showDots && slides.length > 1 && (
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
      )}
    </div>
  );
}