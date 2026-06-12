export { default as MimicTooltip } from "./MimicTooltip.vue";
export { default as MimicTooltipProvider } from "./MimicTooltipProvider.vue";
export { default as MimicTooltipTrigger } from "./MimicTooltipTrigger.vue";
export { default as NoopTooltipProvider } from "./NoopTooltipProvider.vue";

import { createContext } from "reka-ui";
import { type Component, markRaw, ref, type Ref } from "vue";
import { MimicComponentType } from "../../types";
import { ExtractComponentFields } from "../../types/fields";

export type TooltipContent = {
  title: string;
  yardTag?: string;
  itemName?: string;
  technicalName?: string;
};

export type TooltipComponentContext<Type extends MimicComponentType = MimicComponentType> = {
  tooltip?: TooltipContent;
} & ExtractComponentFields<Type>;

export type TooltipContext = {
  data: Ref<TooltipComponentContext | null>;
  component: Ref<Component | null>;
  disabled?: boolean;
  setTooltip: <Type extends MimicComponentType>(
    context: TooltipComponentContext<Type>,
    component?: Component,
  ) => void;
  getData: <Type extends MimicComponentType>() => TooltipComponentContext<Type> | null;
  clear(): void;
};

export const [getTooltipContext, provideTooltipContext] =
  createContext<TooltipContext>("TooltipContext");

export const createTooltipContext = (): TooltipContext => {
  const component = ref<Component | null>(null);
  const data = ref<TooltipComponentContext | null>(null);

  const setTooltip = <Type extends MimicComponentType>(
    context: TooltipComponentContext<Type>,
    comp?: Component,
  ) => {
    if (!context.tooltip || !comp) return;

    data.value = context;
    component.value = markRaw(comp);
  };

  const getData = <Type extends MimicComponentType>() => {
    return data.value as TooltipComponentContext<Type> | null;
  };

  const clear = () => {
    data.value = null;
    component.value = null;
  };

  return {
    data,
    component,
    setTooltip,
    getData,
    clear,
  };
};
