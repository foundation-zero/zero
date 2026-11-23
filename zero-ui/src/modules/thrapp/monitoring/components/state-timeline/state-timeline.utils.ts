import type { ResolvedRange, StyledSegment } from "@/modules/thrapp/monitoring/monitoring.types";

export type PlacedSegment = StyledSegment & { left: number; width: number };

/** Position segments as percentages of the range, clipped to it. */
export function placeSegments(segments: StyledSegment[], range: ResolvedRange): PlacedSegment[] {
  const span = range.end - range.start;
  return segments.flatMap((segment) => {
    const start = Math.max(segment.start, range.start);
    const end = Math.min(segment.end, range.end);
    if (end <= start) return [];
    return [
      {
        ...segment,
        left: ((start - range.start) / span) * 100,
        width: ((end - start) / span) * 100,
      },
    ];
  });
}

// About the width of one character of the 14px label font, plus the padding.
const CHARACTER_WIDTH = 8.5;
const PADDING = 16;

/** Whether a label fits in a segment this many pixels wide. */
export const fitsLabel = (label: string, widthPx: number) =>
  label.length * CHARACTER_WIDTH + PADDING <= widthPx;
