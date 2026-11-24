// Use: one small API helper and a polling hook, with clear loading and error states.
// Copyright (c) 2026 Imarah.tech. All rights reserved.
import { useCallback, useEffect, useState } from "react";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, options);
  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: "The server could not process this request." }));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : "Please check the form and try again.",
    );
  }
  return response.json() as Promise<T>;
}

export function useApi<T>(path: string, pollMs = 0) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [revision, setRevision] = useState(0);
  const refresh = useCallback(() => setRevision((value) => value + 1), []);
  useEffect(() => {
    let active = true;
    let timer: ReturnType<typeof setTimeout>;
    setData(null);
    setLoading(true);
    async function read() {
      try {
        const next = await api<T>(path);
        if (active) {
          setData(next);
          setError("");
        }
      } catch (err) {
        if (active)
          setError(
            err instanceof Error
              ? err.message
              : "Cannot reach the local server.",
          );
      } finally {
        if (active) {
          setLoading(false);
          if (pollMs) timer = setTimeout(read, pollMs);
        }
      }
    }
    void read();
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [path, pollMs, revision]);
  return { data, error, loading, refresh };
}

export const seconds = (ms: number) => `${(ms / 1000).toFixed(1)}s`;
export const date = (value: string) =>
  new Date(value).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
