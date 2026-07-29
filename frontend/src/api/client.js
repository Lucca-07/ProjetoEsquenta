const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
    const token = localStorage.getItem("auth_token");
    const response = await fetch(`${BASE_URL}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(options.headers || {}),
        },
        ...options,
    });

    if (!response.ok) {
        let detail = response.statusText;
        try {
            const body = await response.json();
            detail = body.detail || detail;
        } catch {
            // resposta sem corpo JSON, mantém o statusText
        }
        const error = new Error(
            typeof detail === "string" ? detail : JSON.stringify(detail),
        );
        error.status = response.status;
        if (response.status === 401 && path !== "/auth/login") {
            localStorage.removeItem("auth_token");
            localStorage.removeItem("auth_user");
            window.location.assign("/");
        }
        throw error;
    }

    if (response.status === 204) return null;
    return response.json();
}

export const api = {
    get: (path) => request(path, { method: "GET" }),
    post: (path, body) => request(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),
    put: (path, body) => request(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),
    del: (path) => request(path, { method: "DELETE" }),
};
