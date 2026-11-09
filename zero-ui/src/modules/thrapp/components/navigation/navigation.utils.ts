import { DOCUMENTATION } from "@/modules/thrapp/router/documentation";
import { MimicKey } from "@/modules/thrapp/router/mimics";
import { computed } from "vue";
import { useRoute } from "vue-router";
import { DEFAULT_MODULE, DOCUMENTATION_ROUTE, MAIN_TABS } from "./navigation.consts";
import { MainTabLink, NavigationLink } from "./navigation.types";

/** Main tabs and the documentation link, keeping the current module where the target page has it. */
export const useThrappNavigation = () => {
  const route = useRoute();
  const currentModule = computed(() => route.params.module as MimicKey | undefined);

  const moduleWithView = (views: Partial<Record<MimicKey, unknown>>) =>
    currentModule.value && views[currentModule.value] ? currentModule.value : DEFAULT_MODULE;

  const tabs = computed<MainTabLink[]>(() =>
    MAIN_TABS.map(({ name, label, views }) => ({
      name,
      label,
      to: { name, params: { module: moduleWithView(views) } },
      active: route.name === name,
    })),
  );

  const documentation = computed<NavigationLink>(() => ({
    to: { name: DOCUMENTATION_ROUTE, params: { module: moduleWithView(DOCUMENTATION) } },
    active: route.name === DOCUMENTATION_ROUTE,
  }));

  return { tabs, documentation };
};
