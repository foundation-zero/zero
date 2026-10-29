import { type Component, type Ref } from "vue";
import { RegisterField } from "../../mimics/data";
import { ModuleField } from "../../mimics/providers";
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
