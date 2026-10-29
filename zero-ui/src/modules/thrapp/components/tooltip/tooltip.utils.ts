import { createContext } from "reka-ui";
import { type Component, markRaw, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { getTooltipContext as _getTooltipContext, findTooltipContext } from "../../mimics/data";
import { TOOLTIPS } from "../../mimics/tooltips";
import { MimicComponentType } from "../../types";
import { TooltipComponentContext, TooltipContext } from "./tooltip.types";

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
