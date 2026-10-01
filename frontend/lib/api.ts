const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("nexora_token");
}

export function saveToken(token: string) {
  localStorage.setItem("nexora_token", token);
}

export function logout() {
  localStorage.removeItem("nexora_token");
  window.location.href = "/";
}

export async function api(
  path: string,
  options: RequestInit = {}
): Promise<any> {
  const headers = new Headers(options.headers);

  const isFormData = options.body instanceof FormData;

  if (!isFormData) {
    headers.set("Content-Type", "application/json");
  }

  const token = getToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store"
  });

  const text = await response.text();

  let data: any = {};

  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { detail: text };
  }

  if (!response.ok) {
    throw new Error(
      data?.detail || `Server xatosi: ${response.status}`
    );
  }

  return data;
}

export function apiUrl(path: string) {
  return `${API_URL}${path}`;
}
