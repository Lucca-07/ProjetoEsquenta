import { api } from "./client";

export const numbersApi = {
    listDashboard: () => api.get("/numbers"),
    getSummary: () => api.get("/numbers/summary"),
};

export const sessionsApi = {
    list: () => api.get("/sessions"),
    create: (phone, nodeName) => api.post("/sessions", { phone, node_name: nodeName }),
    getStatus: (numberId) => api.get(`/sessions/${numberId}/status`),
    stop: (numberId) => api.post(`/sessions/${numberId}/stop`),
};

export const warmupApi = {
    start: (numberId) => api.post(`/warmup/${numberId}/start`),
    pause: (numberId) => api.post(`/warmup/${numberId}/pause`),
    startBulk: (numberIds) => api.post("/warmup/start-bulk", { number_ids: numberIds }),
    pauseBulk: (numberIds) => api.post("/warmup/pause-bulk", { number_ids: numberIds }),
    getStatus: (numberId) => api.get(`/warmup/${numberId}/status`),
    getLogs: (numberId) => api.get(`/warmup/${numberId}/logs`),
};

export const phrasesApi = {
    list: (activeOnly = false) => api.get(`/phrases?active_only=${activeOnly}`),
    create: (text, category) => api.post("/phrases", { text, category }),
    update: (id, payload) => api.put(`/phrases/${id}`, payload),
    remove: (id) => api.del(`/phrases/${id}`),
};
