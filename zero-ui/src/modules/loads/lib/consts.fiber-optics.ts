import { VariableId } from "./consts.variables";

export type FiberOpticColumn = { titleKey: string };

export type FiberOpticRow = {
  label?: string;
  variableIds: VariableId[];
};

export type FiberOpticCard = {
  titleKey: string;
  columns: FiberOpticColumn[];
  rows: FiberOpticRow[];
};

export type FiberOpticMastColumn = {
  titleKey: string;
  cards: FiberOpticCard[];
};

export function getDeflectionDisplayName(variableId: string): string | null {
  const height = /-(?:fa|sw)-deflection(\d{3})$/.exec(variableId);
  if (height) return `${Number(height[1])}% Height`;

  const spreader = /-(?:fa|sw)-deflection-spr(\d)$/.exec(variableId);
  if (spreader) return `Spreader ${spreader[1]}`;

  return null;
}

const id = (value: string): VariableId => value as VariableId;

const STRAIN_DIRECTIONS = ["fore", "side-port", "side-stbd", "aft-port", "aft-stbd"] as const;

const MAST_DEFLECTION_ORDER = [
  "100",
  "090",
  "080",
  "070",
  "060",
  "050",
  "040",
  "030",
  "020",
  "010",
  "000",
] as const;

const SPREADER_DEFLECTION_ORDER = ["1", "2", "3", "4", "5"] as const;

const STATIONS = [9, 8, 7, 6, 5, 4, 3, 2, 1] as const;

const s9toS1 = (mast: "main" | "mizzen", type: string): VariableId[] =>
  Array.from({ length: 9 }, (_, i) => id(`fiber-optic-${mast}-mast-${type}-s${STATIONS[i]}`));

const bendingRows = (mast: "main" | "mizzen"): FiberOpticRow[] => {
  const momentSide = s9toS1(mast, "bending-moment-side-way");
  const momentForeAft = s9toS1(mast, "bending-moment-fore-aft");
  const strainSide = s9toS1(mast, "bending-strain-side-way");
  const strainForeAft = s9toS1(mast, "bending-strain-fore-aft");
  return STATIONS.map((station, i) => ({
    label: `S${station}`,
    variableIds: [momentSide[i], momentForeAft[i], strainSide[i], strainForeAft[i]],
  }));
};

const sectionStrainRows = (mast: "main" | "mizzen"): FiberOpticRow[] =>
  STATIONS.map((station) => ({
    label: `S${station}`,
    variableIds: STRAIN_DIRECTIONS.map((direction) =>
      id(`fiber-optic-${mast}-mast-strain-s${station}-${direction}`),
    ),
  }));

const longitudinalRows = (mast: "main" | "mizzen"): FiberOpticRow[] => {
  const load = s9toS1(mast, "longitudinal-load");
  const strain = s9toS1(mast, "longitudinal-strain");
  return STATIONS.map((station, i) => ({
    label: `S${station}`,
    variableIds: [load[i], strain[i]],
  }));
};

const deflectionRow = (mast: "main" | "mizzen", token: string): FiberOpticRow => {
  const foreAft = id(`fiber-optic-${mast}-mast-fa-deflection${token}`);
  const sideWay = id(`fiber-optic-${mast}-mast-sw-deflection${token}`);
  return {
    label: getDeflectionDisplayName(foreAft) ?? "",
    variableIds: [sideWay, foreAft],
  };
};

const mastDeflectionRows = (mast: "main" | "mizzen"): FiberOpticRow[] =>
  MAST_DEFLECTION_ORDER.map((token) => deflectionRow(mast, token));

const spreaderDeflectionRows = (mast: "main" | "mizzen"): FiberOpticRow[] =>
  SPREADER_DEFLECTION_ORDER.map((n) => deflectionRow(mast, `-spr${n}`));

const spreaderTempRows = (mast: "main" | "mizzen"): FiberOpticRow[] => [
  {
    label: "Spreader 0",
    variableIds: [id(`fiber-optic-${mast}-mast-temperature-spr0-port`)],
  },
  {
    label: "Spreader 1",
    variableIds: [
      id(`fiber-optic-${mast}-mast-temperature-spr1-fore`),
      id(`fiber-optic-${mast}-mast-temperature-spr1-port`),
      id(`fiber-optic-${mast}-mast-temperature-spr1-stbd`),
    ],
  },
  {
    label: "Spreader 2",
    variableIds: [
      id(`fiber-optic-${mast}-mast-temperature-spr2-fore`),
      id(`fiber-optic-${mast}-mast-temperature-spr2-port`),
      id(`fiber-optic-${mast}-mast-temperature-spr2-stbd`),
    ],
  },
  {
    label: "Spreader 3",
    variableIds: [
      id(`fiber-optic-${mast}-mast-temperature-spr3-port`),
      id(`fiber-optic-${mast}-mast-temperature-spr3-stbd`),
    ],
  },
  {
    label: "Spreader 4",
    variableIds: [
      id(`fiber-optic-${mast}-mast-temperature-spr4-fore`),
      id(`fiber-optic-${mast}-mast-temperature-spr4-aft-port`),
      id(`fiber-optic-${mast}-mast-temperature-spr4-aft-stbd`),
    ],
  },
  {
    label: "Spreader 5",
    variableIds: [
      id(`fiber-optic-${mast}-mast-temperature-spr5-fore`),
      id(`fiber-optic-${mast}-mast-temperature-spr5-side-port`),
      id(`fiber-optic-${mast}-mast-temperature-spr5-side-stbd`),
    ],
  },
];

const riggingRows = (mast: "main" | "mizzen"): FiberOpticRow[] => [
  {
    label: "D1",
    variableIds: [
      id(`fiber-optic-${mast}-d1-ps`),
      id(`fiber-optic-${mast}-d1-sb`),
      id(`fiber-optic-${mast}-rigging-strain-d1-port`),
      id(`fiber-optic-${mast}-rigging-strain-d1-stbd`),
    ],
  },
  ...[2, 3, 4, 5].map((d) => ({
    label: `D${d}`,
    variableIds: [
      id(`fiber-optic-${mast}-rigging-load-d${d}-port`),
      id(`fiber-optic-${mast}-rigging-load-d${d}-stbd`),
      id(`fiber-optic-${mast}-rigging-strain-d${d}-port`),
      id(`fiber-optic-${mast}-rigging-strain-d${d}-stbd`),
    ],
  })),
  {
    label: "V1",
    variableIds: [
      id(`fiber-optic-${mast}-v1-ps`),
      id(`fiber-optic-${mast}-v1-sb`),
      id(`fiber-optic-${mast}-rigging-strain-v1-port`),
      id(`fiber-optic-${mast}-rigging-strain-v1-stbd`),
    ],
  },
];

const riggingSumRows = (mast: "main" | "mizzen"): FiberOpticRow[] =>
  [1, 2, 3, 4].map((v) => ({
    label: `V${v} Sum`,
    variableIds: [
      id(`fiber-optic-${mast}-rigging-sum-load-v${v}-port`),
      id(`fiber-optic-${mast}-rigging-sum-load-v${v}-stbd`),
    ],
  }));

const riggingTempRows = (mast: "main" | "mizzen"): FiberOpticRow[] => [
  ...[1, 2, 3, 4, 5].map((d) => ({
    label: `D${d}`,
    variableIds: [
      id(`fiber-optic-${mast}-rigging-temperature-d${d}-port`),
      id(`fiber-optic-${mast}-rigging-temperature-d${d}-stbd`),
    ],
  })),
  {
    label: "V1",
    variableIds: [
      id(`fiber-optic-${mast}-rigging-temperature-v1-port`),
      id(`fiber-optic-${mast}-rigging-temperature-v1-stbd`),
    ],
  },
];

const card = (
  titleKey: string,
  columns: FiberOpticColumn[],
  rows: FiberOpticRow[],
): FiberOpticCard => ({ titleKey, columns, rows });

const fiberCards = (mast: "main" | "mizzen"): FiberOpticCard[] => [
  card(
    "loads.fiberOptics.cards.bendingMomentStrain",
    [
      { titleKey: "loads.fiberOptics.columns.bendingMomentSideways" },
      { titleKey: "loads.fiberOptics.columns.bendingMomentForeAft" },
      { titleKey: "loads.fiberOptics.columns.bendingStrainSideways" },
      { titleKey: "loads.fiberOptics.columns.bendingStrainForeAft" },
    ],
    bendingRows(mast),
  ),
  card(
    "loads.fiberOptics.cards.sectionStrain",
    [
      { titleKey: "loads.fiberOptics.columns.fore" },
      { titleKey: "loads.fiberOptics.columns.pt" },
      { titleKey: "loads.fiberOptics.columns.sb" },
      { titleKey: "loads.fiberOptics.columns.ptAft" },
      { titleKey: "loads.fiberOptics.columns.sbAft" },
    ],
    sectionStrainRows(mast),
  ),
  card(
    "loads.fiberOptics.cards.longitudinalLoadStrain",
    [
      { titleKey: "loads.fiberOptics.columns.longitudinalLoad" },
      { titleKey: "loads.fiberOptics.columns.longitudinalStrain" },
    ],
    longitudinalRows(mast),
  ),
  card(
    "loads.fiberOptics.cards.mastDeflection",
    [
      { titleKey: "loads.fiberOptics.columns.sideways" },
      { titleKey: "loads.fiberOptics.columns.foreAft" },
    ],
    mastDeflectionRows(mast),
  ),
  card(
    "loads.fiberOptics.cards.spreaderDeflection",
    [
      { titleKey: "loads.fiberOptics.columns.sideways" },
      { titleKey: "loads.fiberOptics.columns.foreAft" },
    ],
    spreaderDeflectionRows(mast),
  ),
  card(
    "loads.fiberOptics.cards.riggingLoadStrain",
    [
      { titleKey: "loads.fiberOptics.columns.loadPt" },
      { titleKey: "loads.fiberOptics.columns.loadSb" },
      { titleKey: "loads.fiberOptics.columns.strainPt" },
      { titleKey: "loads.fiberOptics.columns.strainSb" },
    ],
    riggingRows(mast),
  ),
  card(
    "loads.fiberOptics.cards.riggingSumLoad",
    [{ titleKey: "loads.fiberOptics.columns.pt" }, { titleKey: "loads.fiberOptics.columns.sb" }],
    riggingSumRows(mast),
  ),
  card(
    "loads.fiberOptics.cards.spreaderTemperature",
    [
      { titleKey: "loads.fiberOptics.columns.fore" },
      { titleKey: "loads.fiberOptics.columns.pt" },
      { titleKey: "loads.fiberOptics.columns.sb" },
    ],
    spreaderTempRows(mast),
  ),
  card(
    "loads.fiberOptics.cards.riggingTemperature",
    [{ titleKey: "loads.fiberOptics.columns.pt" }, { titleKey: "loads.fiberOptics.columns.sb" }],
    riggingTempRows(mast),
  ),
];

export const FIBER_MAIN_CARDS: FiberOpticCard[] = fiberCards("main");

export const FIBER_MIZZEN_CARDS: FiberOpticCard[] = fiberCards("mizzen");

export const FIBER_OPTICS_COLUMNS: FiberOpticMastColumn[] = [
  { titleKey: "loads.fiberOptics.columns.mizzenMast", cards: FIBER_MIZZEN_CARDS },
  { titleKey: "loads.fiberOptics.columns.mainMast", cards: FIBER_MAIN_CARDS },
];
