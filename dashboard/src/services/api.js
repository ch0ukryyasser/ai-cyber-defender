import axios from "axios";

const API_BASE = "http://localhost:5001/api";

export const api = axios.create({
  baseURL: API_BASE,
});

export const getAlerts = () => api.get("/alerts").then(r => r.data);
export const getBlockedIps = () => api.get("/blocked-ips").then(r => r.data);
export const getTraffic = () => api.get("/traffic").then(r => r.data);
export const getReports = () => api.get("/reports").then(r => r.data);
