// src/pages/PatientDashboard/components/records/MedicalRecordList.jsx
import React, { useState, useMemo, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "../../../../hooks/useTranslation";
import { payMedicalRecord } from "../../../../api/medicalRecordAPI";

export default function MedicalRecordList({
  appointments = [],
  records = [],
  toast,
  onRefresh,
}) {
  const { t } = useTranslation();
  
  // Lọc các lịch đã khám xong (hoặc history)
  const historyAppointments = useMemo(() => {
    if (!Array.isArray(appointments)) return [];
    // Nếu bạn muốn lấy tất cả appointments thì bỏ filter status
    return appointments.filter((a) => a.status === "completed");
  }, [appointments]);

  const navigate = useNavigate();

  const [selectedId, setSelectedId] = useState(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [paying, setPaying] = useState(false);

  // Auto chọn appointment đầu tiên khi có dữ liệu
  useEffect(() => {
    if (historyAppointments.length > 0 && !selectedId) {
      setSelectedId(historyAppointments[0].id);
    }
  }, [historyAppointments, selectedId]);

  const selectedAppt = historyAppointments.find(
    (a) => a.id === selectedId
  );

  // Nếu backend sau này trả records riêng, có thể map theo appointmentId
  const findRecordForAppointment = (appt) => {
    if (!appt) return null;

    // 1. Nếu appointment có sẵn medicalRecord embedded từ API
    if (appt.medicalRecord) {
      return {
        ...appt.medicalRecord,
        id: appt.medicalRecord.id || appt.medicalRecord.record_id,
      };
    }

    // 2. Nếu records là mảng có field appointmentId
    if (Array.isArray(records) && records.length > 0) {
      const found = records.find((r) => r.appointmentId === appt.id);
      if (found) return found;
    }

    return null;
  };

  const selectedRecord = findRecordForAppointment(selectedAppt);

  // Handler for view detail - can use either record id or appointment id
  const handleViewDetail = () => {
    if (selectedRecord?.id) {
      navigate(`/patient/medical-record/${selectedRecord.id}`);
    } else if (selectedAppt?.id) {
      // Fallback: navigate to appointment detail which shows medical record
      navigate(`/patient/appointment/${selectedAppt.id}`);
    }
  };

  // Payment handler
  const handlePayment = async () => {
    if (!selectedAppt?.id) return;
    
    setPaying(true);
    try {
      const result = await payMedicalRecord(selectedAppt.id, paymentMethod);
      if (result.success) {
        toast?.success?.(t("payment.paymentSuccess") || "Payment completed successfully!");
        setShowPaymentModal(false);
        // Refresh appointments to get updated payment status
        if (onRefresh) onRefresh();
      } else {
        toast?.error?.(result.error || t("payment.paymentFailed") || "Payment failed");
      }
    } catch (error) {
      console.error("Payment error:", error);
      toast?.error?.(error?.error || error?.message || t("payment.paymentFailed") || "Payment failed");
    } finally {
      setPaying(false);
    }
  };

  // Format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount || 0);
  };

  // Get payment status display
  const getPaymentStatusDisplay = (record) => {
    if (!record) return null;
    
    const status = record.payment_status;
    if (status === 'paid') {
      return { label: t("payment.paid") || "Paid", className: "pd-status--completed" };
    } else if (status === 'not_required') {
      return { label: t("payment.free") || "Free", className: "pd-status--completed" };
    } else {
      return { label: t("payment.pending") || "Pending", className: "pd-status--upcoming" };
    }
  };

  return (
    <div className="pd-card">
      <h3 className="pd-section-title">My medical records</h3>

      {historyAppointments.length === 0 ? (
        <div className="pd-empty-tab">
          You don't have any records.
        </div>
      ) : (
        <div className="pd-history-layout">
          {/* Danh sách appointment bên trái */}
          <div className="pd-history-list">
            {historyAppointments.map((appt) => (
              <button
                key={appt.id}
                type="button"
                className={
                  "pd-history-item" +
                  (appt.id === selectedId ? " pd-history-item--active" : "")
                }
                onClick={() => setSelectedId(appt.id)}
              >
                <div className="pd-history-item-main">
                  <div className="pd-history-doctor">
                    {appt.doctorName}
                  </div>
                  <div className="pd-history-specialty">
                    {appt.specialty}
                  </div>
                </div>
                <div className="pd-history-item-meta">
                  <span>{appt.date}</span>
                  <span>{appt.time}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Medical record của appointment đã chọn */}
          <div className="pd-history-detail">
            {selectedAppt ? (
              <>
                <h4 className="pd-history-detail-title">
                  {t("patient.medicalRecords")}
                </h4>
                <div className="pd-history-detail-info">
                  <div>
                    <span className="pd-profile-label">{t("patient.doctor")}</span>
                    <div className="pd-profile-value">
                      {selectedAppt.doctorName}
                    </div>
                  </div>
                  <div>
                    <span className="pd-profile-label">{t("patient.specialty")}</span>
                    <div className="pd-profile-value">
                      {selectedAppt.specialty}
                    </div>
                  </div>
                  <div>
                    <span className="pd-profile-label">{t("patient.date")}</span>
                    <div className="pd-profile-value">
                      {selectedAppt.date} {selectedAppt.time}
                    </div>
                  </div>
                  {selectedAppt.location && (
                    <div>
                      <span className="pd-profile-label">{t("patient.location")}</span>
                      <div className="pd-profile-value">
                        {selectedAppt.location}
                      </div>
                    </div>
                  )}
                </div>

                <div className="pd-history-detail-record">
                  <span className="pd-profile-label">{t("patient.diagnosis")}</span>
                  <div className="pd-profile-value">
                    {selectedRecord?.diagnosis ||
                      t("patient.noDiagnosis")}
                  </div>

                  <span className="pd-profile-label" style={{ marginTop: 12 }}>
                    {t("patient.notesPrescription")}
                  </span>
                  <div className="pd-profile-value">
                    {selectedRecord?.notes ||
                      t("patient.noNotes")}
                  </div>

                  {/* Payment Section */}
                  {selectedRecord && (
                    <div className="pd-payment-section" style={{ marginTop: 16 }}>
                      <div className="pd-payment-info">
                        <div className="pd-payment-row">
                          <span className="pd-profile-label">{t("payment.serviceFee") || "Service Fee"}:</span>
                          <span className="pd-profile-value">{formatCurrency(selectedRecord.service_fee)}</span>
                        </div>
                        <div className="pd-payment-row">
                          <span className="pd-profile-label">{t("payment.examinationFee") || "Examination Fee"}:</span>
                          <span className="pd-profile-value">{formatCurrency(selectedRecord.examination_fee)}</span>
                        </div>
                        <div className="pd-payment-row pd-payment-total">
                          <span className="pd-profile-label" style={{ fontWeight: 600 }}>{t("payment.total") || "Total"}:</span>
                          <span className="pd-profile-value" style={{ fontWeight: 600, color: '#e53e3e' }}>
                            {formatCurrency(selectedRecord.total_fee)}
                          </span>
                        </div>
                        <div className="pd-payment-row">
                          <span className="pd-profile-label">{t("payment.status") || "Status"}:</span>
                          {getPaymentStatusDisplay(selectedRecord) && (
                            <span className={`pd-status-badge ${getPaymentStatusDisplay(selectedRecord).className}`}>
                              {getPaymentStatusDisplay(selectedRecord).label}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Pay Button - only show if pending and total > 0 */}
                      {selectedRecord.payment_status === 'pending' && selectedRecord.total_fee > 0 && (
                        <button
                          type="button"
                          className="pd-primary-btn pd-pay-btn"
                          style={{ marginTop: 12, background: '#38b2ac', color: 'white' }}
                          onClick={() => setShowPaymentModal(true)}
                        >
                          💳 {t("payment.payNow") || "Pay Now"}
                        </button>
                      )}
                    </div>
                  )}
                </div>

                <button
                  type="button"
                  className="pd-outline-btn"
                  style={{ alignSelf: "flex-start", marginTop: 8 }}
                  onClick={handleViewDetail}
                  disabled={!selectedRecord && !selectedAppt}
                >
                  {t("patient.viewDetail")}
                </button>
              </>
            ) : (
              <div className="pd-empty-tab">
                {t("patient.selectAppointmentToView")}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Payment Modal */}
      {showPaymentModal && selectedRecord && (
        <div className="pd-modal-overlay" onClick={() => setShowPaymentModal(false)}>
          <div className="pd-modal pd-payment-modal" onClick={(e) => e.stopPropagation()}>
            <h3 className="pd-modal-title">{t("payment.completePayment") || "Complete Payment"}</h3>
            
            <div className="pd-modal-content">
              <div className="pd-payment-summary">
                <p>{t("payment.paymentFor") || "Payment for medical service"}</p>
                <div className="pd-payment-amount">
                  {formatCurrency(selectedRecord.total_fee)}
                </div>
              </div>

              <div className="pd-payment-methods">
                <label className="pd-payment-method-label">{t("payment.selectMethod") || "Select payment method"}:</label>
                
                <div className="pd-payment-method-options">
                  <label className={`pd-payment-option ${paymentMethod === 'card' ? 'pd-payment-option--selected' : ''}`}>
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="card"
                      checked={paymentMethod === 'card'}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                    <span>💳 {t("payment.creditCard") || "Credit/Debit Card"}</span>
                  </label>
                  
                  <label className={`pd-payment-option ${paymentMethod === 'ewallet' ? 'pd-payment-option--selected' : ''}`}>
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="ewallet"
                      checked={paymentMethod === 'ewallet'}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                    <span>📱 {t("payment.ewallet") || "E-Wallet"}</span>
                  </label>
                  
                  <label className={`pd-payment-option ${paymentMethod === 'bank_transfer' ? 'pd-payment-option--selected' : ''}`}>
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="bank_transfer"
                      checked={paymentMethod === 'bank_transfer'}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                    <span>🏦 {t("payment.bankTransfer") || "Bank Transfer"}</span>
                  </label>
                  
                  <label className={`pd-payment-option ${paymentMethod === 'cash' ? 'pd-payment-option--selected' : ''}`}>
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="cash"
                      checked={paymentMethod === 'cash'}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                    <span>💵 {t("payment.payAtClinic") || "Pay at Clinic"}</span>
                  </label>
                </div>
              </div>
            </div>

            <div className="pd-modal-actions">
              <button
                type="button"
                className="pd-secondary-btn"
                onClick={() => setShowPaymentModal(false)}
                disabled={paying}
              >
                {t("common.cancel") || "Cancel"}
              </button>
              <button
                type="button"
                className="pd-primary-btn"
                style={{ background: '#38b2ac', color: 'white' }}
                onClick={handlePayment}
                disabled={paying}
              >
                {paying ? (t("common.processing") || "Processing...") : (t("payment.confirmPayment") || "Confirm Payment")}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
