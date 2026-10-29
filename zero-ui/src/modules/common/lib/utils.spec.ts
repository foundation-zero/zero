import { describe, expect, test, vi } from "vitest";
import { ref } from "vue";
import {
  capitalizeFirst,
  cn,
  compareByName,
  entriesOf,
  extractProperty,
  generateRandomId,
  isDefined,
  isEntry,
  isStamped,
  isStampedWithSource,
  keysOf,
  logToSeries,
  mmath,
  ratioAsPercentage,
  separateDecimals,
  stamp,
  stampWithSource,
  toCapitalized,
  toEntries,
  toInversedPercentage,
  toRecord,
  toTimeSeriesData,
  toUpperCamelCase,
  tScoped,
  unstamp,
  useFixed,
  valueAsArray,
  valueWithValidation,
  writeProtected,
} from "./utils";

vi.mock("vue-i18n", () => {
  const messages: Record<string, string> = { "pump.title": "Pump", "pump.speed": "Speed {value}" };
  const t = (key: string, value?: Record<string, unknown>) =>
    (messages[key] ?? key).replace(/{(\w+)}/g, (_, name) => String(value?.[name]));

  return { useI18n: () => ({ t, te: (key: string) => key in messages }) };
});

const timestamp = new Date("2026-01-01T12:00:00Z");

describe("strings", () => {
  test("cn merges conflicting tailwind classes", () => {
    expect(cn("p-2 text-sm", { hidden: false }, "p-4")).toBe("text-sm p-4");
  });

  test("capitalizeFirst only changes the first character", () => {
    expect(capitalizeFirst("pumpSpeed")).toBe("PumpSpeed");
  });

  test("toCapitalized lowercases the rest", () => {
    expect(toCapitalized("hELLO")).toBe("Hello");
  });

  test("toUpperCamelCase splits words on capitals", () => {
    expect(toUpperCamelCase("PumpSpeed")).toBe("Pump Speed");
  });

  test("tScoped prefixes keys with its scope", () => {
    const t = tScoped("pump");

    expect(t("title")).toBe("Pump");
    expect(t("speed", { value: 50 })).toBe("Speed 50");
  });

  test("tScoped.exists checks keys within its scope", () => {
    const t = tScoped("pump");

    expect(t.exists("title")).toBe(true);
    expect(t.exists("missing")).toBe(false);
  });
});

describe("comparisons", () => {
  test("isDefined rejects only null and undefined", () => {
    expect([0, "", false, null, undefined].filter(isDefined)).toEqual([0, "", false]);
  });

  test("compareByName sorts missing names first", () => {
    const items = [{ name: "b" }, { name: null }, { name: "a" }];

    expect(items.sort(compareByName).map(({ name }) => name)).toEqual([null, "a", "b"]);
  });
});

describe("percentages", () => {
  test("ratioAsPercentage converts both ways", () => {
    const ratio = ref<number | undefined>(0.25);
    const percentage = ratioAsPercentage(ratio);

    expect(percentage.value).toBe(25);

    percentage.value = 50;
    expect(ratio.value).toBe(0.5);
  });

  test("ratioAsPercentage can default to zero", () => {
    expect(ratioAsPercentage(undefined).value).toBeUndefined();
    expect(ratioAsPercentage(undefined, true).value).toBe(0);
  });

  test("toInversedPercentage", () => {
    expect(toInversedPercentage(ref(30))).toBe(70);
  });

  test("separateDecimals splits the integer and decimal part", () => {
    const { integer, decimal } = separateDecimals(ref(21.46), 2);

    expect(integer.value).toBe(21);
    expect(decimal.value).toBe(46);
  });
});

describe("writable computeds", () => {
  test("valueWithValidation ignores invalid values", () => {
    const value = ref(1);
    const validated = valueWithValidation(value, (next) => next > 0);

    validated.value = -1;
    expect(value.value).toBe(1);

    validated.value = 2;
    expect(value.value).toBe(2);
  });

  test("valueAsArray wraps the value and rejects empty arrays", () => {
    const value = ref("a");
    const array = valueAsArray(value);

    expect(array.value).toEqual(["a"]);

    array.value = ["b", "c"];
    expect(value.value).toBe("b");
    expect(() => (array.value = [])).toThrow("Array cannot be empty");
  });

  test("writeProtected only writes when allowed", () => {
    const value = ref(1);
    const allowed = ref(false);
    const protectedValue = writeProtected(value, allowed);

    protectedValue.value = 2;
    expect(value.value).toBe(1);

    allowed.value = true;
    protectedValue.value = 2;
    expect(value.value).toBe(2);
  });
});

describe("stamps", () => {
  test("stamp and unstamp", () => {
    const stamped = stamp(ref(42), timestamp);

    expect(stamped).toEqual({ value: 42, timestamp });
    expect(unstamp(stamped)).toBe(42);
    expect(unstamp(42)).toBe(42);
  });

  test("isStamped checks objects and the first item of arrays", () => {
    expect(isStamped({ value: 1, timestamp })).toBe(true);
    expect(isStamped([{ value: 1, timestamp }])).toBe(true);
    expect(isStamped({ value: 1 })).toBe(false);
    expect(isStamped(null)).toBe(false);
  });

  test("isStampedWithSource requires a source", () => {
    expect(isStampedWithSource(stampWithSource(1, "sensor", timestamp))).toBe(true);
    expect(isStampedWithSource(stamp(1, timestamp))).toBe(false);
  });

  test("toTimeSeriesData", () => {
    expect(toTimeSeriesData({ value: 3, timestamp })).toEqual([timestamp, 3]);
  });

  test("logToSeries converts timestamps to dates", () => {
    const log = [{ timestamp: timestamp.toISOString(), power: 10 }];

    expect(logToSeries(log, "power")).toEqual([[timestamp, 10]]);
    expect(logToSeries(undefined, "timestamp")).toEqual([]);
  });
});

describe("entries", () => {
  test("isEntry matches pairs only", () => {
    expect(isEntry(["a", 1])).toBe(true);
    expect(isEntry(["a"])).toBe(false);
  });

  test("entriesOf handles every input type", () => {
    expect(entriesOf([["a", 1]])).toEqual([["a", 1]]);
    expect(entriesOf(["a", "b"])).toEqual([["a"], ["b"]]);
    expect(entriesOf({ a: 1 })).toEqual([["a", 1]]);
    expect(entriesOf(new Map([["a", new Map([["b", 1]])]]))).toEqual([["a", [["b", 1]]]]);
  });

  test("toEntries and toRecord map the values", () => {
    expect(toEntries(["a", "b"], (key) => key.toUpperCase())).toEqual([
      ["a", "A"],
      ["b", "B"],
    ]);
    expect(toRecord({ a: 1, b: 2 }, (_key, value) => value * 10)).toEqual({ a: 10, b: 20 });
  });

  test("keysOf", () => {
    expect(keysOf({ a: 1, b: 2 })).toEqual(["a", "b"]);
    expect(keysOf(undefined)).toBeUndefined();
  });
});

describe("numbers", () => {
  test("mmath", () => {
    expect(mmath.avg(1, 2, 6)).toBe(3);
    expect(mmath.normalizeDegrees(-90)).toBe(270);
    expect(mmath.normalizeDegrees(450)).toBe(90);
  });

  test("useFixed splits the integer and fraction digits", () => {
    const value = ref<number | undefined>(3.14159);

    expect(useFixed(value, 2).value).toEqual([3, [1, 4]]);
    expect(useFixed(value, 0).value).toEqual([3, undefined]);

    value.value = undefined;
    expect(useFixed(value, 2).value).toEqual([undefined, undefined]);
  });
});

describe("misc", () => {
  test("generateRandomId uses the prefix", () => {
    expect(generateRandomId("tooltip")).toMatch(/^tooltip-[a-z0-9]+$/);
  });

  test("extractProperty", () => {
    expect([{ id: 1 }, { id: 2 }].map(extractProperty("id"))).toEqual([1, 2]);
  });
});
