import { NumberFormatter } from "@/modules/common/lib/utils.ts";
import { HTMLAttributes } from "vue";

export type FieldRendererProps<T> = {
  value?: T;
  class?: HTMLAttributes["class"];
  format?: NumberFormatter;
  transform?: (value: T) => T;
};
