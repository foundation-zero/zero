import { HTMLAttributes } from "vue";
import AutoEditor from "./AutoEditor.vue";
import NumberEditor from "./NumberEditor.vue";
import OnOffEditor from "./OnOffEditor.vue";
import OpenClosedEditor from "./OpenClosedEditor.vue";
import PercentageEditor from "./PercentageEditor.vue";
import SubmitButton from "./SubmitButton.vue";
import TemperatureEditor from "./TemperatureEditor.vue";

export const FieldEditor = {
  OnOff: OnOffEditor,
  Submit: SubmitButton,
  Temperature: TemperatureEditor,
  Number: NumberEditor,
  Auto: AutoEditor,
  Percentage: PercentageEditor,
  OpenClosed: OpenClosedEditor,
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
