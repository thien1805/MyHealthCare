// src/api/authAPI.js
import axios from "axios";

export const API_PREFIX = "/api/v1";
const DEFAULT_API_BASE_URL = "https://myhealthcare-api-h3amhrevg2feeab9.southeastasia-01.azurewebsites.net";
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL).replace(/\/+$/, "");

function buildApiUrl(path = "") {
  const normalizedPath = path ? (path.startsWith("/") ? path : `/${path}`) : "";
  if (normalizedPath.startsWith(API_PREFIX)) {
    return `${API_BASE_URL}${normalizedPath}`;
  }
  return `${API_BASE_URL}${API_PREFIX}${normalizedPath}`;
}

export const ADMIN_PANEL_URL = buildApiUrl("/admin/");

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const access = localStorage.getItem("access_token");
  if (access) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});
// ---- Helpers ----
function saveAuthToStorage({ user, tokens }) {
  if (tokens?.access) {
    localStorage.setItem("access_token", tokens.access);
  }
  if (tokens?.refresh) {
    localStorage.setItem("refresh_token", tokens.refresh);
  }
  if (user) {
    localStorage.setItem("user", JSON.stringify(user));
  }
}

let refreshPromise = null;

async function refreshAccessToken() {
  console.log("Refreshing access token...");
  const refresh = localStorage.getItem("refresh_token");
  console.log("Refresh token:", refresh ? "Exists" : "Not found");
  if (!refresh) throw new Error("No refresh token");

  const res = await fetch(buildApiUrl("/token/refresh/"), {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ refresh }),
    });
    console.log("Refresh response status:", res.status);
    const data = await res.json().catch(() => null); // tránh lỗi JSON parse nếu response không phải JSON
    
    if (!res.ok || !data?.access) {
      throw new Error("Failed to refresh access token");
    }
    localStorage.setItem("access_token", data.access);
    return data;
  }

//Axios respone interceptor to handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status;
    const originalRequest = error.config || {};

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        if (!refreshPromise){
          refreshPromise = refreshAccessToken().finally(() => {
            refreshPromise = null;
          });
        } 
        const tokens = await refreshPromise;
        originalRequest.headers.Authorization = `Bearer ${tokens.access}`;
        return apiClient(originalRequest);
      } catch (refreshErr){
        // Refresh token failed, logout user
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
        window.location.href = "/login";
        return Promise.reject(refreshErr);
      }
    }
    return Promise.reject(error?.response?.data || error?.message || error);
  }
);

export function getCurrrentUser() {
  // 👈 tên hàm này cố tình sai chính tả để khớp import của bạn
  const raw = localStorage.getItem("user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  const access = localStorage.getItem("access_token");
  return !!access;
}

// ---- LOGIN ----
export async function login({ email, password }) {
  const res = await fetch(buildApiUrl("/auth/login/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok || !data?.success) {
    // backend trả: { success: False, message: "Invalid email or password" }
    const message = data?.message || "Login failed";
    throw new Error(message);
  }

  // data = { success, message, user, tokens: { refresh, access } }
  saveAuthToStorage({ user: data.user, tokens: data.tokens });

  return data; // cho AuthContext dùng
}

// ---- LOGOUT ----
export async function logout() {
  const refresh = localStorage.getItem("refresh_token");

  try {
    if (refresh) {
      await fetch(buildApiUrl("/auth/logout/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
        },
        body: JSON.stringify({ refresh }),
      });
    }
  } catch (err) {
    console.error("Logout API error:", err);
    // vẫn clear localStorage dù API fail
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    window.location.href = "/home";
  }
}

// ---- REGISTER ----
export async function register(payload) {
  const res = await fetch(buildApiUrl("/auth/register/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok || !data?.success) {
    // Ném nguyên payload lỗi để UI hiển thị đúng từng field
    throw data || { message: "Registration failed" };
  }

  // Lưu token + user xuống localStorage để auto đăng nhập sau đăng ký
  saveAuthToStorage({ user: data.user, tokens: data.tokens });
  return data;
}

// ---- FORGOT PASSWORD (request email) ----
export async function requestPasswordReset({ email }) {
  const res = await fetch(buildApiUrl("/auth/forgot-password/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok || !data?.success) {
    const msg = data?.message || data?.detail || "Failed to send password reset email";
    throw new Error(msg);
  }

  return data;
}

// ---- VERIFY RESET TOKEN (optional) ----
export async function verifyResetToken({ uid, token }) {
  const res = await fetch(buildApiUrl("/auth/verify-reset-token/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ uid, token }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok || !data?.success) {
    const msg = data?.message || data?.detail || "Token is invalid or has expired";
    throw new Error(msg);
  }

  return data;
}

// ---- RESET PASSWORD ----
export async function resetPassword({ uid, token, newPassword, confirmPassword }) {
  const res = await fetch(buildApiUrl("/auth/reset-password/"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      uid,
      token,
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok || !data?.success) {
    const msg = data?.message || data?.detail || "Reset password failed";
    throw new Error(msg);
  }

  return data;
}

// ---- GET PROFILE ----
export async function getProfile() {
  const access = localStorage.getItem("access_token");
  if (!access) throw new Error("No access token");

  const res = await fetch(buildApiUrl("/user/me/"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${access}`,
      "Content-Type": "application/json",
    },
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.detail || data?.message || "Failed to fetch profile";
    throw new Error(msg);
  }

  // Lưu user profile vào localStorage
  localStorage.setItem("user", JSON.stringify(data));
  return data;
}

// ---- UPDATE PROFILE (PATCH) ----
export async function updateProfile(profilePayload) {
  const access = localStorage.getItem("access_token");
  if (!access) throw new Error("No access token");

  const res = await fetch(buildApiUrl("/user/me/"), {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${access}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(profilePayload),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    // lỗi validate sẽ trả { field: ["msg"] }
    throw data || { message: "Failed to update profile" };
  }

  // Backend đã trả lại User đầy đủ sau khi update
  localStorage.setItem("user", JSON.stringify(data));
  return data;
}

// ---- GET ME (CURRENT USER INFO) ----
export async function getMe() {
  const access = localStorage.getItem("access_token");
  if (!access) throw new Error("No access token");

  const res = await fetch(buildApiUrl("/user/me/"), {
    method: "GET",
    headers: {
      Authorization: `Bearer ${access}`,
      "Content-Type": "application/json",
    },
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.detail || data?.message || "Failed to fetch user info";
    throw new Error(msg);
  }

  // Lưu user info vào localStorage
  localStorage.setItem("user", JSON.stringify(data));
  return data;
}

export default apiClient;
