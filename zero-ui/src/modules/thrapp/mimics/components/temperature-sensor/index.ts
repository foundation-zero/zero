import { ComponentOrientation } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-48171&t=JfBIEDjiEP5NKk6I-4";

export interface TemperatureSensorProps {
  orientation?: ComponentOrientation;
}

export const TEMPERATURE_SENSOR_WIDTH = 32;
export const TEMPERATURE_SENSOR_HEIGHT = 32;
export const TEMPERATURE_SENSOR_BASE_ORIENTATION = ComponentOrientation.Down;

export const TEMPERATURE_SENSOR_BODY_FILL = "var(--background-muted)";
export const TEMPERATURE_SENSOR_STROKE_COLOR = "var(--attention)";
export const TEMPERATURE_SENSOR_MARK_COLOR = "var(--foreground)";
