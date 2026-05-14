import React, { createContext, useContext, useState, useEffect } from "react";
import {
  login as loginAPI,
  logout as logoutAPI,
  getCurrrentUser as getCurrentUser, 
  isAuthenticated,
} from "../api/authAPI";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuth, setIsAuth] = useState(false);
  const [loading, setLoading] = useState(true);

  // ---- helper: sync state từ storage / authAPI (có refresh token) ----
  const loadUser = async () => {
    try {
      setLoading(true);
      const savedUser = getCurrentUser();
      const authenticated = isAuthenticated();

      if (savedUser && authenticated) {
        setUser(savedUser);
        setIsAuth(true);
      } else {
        setUser(null);
        setIsAuth(false);
      }
    } catch (error) {
      console.error("Error loading user:", error);
      setUser(null);
      setIsAuth(false);
    } finally {
      setLoading(false);
    }
  };

  // ---- init + lắng nghe thay đổi localStorage ----
  useEffect(() => {
    loadUser();

    const handleStorageChange = (e) => {
      if (
        e.key === "user" ||
        e.key === "access_token" ||
        e.key === "refresh_token"
      ) {
        loadUser();
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);



  // ---- LOGIN ----
  const login = async (credentials) => {
    try {
      setLoading(true);

      const data = await loginAPI(credentials);

      if (data && (data.success === true || data.tokens || data.user)) {
        // ưu tiên user trả về từ API, fallback sang getCurrentUser()
        const userData = data.user || getCurrentUser();

        if (!userData) {
          throw new Error("Cannot read logged-in user.");
        }

        setUser(userData);
        setIsAuth(true);

        // đảm bảo đồng bộ với localStorage (để useEffect & tab khác bắt được)
        localStorage.setItem("user", JSON.stringify(userData));

        return { success: true, user: userData };
      }

      throw new Error(data?.message || "Login failed");
    } catch (error) {
      setUser(null);
      setIsAuth(false);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // ---- LOGOUT ----
  const logout = async () => {
    try {
      setLoading(true);
      await logoutAPI();
    } catch (error) {
      console.error("Error logging out:", error);
    } finally {
      setUser(null);
      setIsAuth(false);
      setLoading(false);

      // xoá luôn ở localStorage cho sạch
      localStorage.removeItem("user");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  };

  // ---- UPDATE USER (khi chỉnh profile) ----
  const updateUser = (userData) => {
    setUser(userData);
    if (userData) {
      localStorage.setItem("user", JSON.stringify(userData));
    } else {
      localStorage.removeItem("user");
    }
  };

  const value = {
    user,      // object user (dùng để lấy tên, role...)
    isAuth,    // true/false: đã đăng nhập chưa
    loading,   // dùng cho spinner nếu muốn
    login,     // login(credentials)
    logout,    // logout()
    updateUser // cập nhật user sau khi edit profile
  };

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
