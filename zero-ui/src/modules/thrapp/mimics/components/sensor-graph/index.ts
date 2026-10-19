export { default as SensorGraph } from "./SensorGraph.vue";

// This must match with the grafana dashboard panels
export const enum GraphType {
  TIMESERIES = "panel-1",
  STAT = "panel-2",
  GAUGE = "panel-3",
}
