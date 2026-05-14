// src/api/doctorPatientAPI.js
import apiClient, { API_PREFIX } from "./authAPI";
// Get list of patients that the doctor can see
export const getDoctorPatients = async (params = {}) => {
  // params có thể có page, search,... nếu backend hỗ trợ
  const response = await apiClient.get(`${API_PREFIX}/patients/`, { params });
  return response.data; // tuỳ backend: có thể là Array hoặc {results, count,...}
};

// Get detail of a single patient
export const getDoctorPatientDetail = async (patientId) => {
  const response = await apiClient.get(`${API_PREFIX}/patients/${patientId}/`);
  return response.data;
};

// Create new patient
export const createDoctorPatient = async (payload) => {
  const response = await apiClient.post(`${API_PREFIX}/patients/`, payload);
  return response.data;
};

// Update existing patient
export const updateDoctorPatient = async (patientId, payload) => {
  const response = await apiClient.put(
    `${API_PREFIX}/patients/${patientId}/`,
    payload
  );
  return response.data;
};

// Delete patient (nếu có)
export const deleteDoctorPatient = async (patientId) => {
  const response = await apiClient.delete(
    `${API_PREFIX}/patients/${patientId}/`
  );
  return response.data;
};

// Update or add a health status note for a patient (doctor side)
export const updatePatientHealthStatus = async (patientId, payload) => {
  // Expected payload: { status: string, note?: string }
  const response = await apiClient.post(
    `${API_PREFIX}/patients/${patientId}/health-status`,
    payload
  );
  return response.data;
};
