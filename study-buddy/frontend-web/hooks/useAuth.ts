/**
 * hooks/useAuth.ts — Authentication hook
 * ========================================
 * Manages auth state: login, register, logout, current user.
 * Uses Zustand for global state + React Query for the /auth/me call.
 */

"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { create } from "zustand";
import { authApi } from "@/services/api";
import { clearSession, saveSession } from "@/lib/auth";
import type { LoginRequest, RegisterRequest, User } from "@/types";

// ── Zustand store for auth state ───────────────────────────────────────────

interface AuthStore {
  user: User | null;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));

// ── Main hook ──────────────────────────────────────────────────────────────

export function useAuth() {
  const router      = useRouter();
  const qc          = useQueryClient();
  const { user, setUser } = useAuthStore();

  // Fetch current user on mount (populates after page refresh)
  const { isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const res = await authApi.me();
      setUser(res.data);
      return res.data;
    },
    retry: false,
    staleTime: 5 * 60_000, // 5 minutes
  });

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: async (tokenRes) => {
      const meRes = await authApi.me();
      saveSession(tokenRes.data.access_token, meRes.data);
      setUser(meRes.data);
      qc.invalidateQueries({ queryKey: ["me"] });
      toast.success(`Welcome back, ${meRes.data.name}!`);
      router.push("/dashboard");
    },
    onError: () => {
      toast.error("Invalid email or password.");
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: () => {
      toast.success("Account created! Please sign in.");
      router.push("/login");
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail ?? "Registration failed.";
      toast.error(msg);
    },
  });

  // Logout
  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    qc.clear();
    toast.success("Logged out.");
    router.push("/");
  }, [qc, router, setUser]);

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login:    loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    isLoginPending:    loginMutation.isPending,
    isRegisterPending: registerMutation.isPending,
  };
}
