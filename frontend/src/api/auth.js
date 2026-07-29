import { api } from "./client";

export const authApi = {
    login: (email, password) =>
        api.post("/auth/login", { email, password }),
    me: () => api.get("/auth/me"),
    listUsers: () => api.get("/auth/users"),
    createUser: (payload) => api.post("/auth/users", payload),
};

export function getStoredUser() {
    try {
        return JSON.parse(localStorage.getItem("auth_user"));
    } catch {
        return null;
    }
}

export function saveSession(session) {
    localStorage.setItem("auth_token", session.access_token);
    localStorage.setItem("auth_user", JSON.stringify(session.user));
}

export function clearSession() {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_user");
}
