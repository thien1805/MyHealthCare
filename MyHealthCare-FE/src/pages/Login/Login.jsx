import './login.css';
import { useToast } from '../../hooks/useToast';
import { useLogin } from './hooks/useLogin';
import AnimatedBackground from './components/AnimatedBackground';
import LoginHeader from './components/LoginHeader';
import LoginForm from './components/LoginForm';
import LoginFooter from './components/LoginFooter';
import Logo from '../../components/Logo/Logo'

export default function LoginPage() {
  const toast = useToast();
  const { ToastContainer } = toast;
  const {
    formData,
    loading,
    handleChange,
    handleSubmit,
    handleKeyPress,
  } = useLogin(toast);

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-blue-50 to-blue-100 flex items-center justify-center p-4 relative overflow-hidden">
      <AnimatedBackground />
      <ToastContainer />

      <div className="w-full max-w-md relative z-10">
        <LoginHeader />

        {/* Form Card with Glass Effect */}
        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20 animate-slide-up">
          <LoginForm
            formData={formData}
            loading={loading}
            onFormChange={handleChange}
            onKeyPress={handleKeyPress}
            onSubmit={handleSubmit}
          />
        </div>

        <LoginFooter />
      </div>
    </div>
  );
}