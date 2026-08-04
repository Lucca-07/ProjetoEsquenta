import { api } from "./client";

export const numbersApi = {
    listDashboard: () => api.get("/numbers"),
    getSummary: () => api.get("/numbers/summary"),
};

export const sessionsApi = {
    list: () => api.get("/sessions"),
    create: (phone, nodeName, connectionMethod = "qr") =>
        api.post("/sessions", {
            phone,
            node_name: nodeName,
            connection_method: connectionMethod,
        }),
    getPendingStatus: (sessionName, phone, nodeName, connectionMethod = "qr") =>
        api.get(
            `/sessions/pending/${encodeURIComponent(sessionName)}/status?phone=${encodeURIComponent(phone)}&node_name=${encodeURIComponent(nodeName)}&connection_method=${encodeURIComponent(connectionMethod)}`,
        ),
    requestCode: (sessionName, phone, nodeName) =>
        api.post(
            `/sessions/pending/${encodeURIComponent(sessionName)}/code`,
            { phone, node_name: nodeName },
        ),
    getStatus: (numberId) => api.get(`/sessions/${numberId}/status`),
    reconnect: (numberId) =>
        api.post(`/sessions/${numberId}/reconnect`),
    stop: (numberId) => api.post(`/sessions/${numberId}/stop`),
};

export const warmupApi = {
    start: (numberId) => api.post(`/warmup/${numberId}/start`),

    pause: (numberId) => api.post(`/warmup/${numberId}/pause`),

    startBulk: (payload) => api.post("/warmup/start-bulk", payload),

    pauseBulk: (numberIds) =>
        api.post("/warmup/pause-bulk", {
            number_ids: numberIds,
        }),

    stopBulk: (numberIds) =>
        api.post("/warmup/stop-bulk", {
            number_ids: numberIds,
        }),

    getStatus: (numberId) => api.get(`/warmup/${numberId}/status`),

    getLogs: (numberId) => api.get(`/warmup/${numberId}/logs`),
};

export const phrasesApi = {
    list: (activeOnly = false) => api.get(`/phrases?active_only=${activeOnly}`),
    create: (text, category) => api.post("/phrases", { text, category }),
    update: (id, payload) => api.put(`/phrases/${id}`, payload),
    remove: (id) => api.del(`/phrases/${id}`),
};

export const logsApi = {
    dashboard: ({ days, phone, status } = {}) => {
        const params = new URLSearchParams();
        if (days) params.set("days", days);
        if (phone) params.set("phone", phone);
        if (status) params.set("status", status);
        const query = params.toString();
        return api.get(`/logs/dashboard${query ? `?${query}` : ""}`);
    },
    deleteWarmup: (groupId) => api.del(`/logs/warmups/${groupId}`),
};
