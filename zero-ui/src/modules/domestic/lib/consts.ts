export const CO2_THRESHOLDS: [warning: number, critical: number] = [1000, 2000];
export const CO2_RANGE = [400, 2500];
export const CO2_SETPOINT_RANGE = [400, 1000];

export const HUMIDITY_THRESHOLDS: [humidityLow: number, humidityHigh: number] = [35, 60];
export const HUMIDITY_RANGE = [30, 80];
export const HUMIDITY_SETPOINT_RANGE = [40, 60];

export const TEMPERATURE_THRESHOLDS: [tempWarm: number, tempHot: number] = [25, 30];
export const TEMPERATURE_RANGE = [15, 35];
export const TEMPERATURE_SETPOINT_RANGE = [18, 23];

export const DEMO_MODE = import.meta?.env?.VITE_DEMO_MODE === "1";
