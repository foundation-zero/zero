export const enum ControlType {
  LIGHT = "lights",
  BLIND = "blinds",
  AMPLIFIER = "amplifier",
  TEMPERATURE = "temperature",
  HUMIDITY = "humidity",
  CO2 = "co2",
}

export const enum SensorType {
  TEMPERATURE = "temperature",
  HUMIDITY = "humidity",
  CO2 = "co2",
  PRESENCE = "presence",
}

export const enum RoomGroup {
  AFT = "AFT",
  MID = "MID",
  FORE = "FORE",
  UPPERDECK = "UPPERDECK",
  HALLWAYS = "HALLWAYS",
}

export const enum ValidationStatus {
  OK = "ok",
  WARN = "warn",
  FAIL = "fail",
  UNKNOWN = "unknown",
}

export const enum Units {
  PPM = "ppm",
}

export const enum ChartPeriod {
  HOUR = "hour",
  DAY = "day",
  WEEK = "week",
  MONTH = "month",
  YEAR = "year",
}
