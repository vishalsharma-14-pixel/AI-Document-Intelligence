import { apiClient } from "./client";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
}

export async function signup(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/api/auth/signup", { email, password });
  return data;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  const { data } = await apiClient.post<TokenResponse>("/api/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data;
}

export async function fetchMe(): Promise<UserResponse> {
  const { data } = await apiClient.get<UserResponse>("/api/auth/me");
  return data;
}
