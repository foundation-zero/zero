import { HTMLAttributes, inject, provide } from "vue";
import AutoEditor from "./AutoEditor.vue";
import FlowRateEditor from "./FlowRateEditor.vue";
import NumberEditor from "./NumberEditor.vue";
import OpenClosedEditor from "./OpenClosedEditor.vue";
import PendingIndicator from "./PendingIndicator.vue";
import PercentageEditor from "./PercentageEditor.vue";
import SubmitButton from "./SubmitButton.vue";
import TankLevelEditor from "./TankLevelEditor.vue";
import TemperatureEditor from "./TemperatureEditor.vue";
import ToggleEditor from "./ToggleEditor.vue";

export const FieldEditor = {
  Toggle: ToggleEditor,
  Submit: SubmitButton,
  Temperature: TemperatureEditor,
  Number: NumberEditor,
  Auto: AutoEditor,
  Percentage: PercentageEditor,
  OpenClosed: OpenClosedEditor,
  TankLevel: TankLevelEditor,
  FlowRate: FlowRateEditor,
  PendingIndicator,
};

export type FieldEditorProps<T> = {
  value?: T;
  class?: HTMLAttributes["class"];
};

export type NumberEditorProps = FieldEditorProps<number> & {
  formatOptions?: Intl.NumberFormatOptions;
  min?: number;
  max?: number;
  step?: number;
};

export const provideMultiLineEditor = (value: boolean) => provide("multiLineEditor", value);
export const injectMultiLineEditor = () => inject<boolean>("multiLineEditor", false);
