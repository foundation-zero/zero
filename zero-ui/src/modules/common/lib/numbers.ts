export const enum Units {
  ACRE = "acre",
  BIT = "bit",
  BYTE = "byte",
  CELSIUS = "celsius",
  CENTIMETER = "centimeter",
  DAY = "day",
  DEGREE = "degree",
  FAHRENHEIT = "fahrenheit",
  FLUID_OUNCE = "fluid-ounce",
  FOOT = "foot",
  GALLON = "gallon",
  GIGABIT = "gigabit",
  GIGABYTE = "gigabyte",
  GRAM = "gram",
  HECTARE = "hectare",
  HOUR = "hour",
  INCH = "inch",
  KILOBIT = "kilobit",
  KILOBYTE = "kilobyte",
  KILOGRAM = "kilogram",
  KILOMETER = "kilometer",
  LITER = "liter",
  MEGABIT = "megabit",
  MEGABYTE = "megabyte",
  METER = "meter",
  MICROSECOND = "microsecond",
  MILE = "mile",
  MILE_SCANDINAVIAN = "mile-scandinavian",
  MILLILITER = "milliliter",
  MILLIMETER = "millimeter",
  MILLISECOND = "millisecond",
  MINUTE = "minute",
  MONTH = "month",
  NANOSECOND = "nanosecond",
  OUNCE = "ounce",
  PERCENT = "percent",
  PETABYTE = "petabyte",
  POUND = "pound",
  SECOND = "second",
  STONE = "stone",
  TERABIT = "terabit",
  TERABYTE = "terabyte",
  WEEK = "week",
  YARD = "yard",
  YEAR = "year",
}

export type NumberFormatter = (value: number, locale?: string) => string;
export type NumberTransformer = (value: number) => number;
export type UnitParam = Units | `${Units}` | `${Units}-per-${Units}`;

export const formatNumber =
  (
    digits: number,
    options?: Intl.NumberFormatOptions,
    transformFn?: NumberTransformer,
  ): NumberFormatter =>
  (value: number, locale: string = "en-US") => {
    const valueToFormat = transformFn ? transformFn(value) : value;

    // Handle the case where the valueToFormat is 0 and digits is 0, to avoid formatting issues (-0 edge case).
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
      ...options,
    }).format(digits === 0 && Math.round(valueToFormat) === 0 ? 0 : valueToFormat);
  };

export const formatUnit = (
  unit: UnitParam,
  digits = 1,
  options?: Intl.NumberFormatOptions,
  transformFn?: NumberTransformer,
) => formatNumber(digits, { style: "unit", unit, ...options }, transformFn);

formatNumber.default = formatNumber(1);
formatNumber.int = formatNumber(0);

export const formatPercentage = (digits: number): NumberFormatter => formatUnit("percent", digits);

formatPercentage.default = formatPercentage(0);

export const formatInt = formatNumber(0);
export const formatFixed = (digits: number, value: number, locale: string = "en-US") =>
  formatNumber(digits)(value, locale);

export const joulesToWatthours = (joules: number) => joules / 3600;
export const scaleNumber = (unscaledValue: number): number => {
  const absValue = Math.abs(unscaledValue);
  if (absValue < 1_000) return unscaledValue;
  else if (absValue < 1_000_000) return Math.sign(unscaledValue) * (absValue / 1_000);
  else return Math.sign(unscaledValue) * (absValue / 1_000_000);
};
export const ratioToPercentage = (value: number): number => value * 100;
