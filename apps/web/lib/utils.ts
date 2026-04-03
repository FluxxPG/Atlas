import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const API_URL =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8011/api/v1";

export const WS_URL =
  process.env.WS_URL ??
  process.env.NEXT_PUBLIC_WS_URL ??
  "ws://127.0.0.1:8011/api/v1/ws/platform";
