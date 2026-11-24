const CIRCUMFERENCE = 2 * Math.PI * 40;

// A gap in the ring's units between arcs, so neighbouring states don't blur together.
const GAP = 1.2;

/** Dash settings that draw each value as an arc of a ring of radius 40. */
export function donutArcs(values: number[]): { dasharray: string; dashoffset: number }[] {
  const total = values.reduce((sum, value) => sum + value, 0);
  if (total <= 0) return [];
  const gap = values.length > 1 ? GAP : 0;

  return values.map((value, index) => {
    const before = values.slice(0, index).reduce((sum, previous) => sum + previous, 0);
    const length = Math.max((value / total) * CIRCUMFERENCE - gap, 0.01);
    return {
      dasharray: `${length} ${CIRCUMFERENCE - length}`,
      dashoffset: -(before / total) * CIRCUMFERENCE,
    };
  });
}
