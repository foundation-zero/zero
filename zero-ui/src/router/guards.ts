import { Roles } from "@/@types";
import { useAuthStore } from "@/stores/auth";
import { _Awaitable, RouteLocationNormalizedGeneric, RouteLocationRaw, Router } from "vue-router";

export const withGuards = (router: Router) => {
  router.beforeEach((to) => {
    if (to.meta.requiresAuth === false) return true;

    const authStore = useAuthStore();

    if (
      !authStore.isLoggedIn ||
      (to.meta.role && !authStore.hasRole(to.meta.role as Roles).value) ||
      to.matched.some(
        (route) => route.meta.role && !authStore.hasRole(route.meta.role as Roles).value,
      )
    ) {
      return { name: "auth" };
    }
  });

  router.beforeResolve(async (to, from) => {
    const next = await (to.meta.beforeResolve as BeforeResolveGuard)?.(to, from, router);

    if (next) {
      router.replace(next);
    }
  });

  return router;
};

export type BeforeResolveGuard = (
  to: RouteLocationNormalizedGeneric,
  from: RouteLocationNormalizedGeneric,
  router: Router,
) => _Awaitable<RouteLocationRaw | void>;
