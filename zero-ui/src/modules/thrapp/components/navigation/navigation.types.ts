import { MimicKey } from "@/modules/thrapp/router/mimics";
import { RouteLocationRaw } from "vue-router";

/** Props `DefaultLayout` passes to the component in the `subNavigation` route meta. */
export type SubNavigationProps = {
  modules: MimicKey[];
  activeModule?: MimicKey;
};

export type MainTabName = "thrs/mimics" | "thrs/control";

export type MainTab = {
  name: MainTabName;
  label: "mimics" | "controls";
  views: Partial<Record<MimicKey, unknown>>;
};

export type NavigationLink = {
  to: RouteLocationRaw;
  active: boolean;
};

export type MainTabLink = NavigationLink & Pick<MainTab, "name" | "label">;
