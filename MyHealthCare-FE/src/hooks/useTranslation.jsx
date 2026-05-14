import { useLanguage, LANGUAGES } from '../context/LanguageContext';
import viTranslations from '../locales/vi.json';
import enTranslations from '../locales/en.json';

const translations = {
  [LANGUAGES.VI]: viTranslations,
  [LANGUAGES.EN]: enTranslations
};

/**
 * Hook to get translations based on current language
 * @returns {Object} { t: function, language: string }
 * 
 * Usage:
 * const { t, language } = useTranslation();
 * <h1>{t('common.home')}</h1>
 * <p>{t('booking.title')}</p>
 */
export const useTranslation = () => {
  const { language } = useLanguage();
  
  /**
   * Get translation by key path (e.g., 'common.home', 'booking.title')
   * @param {string} keyPath - Dot-separated key path
   * @param {Object} params - Optional parameters for string interpolation
   * @returns {string} Translated string or key if not found
   */
  const t = (keyPath, params = {}) => {
    const keys = keyPath.split('.');
    let value = translations[language];
    
    for (const key of keys) {
      if (value && typeof value === 'object' && key in value) {
        value = value[key];
      } else {
        // Return the key if translation not found
        console.warn(`Translation not found: ${keyPath}`);
        return keyPath;
      }
    }
    
    // Handle string interpolation {{variable}}
    if (typeof value === 'string' && Object.keys(params).length > 0) {
      return value.replace(/\{\{(\w+)\}\}/g, (match, paramKey) => {
        return params[paramKey] !== undefined ? params[paramKey] : match;
      });
    }
    
    return value;
  };
  
  /**
   * Get locale string based on current language
   * @returns {string} Locale string (e.g., 'vi-VN', 'en-US')
   */
  const getLocale = () => {
    return language === 'vi' ? 'vi-VN' : 'en-US';
  };

  /**
   * Format date according to current language
   * @param {string|Date} dateStr - Date string or Date object
   * @param {Object} options - Intl.DateTimeFormat options
   * @returns {string} Formatted date
   */
  const formatDate = (dateStr, options = {}) => {
    if (!dateStr) return "N/A";
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return dateStr;
      
      const defaultOptions = {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        ...options
      };
      
      return date.toLocaleDateString(getLocale(), defaultOptions);
    } catch {
      return dateStr;
    }
  };

  /**
   * Format time according to current language
   * @param {string} timeStr - Time string (HH:MM:SS or HH:MM)
   * @returns {string} Formatted time (HH:MM)
   */
  const formatTime = (timeStr) => {
    if (!timeStr) return "N/A";
    // Just return HH:MM format
    if (/^\d{2}:\d{2}(:\d{2})?$/.test(timeStr)) {
      return timeStr.slice(0, 5);
    }
    return timeStr;
  };

  /**
   * Format datetime according to current language
   * @param {string|Date} dateTimeStr - DateTime string or Date object
   * @returns {string} Formatted datetime
   */
  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return "N/A";
    try {
      const date = new Date(dateTimeStr);
      if (isNaN(date.getTime())) return dateTimeStr;
      
      return date.toLocaleString(getLocale(), {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateTimeStr;
    }
  };
  
  return { t, language, getLocale, formatDate, formatTime, formatDateTime };
};

/**
 * Get translation without hook (for use outside components)
 * @param {string} lang - Language code ('vi' or 'en')
 * @param {string} keyPath - Dot-separated key path
 * @returns {string} Translated string
 */
export const getTranslation = (lang, keyPath) => {
  const keys = keyPath.split('.');
  let value = translations[lang] || translations[LANGUAGES.VI];
  
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      return keyPath;
    }
  }
  
  return value;
};

export default useTranslation;
