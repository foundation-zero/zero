import { HTMLAttributes, inject, provide } from "vue";
import AutoEditor from "./AutoEditor.vue";
import DurationEditor from "./DurationEditor.vue";
import FlowRateEditor from "./FlowRateEditor.vue";
import NumberEditor from "./NumberEditor.vue";
import OpenClosedEditor from "./OpenClosedEditor.vue";
import PendingIndicator from "./PendingIndicator.vue";
import PercentageEditor from "./PercentageEditor.vue";
import PidEditor from "./PidEditor.vue";
import PowerEditor from "./PowerEditor.vue";
import SubmitButton from "./SubmitButton.vue";
import TankLevelEditor from "./TankLevelEditor.vue";
import TemperatureEditor from "./TemperatureEditor.vue";
import ToggleEditor from "./ToggleEditor.vue";

export const FieldEditor = {
  get Toggle() {
    return ToggleEditor;
  },
  get Submit() {
    return SubmitButton;
  },
  get Temperature() {
    return TemperatureEditor;
  },
  get Number() {
    return NumberEditor;
  },
  get Auto() {
    return AutoEditor;
  },
  get Percentage() {
    return PercentageEditor;
  },
  get OpenClosed() {
    return OpenClosedEditor;
  },
  get TankLevel() {
    return TankLevelEditor;
  },
  get FlowRate() {
    return FlowRateEditor;
  },
  get Duration() {
    return DurationEditor;
  },
  get Power() {
    return PowerEditor;
  },
  get PendingIndicator() {
    return PendingIndicator;
  },
  get PidTuning() {
    return PidEditor;
  },
};

export type FieldEditorProps<T> = {
  value?: T;
  class?: HTMLAttributes["class"];
};

export type NumberEditorProps<T = number> = FieldEditorProps<T> & {
  formatOptions?: Intl.NumberFormatOptions;
  min?: number;
  max?: number;
  step?: number;
};

export const provideMultiLineEditor = (value: boolean) => provide("multiLineEditor", value);
export const injectMultiLineEditor = () => inject<boolean>("multiLineEditor", false);
