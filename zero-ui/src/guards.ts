import { RouteLocationNormalizedGeneric } from "vue-router";

export const attachReturnUrlGuard = (
  to: RouteLocationNormalizedGeneric,
  from: RouteLocationNormalizedGeneric,
) => {
  if (!to.query.returnUrl && from.query.returnUrl) {
    return { ...to, query: { ...to.query, returnUrl: from.query.returnUrl } };
  }
};
