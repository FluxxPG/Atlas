import "server-only";

import { cookies } from "next/headers";

import { API_URL } from "@/lib/utils";

const SESSION_COOKIE = "atlasbi_session";

export type SessionUser = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  default_organization?: {
    id: string;
    name: string;
    slug: string;
    plan: string;
    status: string;
  } | null;
};

type JsonOptions = {
  method?: string;
  auth?: boolean;
  body?: unknown;
};

export function getSessionToken() {
  return cookies().get(SESSION_COOKIE)?.value ?? null;
}

export function setSessionToken(token: string) {
  cookies().set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: false,
    path: "/"
  });
}

export function clearSessionToken() {
  cookies().delete(SESSION_COOKIE);
}

export async function apiJson<T>(path: string, fallback: T, options: JsonOptions = {}): Promise<T> {
  try {
    const response = await apiRequest(path, options);
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function apiText(path: string, fallback: string, options: JsonOptions = {}): Promise<string> {
  try {
    const response = await apiRequest(path, options);
    if (!response.ok) {
      return fallback;
    }
    return await response.text();
  } catch {
    return fallback;
  }
}

export async function apiRequest(path: string, options: JsonOptions = {}) {
  const headers = new Headers();
  headers.set("Content-Type", "application/json");

  if (options.auth) {
    const token = getSessionToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  return fetch(`${API_URL}${path}`, {
    cache: "no-store",
    method: options.method ?? "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  });
}

export async function getSessionUser() {
  const token = getSessionToken();
  if (!token) {
    return null;
  }
  return apiJson<SessionUser | null>("/auth/me", null, { auth: true });
}
