import { HTMLAttributes } from "vue";

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
