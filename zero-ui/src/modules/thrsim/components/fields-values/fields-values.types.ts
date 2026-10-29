import { ChartDataType, SeriesChart } from "@/modules/common/types";
import { Ref } from "vue";

export type FieldSeries = [field: string, series: SeriesChart<ChartDataType>[]];
export type FieldsValuesContext = {
  series: Ref<FieldSeries[]>;
  selected: Ref<string[]>;
  activeSeries: Ref<FieldSeries[]>;
};
