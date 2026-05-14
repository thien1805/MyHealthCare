import React, { useState, useCallback } from "react";
import Toast from "../components/Toast/Toast";
import { useMemo } from "react";

function ToastContainerComponent({ toasts, onClose }) {
  const closeHandlers = useMemo(
    () => new Map(toasts.map((t) => [t.id, () => onClose(t.id)])),
    [toasts, onClose]
  );
  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => onClose(toast.id)}
          duration={toast.duration}
        />
      ))}
    </div>
  );
}

export function useToast() {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((message, type = "info", duration = 3000) => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type, duration }]);
    return id;
  }, []);

  const hideToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const ToastContainer = useCallback(
    () => <ToastContainerComponent toasts={toasts} onClose={hideToast} />,
    [toasts, hideToast]
  );
  return {
    showToast,
    hideToast,
    ToastContainer,
    success: useCallback((msg, duration) => showToast(msg, "success", duration), [showToast]),
    error: useCallback((msg, duration) => showToast(msg, "error", duration), [showToast]),
    info: useCallback((msg, duration) => showToast(msg, "info", duration), [showToast]),
    warning: useCallback((msg, duration) => showToast(msg, "warning", duration), [showToast]),
  };
}
