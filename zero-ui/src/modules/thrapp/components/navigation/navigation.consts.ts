import { MIMICS, MimicKey } from "@/modules/thrapp/router/mimics";
import { PARAMETERS } from "@/modules/thrapp/router/parameters";
import { MainTab } from "./navigation.types";

export const DEFAULT_MODULE: MimicKey = "dhw";

export const DOCUMENTATION_ROUTE = "thrs/documentation";

export const MAIN_TABS: MainTab[] = [
  { name: "thrs/mimics", label: "mimics", views: MIMICS },
  { name: "thrs/control", label: "controls", views: PARAMETERS },
];

// 36 px icon buttons, grown to a 44 px touch target on coarse pointers.
export const ICON_BUTTON_CLASS = "size-9 pointer-coarse:size-11";

// Buttons on the dark banner: a translucent background and brand-coloured icon (design spec).
export const BANNER_BUTTON_CLASS = "bg-background/50 text-brand rounded-md";
