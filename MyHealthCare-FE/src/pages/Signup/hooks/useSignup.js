import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register } from "../../../api/authAPI";

export function useSignup() {
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    phone_num: "",
    date_of_birth: "",
    password: "",
    password_confirm: "",
    gender: "",
    role: "patient",
    address: "",
    termsAccepted: false,
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [errors, setErrors] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const validateForm = () => {
    const newErrors = {};
    if (!formData.full_name.trim()) newErrors.full_name = "Full name is required";
    if (!formData.email.trim()) newErrors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = "Email is invalid";
    if (!formData.phone_num.trim()) newErrors.phone_num = "Phone number is required";
    if (!formData.date_of_birth) newErrors.date_of_birth = "Date of birth is required";
    if (!formData.gender) newErrors.gender = "Gender is required";
    if (!formData.address.trim()) newErrors.address = "Address is required";
    if (!formData.password) newErrors.password = "Password is required";
    else if (formData.password.length < 8)
      newErrors.password = "Password must be at least 8 characters";
    
    // Check password_confirm
    if (!formData.password_confirm) {
      newErrors.password_confirm = "This field is required";
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = "Passwords do not match";
    }

    
    if (!formData.termsAccepted)
      newErrors.termsAccepted = "You must accept the terms and conditions";
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validateForm();
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    // Chuẩn hóa payload theo API
    const {
      termsAccepted,
      ...rest
    } = formData;

    const dataToSend = {
      ...rest,
      role: "patient",
    };

    setLoading(true);
    setErrors({});

    try {
      const response = await register(dataToSend);
      console.log("✅ Register API call thành công - không có exception");
      console.log("Register response:", response);
      console.log("Register response type:", typeof response);
      console.log("Register response keys:", response && typeof response === 'object' ? Object.keys(response) : 'no keys');
      console.log("Register response.success:", response?.success);

      const successMessage = response?.message || 
                           response?.detail || 
                           "Register successfully! Please log in to continue.";
      
      console.log("✅ Đăng ký thành công! User cần login để tiếp tục...");
      alert(successMessage);
      navigate("/login");
      
    } catch (error) {
      console.error("❌ Register error - có exception:", error);

      const backendData = error;
      const backendErrors = {};

      if (!backendData) {
        setErrors({ general: 'Network error. Please check your connection and try again.' });
      } else if (Array.isArray(backendData)) {
        setErrors({ general: backendData[0] || 'Register failed. Please try again.' });
      } else if (typeof backendData === 'object') {
        Object.keys(backendData).forEach((key) => {
          const value = backendData[key];
          if (Array.isArray(value)) {
            backendErrors[key] = value[0];
          } else if (typeof value === 'string') {
            backendErrors[key] = value;
          } else if (value !== null && value !== undefined) {
            backendErrors[key] = JSON.stringify(value);
          }
        });

        if (backendErrors.detail) {
          backendErrors.general = backendErrors.detail;
          delete backendErrors.detail;
        }
        if (backendErrors.non_field_errors) {
          backendErrors.general = backendErrors.non_field_errors;
          delete backendErrors.non_field_errors;
        }
        if (backendErrors.message) {
          backendErrors.general = backendErrors.message;
          delete backendErrors.message;
        }

        if (backendErrors.email) {
          setFormData((prev) => ({
            ...prev,
            email: '',
            password: '',
            password_confirm: '',
          }));
        }

        if (backendErrors.phone_num) {
          setFormData((prev) => ({
            ...prev,
            phone_num: '',
          }));
        }

        if (Object.keys(backendErrors).length === 0) {
          setErrors({ general: 'Register failed. Please check your information and try again.' });
        } else {
          setErrors(backendErrors);
        }
      } else {
        console.error("Unknown error format:", backendData);
        setErrors({ general: 'An unexpected error occurred. Please try again later.' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  return {
    formData,
    loading,
    errors,
    submitted,
    setSubmitted,
    handleChange,
    handleSubmit,
  };
}

