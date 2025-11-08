import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle 401 errors (unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't redirect if we're already on login/signup pages or if it's an auth endpoint
      const currentPath = window.location.pathname;
      const isAuthEndpoint =
        error.config?.url?.includes("/api/auth/login") ||
        error.config?.url?.includes("/api/auth/register") ||
        error.config?.url?.includes("/api/auth/validate-password") ||
        error.config?.url?.includes("/api/auth/change-password");

      // Only redirect if not on auth pages and not calling auth endpoints
      if (
        !isAuthEndpoint &&
        currentPath !== "/login" &&
        currentPath !== "/signup"
      ) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (data) => api.post("/api/auth/register", data),
  login: (data) => {
    const formData = new FormData();
    formData.append("username", data.email);
    formData.append("password", data.password);
    return api.post("/api/auth/login", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getMe: () => api.get("/api/auth/me"),
  updateProfile: (data) => api.put("/api/auth/profile", data),
  validatePassword: (data) => api.post("/api/auth/validate-password", data),
  changePassword: (data) => api.post("/api/auth/change-password", data),
};

// Detection endpoints
export const detectAPI = {
  text: (text) => api.post("/api/detect/text", { text }),
  image: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/api/detect/image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  video: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/api/detect/video", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// Results endpoints
export const resultsAPI = {
  getAll: (limit = 50, skip = 0) =>
    api.get(`/api/results/?limit=${limit}&skip=${skip}`),
  getStats: () => api.get("/api/results/stats"),
};

// Contact endpoints
export const contactAPI = {
  submit: (data) => api.post("/api/contact", data),
};

export default api;
