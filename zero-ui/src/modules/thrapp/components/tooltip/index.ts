export { default as MimicTooltip } from "./MimicTooltip.vue";
export { default as MimicTooltipProvider } from "./MimicTooltipProvider.vue";
export { default as MimicTooltipTrigger } from "./MimicTooltipTrigger.vue";
export { default as NoopTooltipProvider } from "./NoopTooltipProvider.vue";

import { createContext } from "reka-ui";
import { type Component, markRaw, ref, type Ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import {
  getTooltipContext as _getTooltipContext,
  findTooltipContext,
  RegisterField,
} from "../../mimics/data";
import { ModuleField } from "../../mimics/providers";
import { TOOLTIPS } from "../../mimics/tooltips";
import { MimicComponentType } from "../../types";
import { ExtractComponentFields } from "../../types/fields";

export type TooltipContent = {
  title: string;
  yardTag?: string;
  componentType?: string;
  technicalName?: string;
  mqttTopic?: string;
};

export type TooltipComponentContext<Type extends MimicComponentType = MimicComponentType> = {
  tooltip?: TooltipContent;
  registerField?: RegisterField<Type>;
  type?: Type;
  index?: number;
} & ExtractComponentFields<Type>;

export type TooltipContext = {
  data: Ref<TooltipComponentContext | null>;
  component: Ref<Component | null>;
  title: Ref<string | null>;
  dialog: Ref<Component | null>;
  disabled?: boolean;
  setTooltip: <Type extends MimicComponentType>(
    context: TooltipComponentContext<Type>,
    component?: Component,
  ) => void;
  setDialog(component: Component): void;
  closeDialog(): void;
  findTooltipContext: (source: ModuleField | string) => TooltipComponentContext[];
  getData: <Type extends MimicComponentType>() => TooltipComponentContext<Type> | null;
  clear(): void;
};

export const [getTooltipContext, provideTooltipContext] =
  createContext<TooltipContext>("TooltipContext");

export const createTooltipContext = (): TooltipContext => {
  const { te, t } = useI18n();
  const component = ref<Component | null>(null);
  const dialog = ref<Component | null>(null);
  const data = ref<TooltipComponentContext | null>(null);
  const title = ref<string | null>(null);

  const setTooltip = <Type extends MimicComponentType>(
    context: TooltipComponentContext<Type>,
    comp?: Component,
  ) => {
    if (!context.tooltip || !comp) return;

    data.value = context as TooltipComponentContext;
    component.value = markRaw(comp);
  };

  const getData = <Type extends MimicComponentType>() => {
    return data.value as TooltipComponentContext<Type> | null;
  };

  const clear = () => {
    data.value = null;
    component.value = null;
    dialog.value = null;
    title.value = null;
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
        const field = String(next.tooltip);
        const type = String(next.type) as MimicComponentType;
        const index = Number(next.index) || 0;

        if (!field) return;

        const tooltipContext = _getTooltipContext(type)(field as never, index);

        if (!tooltipContext) return;

        setTooltip(tooltipContext, TOOLTIPS[type]);
        const titleKey = `thrapp.tooltips.titles.${type}`;
        title.value = te(titleKey) ? t(titleKey) : (tooltipContext?.tooltip?.title ?? null);
      }
    },
    { immediate: true },
  );

  return {
    data,
    component,
    dialog,
    title,
    findTooltipContext,
    setTooltip,
    setDialog,
    closeDialog,
    getData,
    clear,
  };
};
