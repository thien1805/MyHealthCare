import React from 'react';
import { useLanguage, LANGUAGES } from '../../context/LanguageContext';
import './LanguageSwitcher.css';

const LanguageSwitcher = ({ variant = 'default' }) => {
  const { language, switchLanguage } = useLanguage();

  return (
    <div className={`language-switcher ${variant}`}>
      <button
        className={`lang-btn ${language === LANGUAGES.VI ? 'active' : ''}`}
        onClick={() => switchLanguage(LANGUAGES.VI)}
        title="Tiếng Việt"
      >
        <span className="lang-flag">🇻🇳</span>
        <span className="lang-text">VI</span>
      </button>
      <span className="lang-divider">|</span>
      <button
        className={`lang-btn ${language === LANGUAGES.EN ? 'active' : ''}`}
        onClick={() => switchLanguage(LANGUAGES.EN)}
        title="English"
      >
        <span className="lang-flag">🇬🇧</span>
        <span className="lang-text">EN</span>
      </button>
    </div>
  );
};

export default LanguageSwitcher;
