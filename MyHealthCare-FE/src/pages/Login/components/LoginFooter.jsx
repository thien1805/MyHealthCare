import { useTranslation } from '../../../hooks/useTranslation';

export default function LoginFooter() {
  const { t } = useTranslation();
  
  return (
    <div className="mt-8 text-center text-xs text-gray-500 animate-fade-in">
      <p>{t('auth.secureLogin')}</p>
      <p className="mt-2">{t('auth.allRightsReserved')}</p>
    </div>
  );
}

