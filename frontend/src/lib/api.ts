import axios from "axios";
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:5000").replace(/\/+$/, "");
export const api = axios.create({ baseURL: API_BASE, headers: { "Content-Type": "application/json" }, timeout: 30000 });
api.interceptors.request.use((config) => { const token = localStorage.getItem("mori_access_token"); if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
export function getToken(){ return localStorage.getItem("mori_access_token"); }
export function setSession(token:string,user?:unknown){localStorage.setItem("mori_access_token",token);if(user)localStorage.setItem("mori_user",JSON.stringify(user));}
export function clearSession(){localStorage.removeItem("mori_access_token");localStorage.removeItem("mori_user");}
export async function assetBlobUrl(path:string){const response=await api.get(path,{responseType:"blob"});return URL.createObjectURL(response.data);}
