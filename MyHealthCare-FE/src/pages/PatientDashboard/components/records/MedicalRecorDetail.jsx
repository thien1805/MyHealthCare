// src/pages/PatientDashboard/components/records/MedicalRecorDetail.jsx
import React, { useEffect, useState } from "react";
import { getMedicalRecordDetail } from "../../../../api/medicalRecordAPI";

/**
 * 📌 GHI CHÚ VỀ API:
 *
 * 1. Hàm getMedicalRecordDetail(recordId)
 *    - FE đang giả định trong medicalRecordAPI.js có:
 *        GET /api/v1/medical-records/{id}/
 *    - Nếu backend CHƯA có endpoint detail này, thì đây là API CÒN THIẾU.
 *
 * 2. Trường doctorNotificationNote
 *    - FE đang giả định backend trả về 1 trong 2 field trong record detail:
 *        - doctor_notification_note
 *        - latest_notification: { message: "..." }
 *    - Nếu backend CHƯA embed thông tin notification vào medical record,
 *      thì phần "Doctor's notification" sẽ luôn rỗng (API CÒN THIẾU PHẦN NÀY).
 */

export default function MedicalRecorDetail({ record, recordId }) {
  const [data, setData] = useState(record || null);
  const [loading, setLoading] = useState(!record && !!recordId);
  const [error, setError] = useState(null);

  // Gọi API nếu không có record mà chỉ có recordId
  useEffect(() => {
    if (record || !recordId) return;

    let cancelled = false;

    const fetchRecord = async () => {
      try {
        setLoading(true);
        setError(null);

        // 🔔 Phụ thuộc API detail: GET /api/v1/medical-records/{id}/
        const res = await getMedicalRecordDetail(recordId);

        if (!cancelled) {
          setData(res);
        }
      } catch (err) {
        if (!cancelled) {
          console.error("Load medical record detail error:", err);
          setError(
            typeof err === "string"
              ? err
              : err?.message || "Failed to load medical record."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchRecord();

    return () => {
      cancelled = true;
    };
  }, [record, recordId]);

  // Không dùng data fake kiểu "John Smith" nữa, chỉ để fallback text
  const display = {
    id: data?.id ?? "",
    date: data?.visit_date || data?.date || "Not provided",
    doctorName:
      data?.doctor_name ||
      data?.doctor?.full_name ||
      data?.doctor?.name ||
      "Not provided",
    type: data?.visit_type || data?.type || "Not provided",
    summary:
      data?.summary ||
      data?.diagnosis_summary ||
      data?.chief_complaint ||
      "Not provided",
    notes:
      data?.notes ||
      data?.clinical_notes ||
      data?.extra_notes ||
      "Not provided",
    // NOTE (API): cần backend trả về 1 trong 2:
    //  - doctor_notification_note
    //  - latest_notification: { message: "..." }
    doctorNotificationNote:
      data?.doctor_notification_note ||
      data?.latest_notification?.message ||
      "",
  };

  if (loading) {
    return (
      <div className="pd-card" style={{ marginTop: "16px" }}>
        <h3 className="pd-section-title">Record details</h3>
        <p className="pd-section-subtitle">Loading medical record...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pd-card" style={{ marginTop: "16px" }}>
        <h3 className="pd-section-title">Record details</h3>
        <p className="pd-section-subtitle" style={{ color: "red" }}>
          {error}
        </p>
      </div>
    );
  }

  return (
    <div className="pd-card" style={{ marginTop: "16px" }}>
      <h3 className="pd-section-title">Record details</h3>
      <p className="pd-section-subtitle">
        Visit date: {display.date} — {display.type}
      </p>

      <div className="pd-record-detail">
        <p>
          <strong>Doctor:</strong> {display.doctorName}
        </p>
        <p>
          <strong>Summary:</strong> {display.summary}
        </p>
        <p>
          <strong>Notes:</strong> {display.notes}
        </p>

        {display.doctorNotificationNote && (
          <p>
            <strong>Doctor&apos;s notification:</strong>{" "}
            {display.doctorNotificationNote}
          </p>
        )}
      </div>
    </div>
  );
}
