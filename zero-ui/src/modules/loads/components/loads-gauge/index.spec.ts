import { describe, expect, test } from "vitest";
import { ref } from "vue";
import {
  AMOUNT_OF_POINTS_PER_SIDE,
  ANGLE_STEP,
  Colors,
  createPoints,
  getTickColor,
  getTicks,
  POINT_ARC_RADIUS,
  START_ANGLE,
  TOTAL_AMOUNT_OF_POINTS,
  type GaugeStep,
} from ".";

const makeTick = (index: number, color: Colors): GaugeStep => ({
  x: 0,
  y: 0,
  angleInRadians: 0,
  angle: START_ANGLE + ANGLE_STEP * index,
  value: index,
  color,
});

describe("getTickColor", () => {
  describe("symmetric gauge", () => {
    const colorAt = getTickColor(2, 2, [8, 12], [9.5, 10.5], [9, 11]);

    test("returns transparent for ticks outside visible range", () => {
      expect(colorAt(10, 10)).toBe(Colors.Transparent);
      expect(colorAt(16, 10)).toBe(Colors.Transparent);
    });

    test("returns target for the exact target value", () => {
      expect(colorAt(13, 10)).toBe(Colors.Target);
    });

    test("returns empty when value is outside fill range", () => {
      expect(colorAt(13, 7)).toBe(Colors.Empty);
    });

    test("returns target for values inside target range (inclusive)", () => {
      expect(colorAt(13, 9.5)).toBe(Colors.Target);
      expect(colorAt(13, 10.5)).toBe(Colors.Target);
    });

    test("returns warning for values in warning range but outside target range", () => {
      expect(colorAt(13, 9)).toBe(Colors.Warning);
      expect(colorAt(13, 11)).toBe(Colors.Warning);
    });

    test("returns destructive for values outside target and warning", () => {
      expect(colorAt(13, 8.5)).toBe(Colors.Destructive);
    });
  });

  describe("asymmetric gauge", () => {
    const colorAt = getTickColor(4, 1, [9, 16], [11, 13], [10, 14]);

    test("uses asymmetric visibility bounds for left and right sides", () => {
      expect(colorAt(8, 12)).toBe(Colors.Transparent);
      expect(colorAt(17, 12)).toBe(Colors.Transparent);
      expect(colorAt(9, 12)).toBe(Colors.Target);
      expect(colorAt(14, 12)).toBe(Colors.Target);
    });
  });
});

describe("createPoints", () => {
  describe("edge cases", () => {
    test("returns fallback ticks when scale collapses to one value", () => {
      const points = createPoints([10, 10], [10, 10], [10, 10], 10, ref(10));

      expect(points).toHaveLength(TOTAL_AMOUNT_OF_POINTS);
      expect(points.every((point) => point.value === 10)).toBe(true);
      expect(points[AMOUNT_OF_POINTS_PER_SIDE].color).toBe(Colors.Target);
      expect(points[0].color).toBe(Colors.Empty);
      expect(points[TOTAL_AMOUNT_OF_POINTS - 1].color).toBe(Colors.Empty);
    });

    test("returns fallback ticks when computed step size is non-finite", () => {
      const points = createPoints([0, Number.POSITIVE_INFINITY], [0, 0], [0, 0], 0, ref(0));

      expect(points).toHaveLength(TOTAL_AMOUNT_OF_POINTS);
      expect(points.every((point) => point.value === 0)).toBe(true);
    });
  });

  describe("symmetric gauge", () => {
    const createSymmetricPoints = () => createPoints([0, 20], [9, 11], [8, 12], 10, ref(12));

    test("keeps all ticks visible when target sits in the middle of scale", () => {
      const points = createSymmetricPoints();

      expect(points).toHaveLength(TOTAL_AMOUNT_OF_POINTS);
      expect(points.some((point) => point.color === Colors.Transparent)).toBe(false);
      expect(points[AMOUNT_OF_POINTS_PER_SIDE].value).toBeCloseTo(10, 6);
    });
  });

  describe("asymmetric gauge", () => {
    const createAsymmetricPoints = () => createPoints([0, 20], [13, 15], [12, 16], 14, ref(17));

    test("creates a full point set and keeps target at center index", () => {
      const points = createAsymmetricPoints();

      expect(points).toHaveLength(TOTAL_AMOUNT_OF_POINTS);
      expect(points[AMOUNT_OF_POINTS_PER_SIDE].value).toBeCloseTo(14, 6);
    });

    test("assigns angles across the configured semicircle", () => {
      const points = createAsymmetricPoints();

      expect(points[0].angle).toBe(START_ANGLE);
      expect(points[TOTAL_AMOUNT_OF_POINTS - 1].angle).toBe(START_ANGLE + ANGLE_STEP * 26);
      expect(points.every((point) => point.angle >= START_ANGLE)).toBe(true);
      expect(points.every((point) => point.angle <= START_ANGLE + ANGLE_STEP * 26)).toBe(true);
      expect(points.every((point) => point.angleInRadians >= Math.PI)).toBe(true);
      expect(points.every((point) => point.angleInRadians <= Math.PI * 2)).toBe(true);
    });

    test("places all points on the point arc radius", () => {
      const points = createAsymmetricPoints();

      expect(points.every((point) => Number.isFinite(point.x) && Number.isFinite(point.y))).toBe(
        true,
      );
      expect(
        points.every(
          (point) =>
            Math.abs(Math.hypot(point.x - 160, point.y - 178) - POINT_ARC_RADIUS) < 0.000001,
        ),
      ).toBe(true);
    });

    test("contains both visible and hidden ticks based on asymmetric range", () => {
      const points = createAsymmetricPoints();

      expect(points.some((point) => point.color === Colors.Transparent)).toBe(true);
      expect(points.some((point) => point.color === Colors.Target)).toBe(true);
    });
  });
});

describe("getTicks", () => {
  test("returns empty array when all ticks are transparent", () => {
    const ticks = Array.from({ length: TOTAL_AMOUNT_OF_POINTS }, (_, index) =>
      makeTick(index, Colors.Transparent),
    );

    expect(getTicks(ticks)).toEqual([]);
  });

  describe("asymmetric gauge", () => {
    test("adds center/opposite helper ticks when offset to middle is large", () => {
      const ticks = Array.from({ length: TOTAL_AMOUNT_OF_POINTS }, (_, index) =>
        makeTick(index, Colors.Transparent),
      );

      ticks[0] = makeTick(0, Colors.Empty);
      ticks[26] = makeTick(26, Colors.Empty);

      expect(getTicks(ticks).map((tick) => tick.value)).toEqual([0, 26, 20, 6]);
    });
  });

  describe("symmetric gauge", () => {
    test("keeps balanced label placement using opposite outer tick", () => {
      const ticks = Array.from({ length: TOTAL_AMOUNT_OF_POINTS }, (_, index) =>
        makeTick(index, Colors.Transparent),
      );

      ticks[10] = makeTick(10, Colors.Empty);
      ticks[20] = makeTick(20, Colors.Empty);

      expect(getTicks(ticks).map((tick) => tick.value)).toEqual([10, 20, 16]);
    });
  });
});
