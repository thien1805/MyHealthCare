// src/pages/Login/hooks/useLogin.js
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { ADMIN_PANEL_URL } from '../../../api/authAPI';
import { useToast } from '../../../hooks/useToast';

export const useLogin = (toastApi) => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { success: showSuccess, error: showError } = toastApi || useToast();

  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async () => {
    if (!formData.email || !formData.password) {
      showError('Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      // Xoá token cũ
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');

      // Login qua AuthContext
      const result = await login({
        email: formData.email,
        password: formData.password,
      });

      console.log('Login result from AuthContext:', result);

      if (!result || !result.user) {
        throw new Error('Invalid response from server');
      }

      const user = result.user;
      console.log('User Info:', user);

      showSuccess('Login successful! Redirecting...', 2000);

      // Chuẩn hoá role
      const rawRole =
        user.role || user.accountType || user.userType || 'patient';
      const role = String(rawRole).toLowerCase();

      console.log(' Role after normalize:', role);

      // 👉 Redirect NGAY sau khi login thành công
      setTimeout(() => {
        if (role === 'doctor') {
          navigate('/doctor/dashboard');
        } else if (role === 'admin') {
          window.location.href = ADMIN_PANEL_URL;
        } else {
          // patient hoặc bất kỳ role nào khác
          navigate('/patient/dashboard');
        }
      }, 500);
    } catch (err) {
      console.error('Login error:', err);

      let errorMessage = 'Invalid email or password';

      if (typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        errorMessage =
          err.message ||
          err.detail ||
          err.error ||
          err.general ||
          'Invalid email or password';

        if (Array.isArray(err.message)) {
          errorMessage = err.message[0];
        } else if (Array.isArray(err.detail)) {
          errorMessage = err.detail[0];
        }
      }

      showError(errorMessage, 5000);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return {
    formData,
    loading,
    handleChange,
    handleSubmit,
    handleKeyPress,
  };
};
