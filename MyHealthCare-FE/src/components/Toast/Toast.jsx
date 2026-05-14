import React, { useEffect, useRef } from "react";
import { Check, X, Info, AlertCircle } from "lucide-react";
import "./Toast.css";

export default function Toast({ message, type = "info", duration = 3000, onClose }) {
  // Dùng ref để giữ onClose mới nhất mà không trigger re-run useEffect
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  useEffect(() => {
    const timer = setTimeout(() => {
      onCloseRef.current?.();
    }, duration);
    return () => clearTimeout(timer);
  }, [duration]); // Chỉ chạy 1 lần khi mount hoặc duration thay đổi

  const icons = {
    success: <Check size={20} />,
    error: <X size={20} />,
    info: <Info size={20} />,
    warning: <AlertCircle size={20} />,
  };

  return (
    <div className={`toast toast-${type}`}>
      <div className="toast-icon">{icons[type]}</div>
      <span className="toast-message">{message}</span>
      <button className="toast-close" onClick={onClose}>
        ×
      </button>
    </div>
  );
}