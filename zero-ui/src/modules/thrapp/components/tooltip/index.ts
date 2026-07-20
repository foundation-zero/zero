export { default as MimicTooltip } from "./MimicTooltip.vue";
export { default as MimicTooltipProvider } from "./MimicTooltipProvider.vue";
export { default as MimicTooltipTrigger } from "./MimicTooltipTrigger.vue";
export { default as NoopTooltipProvider } from "./NoopTooltipProvider.vue";

import { isEqual } from "lodash";
import { createContext } from "reka-ui";
import { type Component, markRaw, ref, type Ref, toRefs, watch } from "vue";
import { useRoute } from "vue-router";
import { MimicComponentFieldsMap } from "../../mimics/modules/index.ts";
import { ModuleField } from "../../mimics/providers/index.ts";
import { TOOLTIPS } from "../../mimics/tooltips";
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
  dialog: Ref<Component | null>;
  disabled?: boolean;
  setTooltip: <Type extends MimicComponentType>(
    context: TooltipComponentContext<Type>,
    component?: Component,
  ) => void;
  setDialog(component: Component): void;
  closeDialog(): void;
  findTooltipContext: (
    source: ModuleField,
  ) => [MimicComponentType, TooltipComponentContext] | undefined;
  getData: <Type extends MimicComponentType>() => TooltipComponentContext<Type> | null;
  clear(): void;
};

export const [getTooltipContext, provideTooltipContext] =
  createContext<TooltipContext>("TooltipContext");

export const createTooltipContext = (
  sourceData: Partial<MimicComponentFieldsMap>,
): TooltipContext => {
  const component = ref<Component | null>(null);
  const dialog = ref<Component | null>(null);
  const data = ref<TooltipComponentContext | null>(null);

  const setTooltip = <Type extends MimicComponentType>(
    context: TooltipComponentContext<Type>,
    comp?: Component,
  ) => {
    if (!context.tooltip || !comp) return;

    data.value = context as TooltipComponentContext;
    component.value = markRaw(comp);
  };

  const findTooltipContext = (
    source: ModuleField,
  ): [MimicComponentType, TooltipComponentContext] | undefined => {
    const typesData = Object.entries(sourceData) as [
      MimicComponentType,
      Record<string, TooltipComponentContext>,
    ][];

    for (const [type, data] of typesData) {
      const values = Object.values(data) as TooltipComponentContext[];

      const sourceValue = values.find((val) => isEqual(val.source, source));

      if (sourceValue) {
        return [type, sourceValue];
      }
    }
  };

  const getData = <Type extends MimicComponentType>() => {
    return data.value as TooltipComponentContext<Type> | null;
  };

  const clear = () => {
    data.value = null;
    component.value = null;
    dialog.value = null;
  };

  const setDialog = (comp: Component) => {
    dialog.value = markRaw(comp);
  };

  const closeDialog = () => {
    dialog.value = null;
  };

  const { query } = toRefs(useRoute());

  watch(
    query,
    (next, prev) => {
      if (!next.tooltip) {
        clear();
      } else if (next.tooltip !== prev?.tooltip) {
        const parts = String(next.tooltip).split(".");
        if (parts.length !== 3) return;

        const field = parts as ModuleField;
        const tooltipContext = findTooltipContext(field);

        if (!tooltipContext) return;

        const [type, tooltip] = tooltipContext;

        setTooltip(tooltip, TOOLTIPS[type]);
      }
    },
    { immediate: true },
  );

  return {
    data,
    component,
    dialog,
    findTooltipContext,
    setTooltip,
    setDialog,
    closeDialog,
    getData,
    clear,
  };
};
