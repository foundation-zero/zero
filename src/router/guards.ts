import { Roles } from "@/@types";
import { useAuthStore } from "@/stores/auth";
import { useRoomStore } from "@/stores/rooms";
import { toRefs, watch } from "vue";
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
      return { name: "unauthorised" };
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

export const waitForRoom: BeforeResolveGuard = (to) => {
  if (to.query.room) {
    return new Promise((resolve) => {
      const store = useRoomStore();
      const { currentRoom } = toRefs(store);

      watch(
        currentRoom,
        (next) => {
          const invalidRoute =
            (to.name === "cabin:blinds" && next.blinds.length === 0) ||
            (to.name === "cabin:lights" && next.lights.length === 0);

          resolve({
            name: invalidRoute ? "cabin:airconditioning" : to.name,
            query: {},
          });
        },
        { once: true },
      );

      useRoomStore().setRoom(String(to.query.room));
    });
  }
};
