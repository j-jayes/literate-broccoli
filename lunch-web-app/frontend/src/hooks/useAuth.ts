import { useState, useEffect, useCallback } from "react";
import { checkAuth, login as apiLogin } from "../api";

export function useAuth() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    checkAuth().then(setAuthenticated);
  }, []);

  const login = useCallback(async (password: string) => {
    await apiLogin(password);
    setAuthenticated(true);
  }, []);

  return { authenticated, login };
}
