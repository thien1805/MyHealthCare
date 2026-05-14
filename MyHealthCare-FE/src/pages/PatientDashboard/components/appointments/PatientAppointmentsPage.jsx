// src/pages/PatientDashboard/components/appointments/PatientAppointmentsPage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../../../../components/Header";
import Footer from "../../../../components/Footer";
import { useAuth } from "../../../../context/AuthContext";
import { useLanguage } from "../../../../context/LanguageContext";
import { useTranslation } from "../../../../hooks/useTranslation";
import { useToast } from "../../../../hooks/useToast";

import {
  getAvailableSlots,
  bookAppointment,
  suggestDepartmentAI,
  getDepartments,
  getDoctorsByDepartment,
} from "../../../../api/appointmentAPI";

import "../../PatientDashboard.css";
import "./BookingWizard.css";

// Fallback specialties if API fails
const FALLBACK_SPECIALTIES = [
  { id: 1, name: "General Internal Medicine", icon: "🩺" },
  { id: 2, name: "Cardiology", icon: "❤️" },
  { id: 3, name: "Dermatology", icon: "🧴" },
  { id: 4, name: "Pediatrics", icon: "🧸" },
  { id: 5, name: "Orthopedics", icon: "🦴" },
  { id: 6, name: "Ophthalmology", icon: "👁️" },
  { id: 7, name: "ENT (Ear-Nose-Throat)", icon: "👂" },
  { id: 8, name: "Dentistry", icon: "🦷" },
];

// Fallback time slots
const FALLBACK_TIME_SLOTS = [
  "08:00", "08:30", "09:00", "09:30", "10:00",
  "10:30", "11:00", "11:30", "13:30", "14:00",
  "14:30", "15:00", "15:30", "16:00", "16:30",
];

const DEFAULT_SERVICE_ID = 3;



export default function PatientAppointmentsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { t } = useTranslation();
  const { getLocalizedName } = useLanguage();
  const toast = useToast();

  const STEPS = [
    { id: "symptom", label: t("booking.symptoms") },
    { id: "specialty", label: t("booking.specialty") },
    { id: "doctor", label: t("booking.doctor") },
    { id: "time", label: t("booking.time") },
    { id: "confirm", label: t("booking.confirmStep") },
    { id: "payment", label: t("booking.payment") },
  ];

  const [stepIndex, setStepIndex] = useState(0);
  const [form, setForm] = useState({
    symptoms: "",
    departmentId: null,
    doctorId: null, // This is now user_id from API (not doctor profile id)
    date: "",
    timeSlot: "",
    extraNote: "",
    paymentMethod: "card",
  });

  // AI suggestions - multiple departments (lifted up to persist on back navigation)
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [aiResult, setAiResult] = useState(null);
  const [previousSymptoms, setPreviousSymptoms] = useState(""); // Track symptoms to detect changes

  const [departments, setDepartments] = useState([]);
  const [loadingDepartments, setLoadingDepartments] = useState(false);

  // Doctors state - fetched from API based on department
  const [doctors, setDoctors] = useState([]);
  const [loadingDoctors, setLoadingDoctors] = useState(false);

  const [timeSlots, setTimeSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [bookingLoading, setBookingLoading] = useState(false);

  const currentStep = STEPS[stepIndex];
  const selectedSpecialty = departments.find(
    (d) => d.id === form.departmentId
  );
  // doctors is now fetched from API, filtered by department_id
  const selectedDoctor = doctors.find((d) => d.user_id === form.doctorId);

  // Get patient name from user object - try multiple field names
  const getPatientName = () => {
    if (!user) return "Patient";
    // Backend uses snake_case (full_name), try different variations
    return (
      user.full_name ||      // Backend Django API (snake_case)
      user.fullName ||       // Some APIs (camelCase)
      user.name ||           // Alternative
      user.first_name ||     // Some APIs
      user.firstName ||      // camelCase alternative
      user.email?.split("@")[0] || // Fallback to email prefix
      "Patient"
    );
  };

  const patientName = getPatientName();
  const initialLetter = patientName.charAt(0).toUpperCase();

  // ===== Fetch doctors when department changes =====
  useEffect(() => {
    const fetchDoctors = async () => {
      if (!form.departmentId) {
        setDoctors([]);
        return;
      }
      
      try {
        setLoadingDoctors(true);
        const data = await getDoctorsByDepartment(form.departmentId);
        // API returns: { department: {...}, doctors: [...], count: N }
        setDoctors(data.doctors || []);
      } catch (err) {
        console.error("Error fetching doctors:", err);
        setDoctors([]);
      } finally {
        setLoadingDoctors(false);
      }
    };
    
    fetchDoctors();
  }, [form.departmentId]);

  // ===== Load available time slots từ backend khi doctor/date đổi =====
  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        setLoadingDepartments(true);
        const data = await getDepartments({ page: 1, pageSize: 50 });
        //API returns paginated: { results: [...]}
        const deptList = data.results || data || [];  
        if (deptList.length > 0){
          setDepartments(deptList);
        } else {
          setDepartments(FALLBACK_SPECIALTIES);
        }
      } catch (err) {
        console.error("Error loading departments:", err);
        setDepartments(FALLBACK_SPECIALTIES);
      } finally {
        setLoadingDepartments(false);
      }
    };

    fetchDepartments();
  }, []);


  // ===== Load available time slots =====
  useEffect(() => {
    const {doctorId, date} = form;
    if (!doctorId || !date) {
      setTimeSlots([]);
      return;
    }

    const fetchSlots = async () => {
      try {
        setLoadingSlots(true);
        const data = await getAvailableSlots({
        doctorId,
        date,
        departmentId: form.departmentId,
      });
      const available = (data.available_slots || [])
      .filter((slot) => slot.available)
      .map((slot) => slot.time);

      setTimeSlots(available.length > 0 ? available : FALLBACK_TIME_SLOTS);
    } catch (err) {
        console.error("Error loading time slots:", err);
        setTimeSlots(FALLBACK_TIME_SLOTS);
      } finally {
        setLoadingSlots(false);
      }
    };


    fetchSlots();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.doctorId, form.date, form.departmentId]);

  const canGoNext = () => {
    switch (currentStep.id) {
      case "symptom":
        return form.symptoms.trim().length > 0;
      case "specialty":
        return !!form.departmentId;
      case "doctor":
        return !!form.doctorId;
      case "time":
        return !!form.date && !!form.timeSlot;
      case "confirm":
        return true;
      case "payment":
        return !!form.paymentMethod;
      default:
        return false;
    }
  };

  const handleNext = async () => {
    if (!canGoNext()) return;

    if (stepIndex < STEPS.length - 1) {
      setStepIndex((prev) => prev + 1);
    } else {
      // ===== FINAL STEP: PAYMENT - GỌI API BOOK APPOINTMENT =====
      try {
        setBookingLoading(true);

        // Ensure time format is HH:MM:SS (backend expects this format for choices)
        const formattedTime = form.timeSlot.includes(':') && form.timeSlot.split(':').length === 2
          ? `${form.timeSlot}:00`  // Add seconds if only HH:MM
          : form.timeSlot;

        const payload = {
          doctor_id: form.doctorId,
          department_id: form.departmentId, 
          appointment_date: form.date,
          appointment_time: formattedTime, // Backend expects HH:MM:SS format
          symptoms: form.symptoms,
          reason: form.symptoms,
          notes: form.extraNote || "",
        };
        
        console.log("Booking payload:", payload);
        const res = await bookAppointment(payload);
        console.log("Book appointment response:", res);

        if (!res?.success) {
          throw new Error(res?.message || "Booking failed");
        }

        exportBookingTicket({
          patientName: patientName,
          symptoms: form.symptoms,
          specialty: selectedSpecialty?.name,
          doctor: selectedDoctor ? `${selectedDoctor.title} ${selectedDoctor.full_name}` : null,
          date: form.date,
          time: form.timeSlot,
          price: selectedSpecialty?.health_examination_fee
            ? `${Math.round(Number(selectedSpecialty.health_examination_fee)).toLocaleString("vi-VN")} VND`
            : "N/A",
        });

        toast.success(t("booking.bookingSuccess"));
        navigate("/patient/dashboard?tab=appointments");
      } catch (err) {
        console.error("Book appointment error:", err);
        toast.error(err?.message || t("booking.bookingError"));
      } finally {
        setBookingLoading(false);
      }
    }
  };

  const handleBack = () => {
    if (stepIndex === 0) return;
    setStepIndex((prev) => prev - 1);
  };

  return (
    <>
      <toast.ToastContainer />
      <Header />
      <main className="booking-page">
        <div className="booking-container">
          {/* Title */}
          <header className="booking-header">
            <h1 className="booking-title">{t("booking.title")}</h1>
            <p className="booking-subtitle">
              {t("booking.step")} {stepIndex + 1} {t("booking.of")} {STEPS.length}
            </p>
          </header>

          {/* Progress bar */}
          <div className="booking-progress-bar">
            <div
              className="booking-progress-bar-fill"
              style={{
                width: `${((stepIndex + 1) / STEPS.length) * 100}%`,
              }}
            />
          </div>

          {/* Step icons */}
          <div className="booking-steps">
            {STEPS.map((step, idx) => {
              const isActive = idx === stepIndex;
              const isDone = idx < stepIndex;
              return (
                <div key={step.id} className="booking-step-item">
                  <div
                    className={
                      "booking-step-circle" +
                      (isActive ? " booking-step-circle--active" : "") +
                      (isDone ? " booking-step-circle--done" : "")
                    }
                  >
                    {idx + 1}
                  </div>
                  <span
                    className={
                      "booking-step-label" +
                      (isActive ? " booking-step-label--active" : "")
                    }
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Step content card */}
          <section className="booking-card">
            {currentStep.id === "symptom" && (
              <StepSymptom 
                form={form} 
                setForm={setForm} 
                aiSuggestions={aiSuggestions} 
                setAiSuggestions={setAiSuggestions}
                aiResult={aiResult}
                setAiResult={setAiResult}
                previousSymptoms={previousSymptoms}
                setPreviousSymptoms={setPreviousSymptoms}
              />
            )}

            {currentStep.id === "specialty" && (
              <StepSpecialty
                form={form}
                setForm={setForm}
                departments={departments}
                loading={loadingDepartments}
              />
            )}

            {currentStep.id === "doctor" && (
              <StepDoctor
                form={form}
                setForm={setForm}
                doctors={doctors}
                loadingDoctors={loadingDoctors}
                selectedDepartment={selectedSpecialty}
              />
            )}

            {currentStep.id === "time" && (
              <StepTime
                form={form}
                setForm={setForm}
                timeSlots={timeSlots}
                loadingSlots={loadingSlots}
              />
            )}

            {currentStep.id === "confirm" && (
              <StepConfirm
                form={form}
                selectedSpecialty={selectedSpecialty}
                selectedDoctor={selectedDoctor}
                patientName={patientName}
                initialLetter={initialLetter}
              />
            )}

            {currentStep.id === "payment" && (
              <StepPayment
                form={form}
                setForm={setForm}
                selectedDoctor={selectedDoctor}
                selectedSpecialty={selectedSpecialty}
              />
            )}
          </section>

          {/* Navigation buttons */}
          <footer className="booking-footer">
            <button
              type="button"
              className="booking-btn booking-btn--ghost"
              disabled={stepIndex === 0 || bookingLoading}
              onClick={handleBack}
            >
              ← {t("common.back")}
            </button>

            <button
              type="button"
              className={
                "booking-btn booking-btn--primary" +
                (!canGoNext() || bookingLoading
                  ? " booking-btn--disabled"
                  : "")
              }
              onClick={handleNext}
              disabled={!canGoNext() || bookingLoading}
            >
              {currentStep.id === "confirm"
                ? t("booking.proceedToPayment") || "Tiến hành thanh toán →"
                : currentStep.id === "payment"
                ? bookingLoading
                  ? t("common.loading")
                  : t("payment.confirmPayment") || "Xác nhận thanh toán"
                : t("common.next") + " →"}
            </button>
          </footer>
        </div>
      </main>
      <Footer />
    </>
  );
}

/* ===== Step components ===== */

function StepSymptom({ 
  form, 
  setForm, 
  aiSuggestions, 
  setAiSuggestions,
  aiResult,
  setAiResult,
  previousSymptoms,
  setPreviousSymptoms
}) {
  const { t } = useTranslation();
  const { getLocalizedName } = useLanguage();
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Reset AI suggestions only when symptoms actually change (not on re-render)
  const handleChange = (e) => {
    const newSymptoms = e.target.value;
    setForm((prev) => ({ ...prev, symptoms: newSymptoms }));
    
    // Only reset AI suggestions if symptoms significantly changed
    if (previousSymptoms && newSymptoms.trim() !== previousSymptoms.trim()) {
      // Don't reset immediately - let user finish typing
    }
  };

  const SYMPTOM_OPTIONS = [
    { id: "fever", label: t("symptoms.fever") },
    { id: "cough", label: t("symptoms.cough") },
    { id: "headache", label: t("symptoms.headache") },
    { id: "fatigue", label: t("symptoms.fatigue") },
    { id: "chest_pain", label: t("symptoms.chestPain") },
    { id: "shortness_breath", label: t("symptoms.shortnessOfBreath") },
    { id: "nausea", label: t("symptoms.nausea") },
    { id: "dizziness", label: t("symptoms.dizziness") },
    { id: "skin_rash", label: t("symptoms.skinRash") },
    { id: "joint_pain", label: t("symptoms.jointPain") },
    { id: "sore_throat", label: t("symptoms.soreThroat") },
    { id: "stomach_ache", label: t("symptoms.stomachAche") },
  ];

  const toggleSymptom = (id) => {
    setSelectedSymptoms((prevIds) => {
      let nextIds;
      if (prevIds.includes(id)) {
        nextIds = prevIds.filter((x) => x !== id);
      } else {
        nextIds = [...prevIds, id];
      }

      // Cập nhật text symptoms từ chip
      const text = SYMPTOM_OPTIONS.filter((opt) =>
        nextIds.includes(opt.id)
      )
        .map((opt) => opt.label)
        .join(", ");

      setForm((prev) => ({
        ...prev,
        symptoms: text || prev.symptoms,
      }));

      return nextIds;
    });
  };

  const handleAISuggest = async () => {
    // Lần bấm đầu chỉ mở danh sách gợi ý
    if (!showSuggestions) {
      setShowSuggestions(true);
      return;
    }

    if (!selectedSymptoms.length && !form.symptoms.trim()) {
      alert("Vui lòng chọn hoặc nhập ít nhất một triệu chứng.");
      return;
    }

    // Check if symptoms haven't changed since last AI suggestion
    if (previousSymptoms === form.symptoms.trim() && aiResult?.success) {
      // Don't call API again if symptoms are the same
      return;
    }

    setLoading(true);
    setAiResult(null);
    setAiSuggestions([]);

    try {
      // Call AI suggest department API
      const res = await suggestDepartmentAI({
        symptoms: form.symptoms,
        // age and gender can be added if available from user profile
      });

      if (res?.success && res.primary_department) {
        // Collect all suggested departments (primary + related)
        const allSuggestions = [];
        
        // Add primary department
        allSuggestions.push({
          ...res.primary_department,
          isPrimary: true,
          reason: res.reason
        });
        
        // Add related departments if any
        if (res.related_departments && res.related_departments.length > 0) {
          res.related_departments.forEach(dept => {
            allSuggestions.push({
              ...dept,
              isPrimary: false,
              reason: dept.reason || res.reason
            });
          });
        }

        setAiSuggestions(allSuggestions);
        setPreviousSymptoms(form.symptoms.trim()); // Save symptoms for which AI was called

        setAiResult({
          success: true,
          departments: allSuggestions,
          reason: res.reason,
          urgency: res.urgency
        });
      } else {
        setAiResult({
          success: false,
          error: res?.error || "Không thể nhận được gợi ý từ AI. Vui lòng chọn thủ công."
        });
      }
    } catch (error) {
      console.error("AI suggestion error:", error);
      setAiResult({
        success: false,
        error: error?.error || "Không thể nhận được gợi ý từ AI. Vui lòng chọn thủ công."
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAISuggestion = (dept) => {
    setForm((prev) => ({
      ...prev,
      departmentId: dept.id,
      doctorId: null,
      timeSlot: "",
    }));
  };

  return (
    <>
      <h2 className="booking-section-title">🩺 {t("booking.describeSymptoms")}</h2>
      <p className="booking-section-subtitle">
        {t("booking.symptomsSubtitle")}
      </p>

      <label className="booking-field-label">{t("booking.yourSymptoms")}</label>
      <textarea
        className="booking-textarea"
        rows={4}
        placeholder={t("booking.symptomsPlaceholder")}
        value={form.symptoms}
        onChange={handleChange}
      />

      <button
        type="button"
        className="booking-btn booking-btn--ai"
        onClick={handleAISuggest}
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="booking-btn-spinner">🔄</span>
            {t("booking.analyzing")}
          </>
        ) : (
          <>
            <span>🤖</span>
            {t("booking.getAISuggestion")}
          </>
        )}
      </button>

      {/* AI Result Card - Multiple Suggestions */}
      {aiResult && aiResult.success && aiResult.departments && (
        <div className="ai-result-card">
          <div className="ai-result-header">
            <span className="ai-result-icon">✨</span>
            <h3>{t("booking.aiSuggestion")}</h3>
          </div>
          
          <div className="ai-result-body">
            <p className="ai-result-intro">
              {t("booking.aiMultipleSuggestions") || "Dựa vào triệu chứng của bạn, AI đề xuất các chuyên khoa sau:"}
            </p>

            <div className="ai-suggestions-list">
              {aiResult.departments.map((dept, index) => (
                <div 
                  key={dept.id || index}
                  className={`ai-suggestion-card ${form.departmentId === dept.id ? 'ai-suggestion-card--selected' : ''} ${dept.isPrimary ? 'ai-suggestion-card--primary' : ''}`}
                  onClick={() => handleSelectAISuggestion(dept)}
                >
                  <div className="ai-suggestion-card-header">
                    <span className="ai-suggestion-dept-icon">{dept.icon || "🏥"}</span>
                    <div className="ai-suggestion-dept-info">
                      <h4>{getLocalizedName(dept)}</h4>
                      {dept.isPrimary && (
                        <span className="ai-primary-badge">{t("booking.recommended") || "Đề xuất hàng đầu"}</span>
                      )}
                    </div>
                    <div className="ai-suggestion-check">
                      {form.departmentId === dept.id ? '✓' : ''}
                    </div>
                  </div>
                  {dept.reason && (
                    <p className="ai-suggestion-reason">{dept.reason}</p>
                  )}
                </div>
              ))}
            </div>

            {aiResult.urgency && (
              <div className={`ai-urgency-indicator ai-urgency-${aiResult.urgency}`}>
                <span className="ai-urgency-icon">
                  {aiResult.urgency === 'high' ? '⚠️' : aiResult.urgency === 'medium' ? '⚡' : 'ℹ️'}
                </span>
                <span className="ai-urgency-text">
                  {t("booking.urgency")}: {aiResult.urgency === 'high' ? t("booking.urgencyHigh") : aiResult.urgency === 'medium' ? t("booking.urgencyMedium") : t("booking.urgencyLow")}
                </span>
              </div>
            )}
            
            <p className="ai-suggestion-hint">
              {t("booking.clickToSelectDepartment") || "👆 Nhấn vào chuyên khoa để chọn"}
            </p>
          </div>
        </div>
      )}

      {aiResult && !aiResult.success && (
        <div className="ai-result-card ai-result-card--error">
          <div className="ai-result-header">
            <span className="ai-result-icon">⚠️</span>
            <h3>Không thể nhận gợi ý</h3>
          </div>
          <div className="ai-result-body">
            <p>{aiResult.error}</p>
          </div>
        </div>
      )}
    </>
  );
}

function StepSpecialty({ form, setForm, departments, loading }) {
  const { t } = useTranslation();
  const { getLocalizedName } = useLanguage();

  if (loading) {
    return (
      <div className="booking-loading">
        <p>{t("common.loading")}</p>
      </div>
    );
  }

  return (
    <>
      <h2 className="booking-section-title">{t("booking.chooseSpecialty")}</h2>
      <p className="booking-section-subtitle">
        {t("booking.chooseSpecialtySubtitle")}
      </p>

      <div className="booking-specialty-grid">
        {departments.map((dept) => {
          const isActive = form.departmentId === dept.id;
          // Use icon from API or fallback emoji
          const emoji = dept.icon || "🏥";
          return (
            <button
              key={dept.id}
              type="button"
              className={
                "booking-specialty-card" +
                (isActive ? " booking-specialty-card--active" : "")
              }
              onClick={() =>
                setForm((prev) => ({
                  ...prev,
                  departmentId: dept.id,
                  doctorId: null, // reset doctor when changing department
                  timeSlot: "",
                }))
              }
            >
              <div className="booking-specialty-emoji">{emoji}</div>
              <div className="booking-specialty-name">{getLocalizedName(dept)}</div>
              {dept.health_examination_fee && (
                <div className="booking-specialty-fee">
                  {dept.health_examination_fee.toLocaleString("vi-VN")} VND
                </div>
              )}
            </button>
          );
        })}
      </div>
    </>
  );
}

function StepDoctor({ form, setForm, doctors, loadingDoctors, selectedDepartment }) {
  const { t } = useTranslation();
  const { getLocalizedName } = useLanguage();

  const getInitials = (name = "") => {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    if (parts.length === 0) return "?";
    // Prefer first letter of given name (last word), fallback to first word
    const last = parts[parts.length - 1].charAt(0).toUpperCase();
    const first = parts[0].charAt(0).toUpperCase();
    return last || first || "?";
  };

  return (
    <>
      <h2 className="booking-section-title">{t("booking.chooseDoctor")}</h2>
      <p className="booking-section-subtitle">
        {selectedDepartment
          ? `${t("booking.specialty")}: ${getLocalizedName(selectedDepartment)}`
          : t("booking.chooseDepartmentFirst")}
      </p>

      {loadingDoctors ? (
        <div className="booking-loading">{t("common.loading") || "Loading..."}</div>
      ) : (
        <div className="booking-doctor-list">
          {doctors.map((doc) => {
            // Use user_id for booking (not doc.id which is Doctor profile id)
            const isActive = form.doctorId === doc.user_id;
            const hasAvatar = Boolean(doc.avatar_url);
            return (
              <button
                key={doc.id}
                type="button"
                className={
                  "booking-doctor-card" +
                  (isActive ? " booking-doctor-card--active" : "")
                }
                onClick={() =>
                  setForm((prev) => ({
                    ...prev,
                    doctorId: doc.user_id, // IMPORTANT: use user_id for API booking
                    timeSlot: "",
                  }))
                }
              >
                <div className="booking-doctor-avatar" data-fallback={hasAvatar ? "0" : "1"}>
                  {hasAvatar && (
                    <img
                      src={doc.avatar_url}
                      alt={doc.full_name || "Doctor avatar"}
                      onError={(e) => {
                        const parent = e.target?.parentElement;
                        if (parent) {
                          parent.setAttribute("data-fallback", "1");
                        }
                        e.target.style.display = "none";
                      }}
                      loading="lazy"
                    />
                  )}
                  <span className="booking-doctor-avatar-fallback">{getInitials(doc.full_name)}</span>
                </div>
                <div className="booking-doctor-info">
                  <div className="booking-doctor-name">{doc.title} {doc.full_name}</div>
                  <div className="booking-doctor-exp">
                    {t("booking.experience")}: {doc.experience_years} {t("booking.years") || "years"}
                  </div>
                  <div className="booking-doctor-meta">
                    ⭐ {Number(doc.rating).toFixed(1)} • {doc.experience_years} {t("booking.yearsExp") || "năm KN"}
                  </div>
                </div>
              </button>
            );
          })}

          {doctors.length === 0 && (
            <div className="booking-empty">
              {selectedDepartment 
                ? (t("booking.noDoctorsAvailable") || "Không có bác sĩ nào trong chuyên khoa này.")
                : t("booking.chooseDepartmentFirst")
              }
            </div>
          )}
        </div>
      )}
    </>
  );
}

function StepTime({ form, setForm, timeSlots, loadingSlots }) {
  const { t } = useTranslation();
  const hasDoctorAndDate = form.doctorId && form.date;
  
  // Calendar state
  const today = new Date();
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  
  const monthNames = [
    t("calendar.january") || "January", t("calendar.february") || "February", 
    t("calendar.march") || "March", t("calendar.april") || "April",
    t("calendar.may") || "May", t("calendar.june") || "June",
    t("calendar.july") || "July", t("calendar.august") || "August",
    t("calendar.september") || "September", t("calendar.october") || "October",
    t("calendar.november") || "November", t("calendar.december") || "December"
  ];
  
  const dayNames = [
    t("calendar.sun") || "Sun", t("calendar.mon") || "Mon", 
    t("calendar.tue") || "Tue", t("calendar.wed") || "Wed",
    t("calendar.thu") || "Thu", t("calendar.fri") || "Fri", 
    t("calendar.sat") || "Sat"
  ];
  
  // Get days in month
  const getDaysInMonth = (month, year) => {
    return new Date(year, month + 1, 0).getDate();
  };
  
  // Get first day of month (0 = Sunday)
  const getFirstDayOfMonth = (month, year) => {
    return new Date(year, month, 1).getDay();
  };
  
  const daysInMonth = getDaysInMonth(currentMonth, currentYear);
  const firstDayOfMonth = getFirstDayOfMonth(currentMonth, currentYear);
  
  const handlePrevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };
  
  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };
  
  const handleSelectDate = (day) => {
    const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    setForm((prev) => ({
      ...prev,
      date: dateStr,
      timeSlot: "",
    }));
  };
  
  const isDateSelected = (day) => {
    const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return form.date === dateStr;
  };
  
  const isDateDisabled = (day) => {
    const date = new Date(currentYear, currentMonth, day);
    const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    return date < todayStart;
  };
  
  const isToday = (day) => {
    return day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear();
  };
  
  // Generate calendar days
  const calendarDays = [];
  // Empty cells for days before the first day
  for (let i = 0; i < firstDayOfMonth; i++) {
    calendarDays.push(<div key={`empty-${i}`} className="calendar-day calendar-day--empty"></div>);
  }
  // Actual days
  for (let day = 1; day <= daysInMonth; day++) {
    const disabled = isDateDisabled(day);
    const selected = isDateSelected(day);
    const todayClass = isToday(day) ? ' calendar-day--today' : '';
    
    calendarDays.push(
      <button
        key={day}
        type="button"
        disabled={disabled}
        className={`calendar-day${selected ? ' calendar-day--selected' : ''}${disabled ? ' calendar-day--disabled' : ''}${todayClass}`}
        onClick={() => !disabled && handleSelectDate(day)}
      >
        {day}
      </button>
    );
  }

  return (
    <>
      <h2 className="booking-section-title">{t("booking.chooseTime")}</h2>
      <p className="booking-section-subtitle">
        {t("booking.chooseTimeSubtitle")}
      </p>

      <div className="booking-time-layout">
        {/* Custom Calendar Picker */}
        <div className="booking-calendar-container">
          <label className="booking-field-label">{t("booking.appointmentDate")}</label>
          
          <div className="custom-calendar">
            <div className="calendar-header">
              <button type="button" className="calendar-nav-btn" onClick={handlePrevMonth}>
                ‹
              </button>
              <span className="calendar-month-year">
                {monthNames[currentMonth]} {currentYear}
              </span>
              <button type="button" className="calendar-nav-btn" onClick={handleNextMonth}>
                ›
              </button>
            </div>
            
            <div className="calendar-weekdays">
              {dayNames.map((day, i) => (
                <div key={i} className="calendar-weekday">{day}</div>
              ))}
            </div>
            
            <div className="calendar-days">
              {calendarDays}
            </div>
          </div>
          
          {form.date && (
            <div className="selected-date-display">
              {t("booking.selectedDate") || "Ngày đã chọn"}: <strong>{form.date}</strong>
            </div>
          )}
        </div>

        {/* Time Slots */}
        <div className="booking-time-slots">
          <label className="booking-field-label">{t("booking.timeSlot")}</label>

          {loadingSlots ? (
            <div className="booking-empty">{t("booking.loadingSlots")}</div>
          ) : !hasDoctorAndDate ? (
            <div className="booking-empty">
              {t("booking.selectDoctorFirst")}
            </div>
          ) : timeSlots.length === 0 ? (
            <div className="booking-empty">
              {t("booking.noSlotsAvailable")}
            </div>
          ) : (
            <div className="booking-time-grid">
              {timeSlots.map((slot) => (
                <button
                  key={slot}
                  type="button"
                  className={
                    "booking-time-slot" +
                    (form.timeSlot === slot
                      ? " booking-time-slot--active"
                      : "")
                  }
                  onClick={() =>
                    setForm((prev) => ({ ...prev, timeSlot: slot }))
                  }
                >
                  {slot}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <label className="booking-field-label">{t("booking.additionalNotes")}</label>
      <textarea
        className="booking-textarea"
        rows={3}
        placeholder={t("booking.notesPlaceholder")}
        value={form.extraNote}
        onChange={(e) =>
          setForm((prev) => ({ ...prev, extraNote: e.target.value }))
        }
      />
    </>
  );
}

function StepConfirm({
  form,
  selectedSpecialty,
  selectedDoctor,
  patientName,
  initialLetter,
}) {
  const { t } = useTranslation();

  return (
    <>
      <h2 className="booking-section-title">{t("booking.reviewDetails")}</h2>
      <p className="booking-section-subtitle">
        {t("booking.reviewSubtitle")}
      </p>

      <div className="booking-confirm-card">
        <div className="booking-confirm-row">
          <span className="booking-confirm-label">{t("common.patient")}:</span>
          <span className="booking-confirm-value">
            <span className="booking-confirm-avatar">{initialLetter}</span>
            {patientName}
          </span>
        </div>

        <div className="booking-confirm-row">
          <span className="booking-confirm-label">{t("booking.symptoms")}:</span>
          <span className="booking-confirm-value">
            {form.symptoms || t("patient.notProvided")}
          </span>
        </div>

        <div className="booking-confirm-row">
          <span className="booking-confirm-label">{t("booking.specialty")}:</span>
          <span className="booking-confirm-value">
            {selectedSpecialty?.name || t("patient.notProvided")}
          </span>
        </div>

        <div className="booking-confirm-row">
          <span className="booking-confirm-label">{t("booking.doctor")}:</span>
          <span className="booking-confirm-value">
            {selectedDoctor ? `${selectedDoctor.title} ${selectedDoctor.full_name}` : t("patient.notProvided")}
          </span>
        </div>

        <div className="booking-confirm-row">
          <span className="booking-confirm-label">{t("patient.date")}:</span>
          <span className="booking-confirm-value">
            {form.date || t("patient.notProvided")}
          </span>
        </div>

        <div className="booking-confirm-row">
          <span className="booking-confirm-label">{t("patient.time")}:</span>
          <span className="booking-confirm-value">
            {form.timeSlot || t("patient.notProvided")}
          </span>
        </div>

        <div className="booking-confirm-row booking-confirm-row--price">
          <span className="booking-confirm-label">{t("booking.consultationFee")}:</span>
          <span className="booking-confirm-price">
            {selectedSpecialty?.health_examination_fee
              ? `${Math.round(Number(selectedSpecialty.health_examination_fee)).toLocaleString("vi-VN")} VND`
              : "N/A"}
          </span>
        </div>

        <div className="booking-confirm-note">
          <em>{t("booking.confirmInfoNote") || "Vui lòng kiểm tra thông tin trước khi tiến hành thanh toán."}</em>
        </div>
      </div>
    </>
  );
}

// ===== STEP PAYMENT =====
function StepPayment({ form, setForm, selectedDoctor, selectedSpecialty }) {
  const { t } = useTranslation();
  const [cardNumber, setCardNumber] = useState('');
  const [cardName, setCardName] = useState('');
  const [expiry, setExpiry] = useState('');
  const [cvv, setCvv] = useState('');

  const paymentMethods = [
    { id: 'card', icon: '💳', label: t("payment.creditCard") || "Thẻ tín dụng/Ghi nợ" },
    { id: 'ewallet', icon: '📱', label: t("payment.ewallet") || "Ví điện tử" },
    { id: 'bank', icon: '🏦', label: t("payment.bankTransfer") || "Chuyển khoản ngân hàng" },
    { id: 'clinic', icon: '🏥', label: t("payment.payAtClinic") || "Thanh toán tại phòng khám" },
  ];

  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = (matches && matches[0]) || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    return parts.length ? parts.join(' ') : value;
  };

  const formatExpiry = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4);
    }
    return v;
  };

  return (
    <>
      <h2 className="booking-section-title">💳 {t("payment.title") || "Thanh toán"}</h2>
      <p className="booking-section-subtitle">
        {t("payment.subtitle") || "Chọn phương thức thanh toán và hoàn tất đặt lịch"}
      </p>

      <div className="payment-layout">
        {/* Payment Methods */}
        <div className="payment-methods-section">
          <label className="booking-field-label">{t("payment.selectMethod") || "Chọn phương thức thanh toán"}</label>
          
          <div className="payment-methods-grid">
            {paymentMethods.map((method) => (
              <button
                key={method.id}
                type="button"
                className={`payment-method-card ${form.paymentMethod === method.id ? 'payment-method-card--active' : ''}`}
                onClick={() => setForm(prev => ({ ...prev, paymentMethod: method.id }))}
              >
                <span className="payment-method-icon">{method.icon}</span>
                <span className="payment-method-label">{method.label}</span>
                {form.paymentMethod === method.id && (
                  <span className="payment-method-check">✓</span>
                )}
              </button>
            ))}
          </div>

          {/* Card Form - Only show when card is selected */}
          {form.paymentMethod === 'card' && (
            <div className="payment-card-form">
              <div className="payment-form-group">
                <label>{t("payment.cardNumber") || "Số thẻ"}</label>
                <input
                  type="text"
                  placeholder="0000 0000 0000 0000"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                  maxLength={19}
                  className="payment-input"
                />
              </div>
              
              <div className="payment-form-group">
                <label>{t("payment.cardName") || "Tên chủ thẻ"}</label>
                <input
                  type="text"
                  placeholder="NGUYEN VAN A"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value.toUpperCase())}
                  className="payment-input"
                />
              </div>
              
              <div className="payment-form-row">
                <div className="payment-form-group payment-form-group--half">
                  <label>{t("payment.expiry") || "Ngày hết hạn"}</label>
                  <input
                    type="text"
                    placeholder="MM/YY"
                    value={expiry}
                    onChange={(e) => setExpiry(formatExpiry(e.target.value))}
                    maxLength={5}
                    className="payment-input"
                  />
                </div>
                
                <div className="payment-form-group payment-form-group--half">
                  <label>{t("payment.cvv") || "CVV"}</label>
                  <input
                    type="password"
                    placeholder="***"
                    value={cvv}
                    onChange={(e) => setCvv(e.target.value.replace(/\D/g, '').substring(0, 3))}
                    maxLength={3}
                    className="payment-input"
                  />
                </div>
              </div>
            </div>
          )}

          {/* E-wallet options */}
          {form.paymentMethod === 'ewallet' && (
            <div className="payment-ewallet-options">
              <p className="payment-info-text">{t("payment.ewalletInfo") || "Chọn ví điện tử:"}</p>
              <div className="ewallet-buttons">
                <button type="button" className="ewallet-btn">MoMo</button>
                <button type="button" className="ewallet-btn">ZaloPay</button>
                <button type="button" className="ewallet-btn">VNPay</button>
              </div>
            </div>
          )}

          {/* Bank transfer info */}
          {form.paymentMethod === 'bank' && (
            <div className="payment-bank-info">
              <p className="payment-info-text">{t("payment.bankInfo") || "Thông tin chuyển khoản:"}</p>
              <div className="bank-details">
                <p><strong>{t("payment.bankName") || "Ngân hàng"}:</strong> Vietcombank</p>
                <p><strong>{t("payment.accountNumber") || "Số tài khoản"}:</strong> 1234567890</p>
                <p><strong>{t("payment.accountName") || "Tên tài khoản"}:</strong> PHONG KHAM MY HEALTHCARE</p>
                <p><strong>{t("payment.content") || "Nội dung"}:</strong> [Họ tên] - Đặt khám</p>
              </div>
            </div>
          )}

          {/* Pay at clinic info */}
          {form.paymentMethod === 'clinic' && (
            <div className="payment-clinic-info">
              <p className="payment-info-text">
                {t("payment.clinicInfo") || "Bạn sẽ thanh toán trực tiếp tại phòng khám khi đến khám."}
              </p>
              <div className="clinic-note">
                <span>💡</span>
                <p>{t("payment.clinicNote") || "Vui lòng đến trước giờ hẹn 15 phút để làm thủ tục thanh toán."}</p>
              </div>
            </div>
          )}
        </div>

        {/* Order Summary */}
        <div className="payment-summary-section">
          <div className="payment-summary-card">
            <h3 className="payment-summary-title">{t("payment.orderSummary") || "Chi tiết đặt lịch"}</h3>
            
            <div className="payment-summary-row">
              <span>{t("booking.specialty")}:</span>
              <span>{selectedSpecialty?.name || '-'}</span>
            </div>
            
            <div className="payment-summary-row">
              <span>{t("booking.doctor")}:</span>
              <span>{selectedDoctor ? `${selectedDoctor.title} ${selectedDoctor.full_name}` : '-'}</span>
            </div>
            
            <div className="payment-summary-row">
              <span>{t("patient.date")}:</span>
              <span>{form.date || '-'}</span>
            </div>
            
            <div className="payment-summary-row">
              <span>{t("patient.time")}:</span>
              <span>{form.timeSlot || '-'}</span>
            </div>
            
            <div className="payment-summary-divider"></div>
            
            <div className="payment-summary-row">
              <span>{t("payment.consultationFee") || "Phí khám"}:</span>
              <span>{selectedSpecialty?.health_examination_fee ? `${Math.round(Number(selectedSpecialty.health_examination_fee)).toLocaleString("vi-VN")} VND` : '-'}</span>
            </div>
            
            <div className="payment-summary-row payment-summary-row--total">
              <span>{t("payment.total") || "Tổng cộng"}:</span>
              <span className="payment-total-amount">
                {selectedSpecialty?.health_examination_fee ? `${Math.round(Number(selectedSpecialty.health_examination_fee)).toLocaleString("vi-VN")} VND` : '-'}
              </span>
            </div>
          </div>

          <div className="payment-secure-badge">
            🔒 {t("payment.securePayment") || "Thanh toán an toàn & bảo mật"}
          </div>
        </div>
      </div>
    </>
  );
}

function exportBookingTicket({
  patientName,
  symptoms,
  specialty,
  doctor,
  date,
  time,
  price,
}) {
  const note =
    "Please bring this booking ticket when going to the appointment.";
  const html = `
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Booking Ticket</title>
    <style>
      body { font-family: Arial, sans-serif; padding: 24px; color: #0f172a; }
      .card { border: 1px solid #dbeafe; border-radius: 12px; padding: 20px; background: #f8fbff; max-width: 600px; margin: 0 auto; }
      .title { font-size: 20px; font-weight: 700; margin-bottom: 12px; color: #0f172a; text-align: center; }
      .row { display: flex; justify-content: space-between; margin-bottom: 8px; }
      .label { color: #475569; font-weight: 600; }
      .value { color: #0f172a; font-weight: 600; }
      .price { color: #059669; font-weight: 700; }
      .note { margin-top: 16px; padding: 10px 12px; background: #fff7e6; border: 1px solid #facc15; border-radius: 8px; color: #b45309; font-weight: 600; font-style: italic; }
    </style>
  </head>
  <body>
    <div class="card">
      <div class="title">Appointment Booking Ticket</div>
      <div class="row"><span class="label">Patient:</span><span class="value">${patientName || "-"}</span></div>
      <div class="row"><span class="label">Symptoms:</span><span class="value">${symptoms || "Not provided"}</span></div>
      <div class="row"><span class="label">Specialty:</span><span class="value">${specialty || "N/A"}</span></div>
      <div class="row"><span class="label">Doctor:</span><span class="value">${doctor || "N/A"}</span></div>
      <div class="row"><span class="label">Date:</span><span class="value">${date || "N/A"}</span></div>
      <div class="row"><span class="label">Time:</span><span class="value">${time || "N/A"}</span></div>
      <div class="row"><span class="label">Consultation fee:</span><span class="price">${price || "N/A"}</span></div>
      <div class="note">${note}</div>
    </div>
  </body>
</html>
`;

  // Prefer direct download via Blob (avoids popup blockers)
  try {
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "booking-ticket.html";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (e) {
    console.error("Download booking ticket failed, fallback to print:", e);
    const newWin = window.open("", "_blank");
    if (!newWin) {
      alert("Please allow popups to download your booking ticket.");
      return;
    }
    newWin.document.write(html);
    newWin.document.close();
    newWin.focus();
    newWin.print();
    newWin.close();
  }
}
