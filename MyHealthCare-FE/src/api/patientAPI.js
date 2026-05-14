// src/api/patientAPI.js
import apiClient, { API_PREFIX } from "./authAPI"; 
export async function getMyProfile() {
  const res = await apiClient.get("/api/v1/user/me"); 
  return res.data;
}

export async function getMyAppointments(params = {}) {
  const tryPaths = [
    `${API_PREFIX}/appointments/my-appointments`,
    `${API_PREFIX}/appointments/`,
  ];

  for (const path of tryPaths) {
    try {
      const res = await apiClient.get(path, { params });
      return res.data;
    } catch (err) {
      const status = err?.response?.status;
      if (status !== 404 && status !== 401 && status !== 403) {
        throw err;
      }
    }
  }

  return [];
}

