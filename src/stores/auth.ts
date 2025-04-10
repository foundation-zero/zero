import { HasuraJWTToken, Roles } from "@/@types";
import { parseJwt } from "@/lib/utils";
import { useLocalStorage } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const token = useLocalStorage<string | null>("token", null);
  const isLoggedIn = computed(() => !!token.value);

  const decodedToken = computed(() => (token.value ? parseJwt<HasuraJWTToken>(token.value) : null));
  const roles = computed(
    () => decodedToken.value?.["https://hasura.io/jwt/claims"]?.["x-hasura-allowed-roles"] ?? [],
  );
  const hasRole = (role: Roles) => computed(() => roles.value.includes(role));
  const isAdmin = hasRole(Roles.Admin);
  const isUser = hasRole(Roles.User);

  function setToken(newToken: string) {
    token.value = newToken;
  }

  function clearToken() {
    token.value = null;
  }

  return { token, decodedToken, hasRole, isAdmin, isUser, roles, isLoggedIn, setToken, clearToken };
});
