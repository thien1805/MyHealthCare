import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, CheckCircle, Loader2 } from 'lucide-react';
import { useTranslation } from '../../../hooks/useTranslation';

export default function LoginForm({ formData, loading, onFormChange, onKeyPress, onSubmit }) {
  const [showPassword, setShowPassword] = useState(false);
  const [focusedField, setFocusedField] = useState('');
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      {/* Email Field with Icon & Animation */}
      <div className="transform transition-all duration-300 hover:scale-[1.02]">
        <label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <Mail className="w-4 h-4 text-blue-600" />
          {t('auth.emailAddress')}
        </label>
        <div className="relative">
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={onFormChange}
            onKeyPress={onKeyPress}
            onFocus={() => setFocusedField('email')}
            onBlur={() => setFocusedField('')}
            placeholder={t('auth.emailPlaceholder')}
            className={`w-full px-4 py-3.5 bg-gray-50 border-2 rounded-xl focus:outline-none transition-all duration-300 ${
              focusedField === 'email' 
                ? 'border-blue-500 shadow-lg shadow-blue-100 bg-white' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
          />
          {formData.email && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <CheckCircle className="w-5 h-5 text-green-500 animate-scale-in" />
            </div>
          )}
        </div>
      </div>

      {/* Password Field with Icon & Animation */}
      <div className="transform transition-all duration-300 hover:scale-[1.02]">
        <label className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <Lock className="w-4 h-4 text-blue-600" />
          {t('auth.password')}
        </label>
        <div className="relative">
          <input
            type={showPassword ? "text" : "password"}
            name="password"
            value={formData.password}
            onChange={onFormChange}
            onKeyPress={onKeyPress}
            onFocus={() => setFocusedField('password')}
            onBlur={() => setFocusedField('')}
            placeholder={t('auth.passwordPlaceholder')}
            className={`w-full px-4 py-3.5 bg-gray-50 border-2 rounded-xl focus:outline-none transition-all duration-300 pr-12 ${
              focusedField === 'password' 
                ? 'border-blue-500 shadow-lg shadow-blue-100 bg-white' 
                : 'border-gray-200 hover:border-gray-300'
            }`}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-300 transition-all duration-300 hover:scale-110"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Remember & Forgot */}
      <div className="flex items-center justify-between text-sm">
        <label className="flex items-center gap-2 cursor-pointer group">
          <input 
            type="checkbox" 
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 transition-all cursor-pointer" 
          />
          <span className="text-gray-600 group-hover:text-gray-900 transition-colors">{t('auth.rememberMe')}</span>
        </label>
        <Link
          to="/forgot-password"
          className="text-blue-600 hover:text-blue-700 font-semibold hover:underline transition-all"
        >
          {t('auth.forgotPassword')}
        </Link>
      </div>

      {/* Submit Button with Gradient & Animation */}
      <button
        onClick={onSubmit}
        disabled={loading}
        className="w-full bg-gradient-to-r from-sky-300 to-blue-300 hover:from-sky-400 hover:to-blue-400 text-white font-bold py-4 px-4 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-95"
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            {t('auth.signingIn')}
          </>
        ) : (
          <>
            <Lock className="w-5 h-5" />
            {t('auth.signIn')}
          </>
        )}
      </button>

      {/* Divider */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200"></div>
        </div>
      </div>

      {/* Register Link */}
      <div className="mt-8 text-center text-sm">
        <span className="text-gray-600">{t('auth.noAccount')}</span>{' '}
        <Link to="/signup" className="text-blue-600 hover:text-blue-700 font-bold hover:underline transition-all">
          {t('auth.registerNow')} →
        </Link>
      </div>
    </div>
  );
}

