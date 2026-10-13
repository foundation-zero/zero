import { ChartDataType, SeriesChart } from "@/modules/common/types";
import { createContext } from "reka-ui";
import { Ref } from "vue";

export { default as FieldCurrent } from "./FieldCurrent.vue";
export { default as FieldsFilter } from "./FieldsFilter.vue";

export { default as FieldHeader } from "./FieldHeader.vue";
export { default as FieldsValues } from "./FieldsValues.vue";
export { default as FieldsValuesEmpty } from "./FieldsValuesEmpty.vue";
export { default as FieldValues } from "./FieldValues.vue";

export type FieldSeries = [field: string, series: SeriesChart<ChartDataType>[]];
export type FieldsValuesContext = {
  series: Ref<FieldSeries[]>;
  selected: Ref<string[]>;
  activeSeries: Ref<FieldSeries[]>;
};

export const [getContext, provideContext] = createContext<FieldsValuesContext>("FieldsValues");
