import { Heart } from 'lucide-react';
import Logo from '../../../components/Logo/Logo';
import { useTranslation } from '../../../hooks/useTranslation';

export default function LoginHeader() {
  const { t } = useTranslation();
  
  return (
    <div className="text-center mb-8 animate-fade-in">
      <Logo />
      <p className="text-gray-600 font-medium">{t('auth.loginSubtitle')}</p>
    </div>
  );
}

