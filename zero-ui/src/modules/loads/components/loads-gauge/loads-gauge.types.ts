import { ToRefs, type Ref } from "vue";
import { ReferenceThresholds } from "../../types";
import { Colors } from "./loads-gauge.consts";

export interface Coords {
  x: number;
  y: number;
}

export interface CoordsWithRadiansAngle extends Coords {
  angleInRadians: number;
}

// GaugeStep defines the data type for both the ticks and points of the gauge.
// Points are the dots/circles and can be colored individually.
// Ticks are the lines on the gauge and are only visible at specific indices based on the visible range and thresholds.
export interface GaugeStep extends CoordsWithRadiansAngle {
  value: number;
  angle: number;
  color: Colors;
}

export type Range = [start: number, end: number];

export interface GaugeRootProps {
  currentValue?: number; // Current/actual value, optional to allow defaulting to target
  scale: Range; // Scale/range [min, max]
  thresholds?: ReferenceThresholds; // Warning/Alarm thresholds
}

export type GaugeRootContext = ToRefs<GaugeRootProps> & {
  points: Ref<GaugeStep[]>;
  ticks: Ref<GaugeStep[]>;
  target: Ref<number>;
  targetRange: Ref<Range>;
};
