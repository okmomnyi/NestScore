import { PaginatedPlots, PaginatedReviews, Plot, PlotMap } from "@/types";

const isServer = typeof window === "undefined";
export const API_BASE_URL = isServer
  ? (process.env.INTERNAL_API_BASE_URL || "http://nestscore_backend:8000/api")
  : (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8001/api");
export const TURNSTILE_SITE_KEY = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY || "";
export const ADS_ENABLED = process.env.NEXT_PUBLIC_ADS_ENABLED === "true";
export const DEFAULT_MAP_CENTER: [number, number] = [-0.0530, 37.6560];
export const DEFAULT_MAP_ZOOM = 14;
export const PLOT_AREAS = [
  "Nchiru",
  "Katheri",
  "Campus-adjacent",
  "Other"
] as const;
