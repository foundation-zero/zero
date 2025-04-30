import { HasuraJWTToken, Roles } from "@/@types";
import { useLocalStorage } from "@vueuse/core";
import { jwtDecode } from "jwt-decode";
import { defineStore } from "pinia";
import { computed } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const token = useLocalStorage<string | null>("token", null);
  const isLoggedIn = computed(() => roles.value.length > 0);

  const decodedToken = computed(() =>
    token.value ? jwtDecode<HasuraJWTToken>(token.value) : null,
  );

  const roles = computed(
    () => decodedToken.value?.["https://hasura.io/jwt/claims"]?.["x-hasura-allowed-roles"] ?? [],
  );

  const cabin = computed(
    () => decodedToken.value?.["https://hasura.io/jwt/claims"]?.["x-hasura-cabin"] ?? null,
  );

  const hasRole = (requiredRole: Roles) => computed(() => roles.value.includes(requiredRole));

  const isAdmin = hasRole(Roles.Admin);
  const isUser = hasRole(Roles.User);

  function setToken(newToken: string) {
    token.value = newToken;

    return { cabin, roles, isAdmin, isUser };
  }

  function clearToken() {
    token.value = null;
  }

  return {
    token,
    cabin,
    decodedToken,
    hasRole,
    isAdmin,
    isUser,
    roles,
    isLoggedIn,
    setToken,
    clearToken,
  };
});
