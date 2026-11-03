import { Mast, RigCard, RigMast, RigRow, RigTableColumn } from "../types";
import { RigVariableId } from "./consts.variables";
import { getDeflectionDisplayName } from "./utils";

const id = (value: string): RigVariableId => value as RigVariableId;

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

const s9toS1 = (mast: Mast, type: string): RigVariableId[] =>
  Array.from({ length: 9 }, (_, i) => id(`fiber-optic-${mast}-mast-${type}-s${STATIONS[i]}`));

const bendingRows = (mast: Mast): RigRow[] => {
  const momentSide = s9toS1(mast, "bending-moment-side-way");
  const momentForeAft = s9toS1(mast, "bending-moment-fore-aft");
  const strainSide = s9toS1(mast, "bending-strain-side-way");
  const strainForeAft = s9toS1(mast, "bending-strain-fore-aft");
  return STATIONS.map((station, i) => ({
    label: `S${station}`,
    variableIds: [momentSide[i], momentForeAft[i], strainSide[i], strainForeAft[i]],
  }));
};

const sectionStrainRows = (mast: Mast): RigRow[] =>
  STATIONS.map((station) => ({
    label: `S${station}`,
    variableIds: STRAIN_DIRECTIONS.map((direction) =>
      id(`fiber-optic-${mast}-mast-strain-s${station}-${direction}`),
    ),
  }));

const longitudinalRows = (mast: Mast): RigRow[] => {
  const load = s9toS1(mast, "longitudinal-load");
  const strain = s9toS1(mast, "longitudinal-strain");
  return STATIONS.map((station, i) => ({
    label: `S${station}`,
    variableIds: [load[i], strain[i]],
  }));
};

const deflectionRow = (mast: Mast, token: string): RigRow => {
  const foreAft = id(`fiber-optic-${mast}-mast-fa-deflection${token}`);
  const sideWay = id(`fiber-optic-${mast}-mast-sw-deflection${token}`);
  return {
    label: getDeflectionDisplayName(foreAft) ?? "",
    variableIds: [sideWay, foreAft],
  };
};

const mastDeflectionRows = (mast: Mast): RigRow[] =>
  MAST_DEFLECTION_ORDER.map((token) => deflectionRow(mast, token));

const spreaderDeflectionRows = (mast: Mast): RigRow[] =>
  SPREADER_DEFLECTION_ORDER.map((n) => deflectionRow(mast, `-spr${n}`));

const spreaderTempRows = (mast: Mast): RigRow[] => [
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

const riggingRows = (mast: Mast): RigRow[] => [
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

const riggingSumRows = (mast: Mast): RigRow[] =>
  [1, 2, 3, 4].map((v) => ({
    label: `V${v} Sum`,
    variableIds: [
      id(`fiber-optic-${mast}-rigging-sum-load-v${v}-port`),
      id(`fiber-optic-${mast}-rigging-sum-load-v${v}-stbd`),
    ],
  }));

const riggingTempRows = (mast: Mast): RigRow[] => [
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

const card = (titleKey: string, columns: RigTableColumn[], rows: RigRow[]): RigCard => ({
  titleKey,
  columns,
  rows,
});

const mastCards = (mast: Mast): RigCard[] => [
  card(
    "rig.cards.bendingMomentStrain",
    [
      { titleKey: "rig.columns.bendingMomentSideways" },
      { titleKey: "rig.columns.bendingMomentForeAft" },
      { titleKey: "rig.columns.bendingStrainSideways" },
      { titleKey: "rig.columns.bendingStrainForeAft" },
    ],
    bendingRows(mast),
  ),
  card(
    "rig.cards.sectionStrain",
    [
      { titleKey: "rig.columns.fore" },
      { titleKey: "rig.columns.pt" },
      { titleKey: "rig.columns.sb" },
      { titleKey: "rig.columns.ptAft" },
      { titleKey: "rig.columns.sbAft" },
    ],
    sectionStrainRows(mast),
  ),
  card(
    "rig.cards.longitudinalLoadStrain",
    [{ titleKey: "rig.columns.longitudinalLoad" }, { titleKey: "rig.columns.longitudinalStrain" }],
    longitudinalRows(mast),
  ),
  card(
    "rig.cards.mastDeflection",
    [{ titleKey: "rig.columns.sideways" }, { titleKey: "rig.columns.foreAft" }],
    mastDeflectionRows(mast),
  ),
  card(
    "rig.cards.spreaderDeflection",
    [{ titleKey: "rig.columns.sideways" }, { titleKey: "rig.columns.foreAft" }],
    spreaderDeflectionRows(mast),
  ),
  card(
    "rig.cards.riggingLoadStrain",
    [
      { titleKey: "rig.columns.loadPt" },
      { titleKey: "rig.columns.loadSb" },
      { titleKey: "rig.columns.strainPt" },
      { titleKey: "rig.columns.strainSb" },
    ],
    riggingRows(mast),
  ),
  card(
    "rig.cards.riggingSumLoad",
    [{ titleKey: "rig.columns.pt" }, { titleKey: "rig.columns.sb" }],
    riggingSumRows(mast),
  ),
  card(
    "rig.cards.spreaderTemperature",
    [
      { titleKey: "rig.columns.fore" },
      { titleKey: "rig.columns.pt" },
      { titleKey: "rig.columns.sb" },
    ],
    spreaderTempRows(mast),
  ),
  card(
    "rig.cards.riggingTemperature",
    [{ titleKey: "rig.columns.pt" }, { titleKey: "rig.columns.sb" }],
    riggingTempRows(mast),
  ),
];

export const RIG_MASTS: RigMast[] = [
  { titleKey: "rig.columns.mizzenMast", cards: mastCards("mizzen") },
  { titleKey: "rig.columns.mainMast", cards: mastCards("main") },
];
