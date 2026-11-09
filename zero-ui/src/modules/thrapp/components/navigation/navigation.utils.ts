import { MimicKey } from "@/modules/thrapp/router/mimics";
import { computed } from "vue";
import { useRoute } from "vue-router";
import { DEFAULT_MODULE, DOCUMENTATION_ROUTE, MAIN_TABS } from "./navigation.consts";
import { MainTabLink, NavigationLink } from "./navigation.types";

/** Main tabs and the documentation link, keeping the current module where the target page has it. */
export const useThrappNavigation = () => {
  const route = useRoute();
  const currentModule = computed(() => route.params.module as MimicKey | undefined);

  const tabs = computed<MainTabLink[]>(() =>
    MAIN_TABS.map(({ name, label, views }) => {
      const module =
        currentModule.value && views[currentModule.value] ? currentModule.value : DEFAULT_MODULE;
      return { name, label, to: { name, params: { module } }, active: route.name === name };
    }),
  );

  const documentation = computed<NavigationLink>(() => ({
    to: { name: DOCUMENTATION_ROUTE, params: { module: currentModule.value ?? DEFAULT_MODULE } },
    active: route.name === DOCUMENTATION_ROUTE,
  }));

  return { tabs, documentation };
};
