import { ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import type {
  LatestValueRow,
  MonitoringAnnotation,
  ResolvedRange,
  StateTotal,
  StyledSegment,
  TrendBand,
  TrendLimit,
  TrendLine,
} from "./monitoring.types";

const MINUTE = 60_000;
const START = new Date(2026, 10, 10, 13, 0).getTime();

/** 13:00 – 17:00, as in the mockup. */
export const MOCK_RANGE: ResolvedRange = { start: START, end: START + 240 * MINUTE };

const at = (minutes: number) => START + minutes * MINUTE;

type Piece = [state: string, label: string, mode: ModeBadgeMode, from: number, to: number];

const segments = (pieces: Piece[]): StyledSegment[] =>
  pieces.map(([state, label, mode, from, to]) => ({
    state,
    label,
    mode,
    start: at(from),
    end: at(to),
  }));

export const MOCK_BOOSTING = segments([
  ["boosting_high_temperature", "Boosting HT", ModeBadgeMode.Boosting, 0, 32],
  ["idle", "Idle", ModeBadgeMode.Idle, 32, 46],
  ["boosting_heatpump", "Boosting HP", ModeBadgeMode.BoostingHigh, 46, 78],
  ["idle", "Idle", ModeBadgeMode.Idle, 78, 92],
  ["manual", "Manual", ModeBadgeMode.ManualControl, 92, 124],
  ["idle", "Idle", ModeBadgeMode.Idle, 124, 240],
]);

export const MOCK_FILLING = segments([
  ["filling", "Filling", ModeBadgeMode.Filling, 0, 18],
  ["idle", "Idle", ModeBadgeMode.Idle, 18, 26],
  ["filling", "Filling", ModeBadgeMode.Filling, 26, 44],
  ["idle", "Idle", ModeBadgeMode.Idle, 44, 52],
  ["filling", "Filling", ModeBadgeMode.Filling, 52, 124],
  ["idle", "Idle", ModeBadgeMode.Idle, 124, 240],
]);

export const MOCK_TANKS = [
  segments([
    ["boosting", "Boosting", ModeBadgeMode.Boosting, 0, 30],
    ["in use", "In use", ModeBadgeMode.Using, 30, 240],
  ]),
  segments([
    ["filling", "Filling", ModeBadgeMode.Filling, 0, 18],
    ["standby", "Standby", ModeBadgeMode.Idle, 18, 48],
    ["boosting", "Boosting", ModeBadgeMode.Boosting, 48, 80],
    ["standby", "Standby", ModeBadgeMode.Idle, 80, 112],
    ["needs boost", "Needs boost", ModeBadgeMode.BoostingLow, 112, 128],
    ["standby", "Standby", ModeBadgeMode.Idle, 128, 240],
  ]),
  segments([
    ["standby", "Standby", ModeBadgeMode.Idle, 0, 90],
    ["needs fill", "Needs fill", ModeBadgeMode.FillingLow, 90, 106],
    ["standby", "Standby", ModeBadgeMode.Idle, 106, 124],
    ["filling", "Filling", ModeBadgeMode.Filling, 124, 240],
  ]),
];

const totals = (pieces: StyledSegment[]): StateTotal[] =>
  Object.values(
    pieces.reduce<Record<string, StateTotal>>((sum, { state, label, mode, start, end }) => {
      const seconds = (sum[state]?.seconds ?? 0) + (end - start) / 1000;
      return { ...sum, [state]: { state, label, mode, seconds } };
    }, {}),
  );

export const MOCK_BOOSTING_TOTALS = totals(MOCK_BOOSTING);
export const MOCK_TANK_TOTALS = totals(MOCK_TANKS.flat());

export const MOCK_BANDS: TrendBand[] = MOCK_BOOSTING.map(({ label, mode, start, end }) => ({
  label,
  mode,
  start,
  end,
}));

const curve = (offset: number, base: number, rise: number) =>
  Array.from({ length: 241 }, (_, minute): [number, number] => {
    const heated = Math.min(Math.max((minute - offset) / 40, 0), 1);
    return [at(minute), base + rise * heated - 0.004 * Math.max(minute - offset - 40, 0)];
  });

export const MOCK_TANK_TEMPERATURES: TrendLine[] = [
  { name: "[50001038-45] dhw-temperature-tank1", points: curve(0, 48, 18) },
  { name: "[50001038-44] dhw-temperature-tank2", points: curve(50, 46, 19) },
  { name: "[50001038-27] dhw-temperature-tank3", points: curve(90, 41, 22) },
];

export const MOCK_TEMPERATURE_LIMITS: { lower: TrendLimit; upper: TrendLimit } = {
  lower: {
    name: "Minimum temperature",
    points: [
      [at(0), 51],
      [at(240), 51],
    ],
  },
  upper: {
    name: "Maximum temperature",
    points: [
      [at(0), 65],
      [at(150), 67],
      [at(240), 67],
    ],
  },
};

export const MOCK_MANY_SENSORS: TrendLine[] = Array.from({ length: 10 }, (_, index) => ({
  name: `dhw-temperature-${index + 1}`,
  points: curve(index * 15, 30 + index * 3, 10),
}));

export const MOCK_WITH_GAP: TrendLine[] = [
  {
    name: "[50001097-11] dhw-pressure",
    points: [
      ...Array.from({ length: 80 }, (_, minute): [number, number] => [
        at(minute),
        2.1 + 0.05 * Math.sin(minute / 6),
      ]),
      [at(80) + 1, null],
      ...Array.from({ length: 100 }, (_, index): [number, number] => {
        const minute = index + 140;
        return [at(minute), 2.2 + 0.05 * Math.sin(minute / 6)];
      }),
    ],
  },
];

export const MOCK_LEVELS: LatestValueRow[] = [
  { asset: "Tank 1", value: 212.4, timestamp: Date.now() - 4_000 },
  { asset: "Tank 2", value: 101.25, timestamp: Date.now() - 8_000 },
  { asset: "Tank 3", value: 79, timestamp: Date.now() - 600_000 },
];

/** A crew note, a parameter change and an alarm across the mock range. */
export const MOCK_ANNOTATIONS: MonitoringAnnotation[] = [
  {
    id: "note",
    kind: "CREW",
    time: new Date(at(50)).toISOString(),
    text: "Swapped the tank 2 temperature sensor",
    author: "Erik",
    canDelete: true,
    changes: [],
  },
  {
    id: "parameters",
    kind: "PARAMETERS",
    time: new Date(at(120)).toISOString(),
    text: "minimum_tank_temperature",
    author: null,
    canDelete: false,
    changes: [{ name: "minimum_tank_temperature", previous: "55", value: "40" }],
  },
  {
    id: "alarm",
    kind: "ALARM",
    time: new Date(at(190)).toISOString(),
    text: "raised",
    author: null,
    canDelete: false,
    changes: [],
  },
];
