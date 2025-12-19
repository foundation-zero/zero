import { ReferenceThresholds, Variable, VariableUnit } from "../types";

// This file contains hardcoded variable definitions for now. Will be replaced by graphql data in the future.

export type VariableUnitMap = {
  [VariableUnit.Tonne]: number;
  [VariableUnit.Percentage]: number;
  [VariableUnit.OnOff]: boolean;
};

export const variable = <Unit extends VariableUnit, Value extends VariableUnitMap[Unit]>(
  unit: Unit,
  id: string,
  name: string,
  value: Value,
  reference?: Partial<ReferenceThresholds>,
): Variable<Value> => ({
  id,
  actual: {
    id,
    value,
  },
  reference: {
    variable: {
      id,
      name,
      unit,
    },
    reference,
  },
});

export const tonne = (
  id: string,
  name: string,
  value: number,
  reference?: Partial<ReferenceThresholds>,
) => variable(VariableUnit.Tonne, id, name, value, reference);

export const percentage = (
  id: string,
  name: string,
  value: number,
  reference?: Partial<ReferenceThresholds>,
) => variable(VariableUnit.Percentage, id, name, value, reference);

export const onOff = (
  id: string,
  name: string,
  value: boolean,
  reference?: Partial<ReferenceThresholds>,
) => variable(VariableUnit.OnOff, id, name, value, reference);

export const VARIABLES = [
  tonne("main-sheet-load", "Main Sheet Load", 2.7, { target: 1, alarmHigh: 2.8 }),
  percentage("main-sheet-position", "Main Sheet Position", 0, { target: 0.3, warningLow: 0 }),
  percentage("main-traveler-position", "Main Traveler Position", 0, { target: 0.3, warningLow: 0 }),
  tonne("main-preventer-load", "Main Preventer Load", 1.2, { target: 1.5, alarmHigh: 3.5 }),
  percentage("main-preventer-position", "Main Preventer Position", 0.45),
  tonne("main-vang-load", "Main Vang Load", 1.8, { target: 2.0, alarmHigh: 4.0 }),
  percentage("main-vang-position", "Main Vang Position", 0.52, { target: 0.5, warningLow: 0 }),
  tonne("main-outhaul-load", "Main Outhaul Load", 0.9, { target: 1.0, alarmHigh: 2.5 }),
  percentage("main-outhaul-position", "Main Outhaul Position", 0.68, {
    target: 0.7,
    warningLow: 0,
  }),
  tonne("main-halyard-load", "Main Halyard Load", 3.2, { target: 3.5, alarmHigh: 6.0 }),
  percentage("main-halyard-position", "Main Halyard Position", 0.95, {
    target: 1.0,
    warningLow: 0.8,
  }),
  tonne("main-cunningham-load", "Main Cunningham Load", 0.7, { target: 0.8, alarmHigh: 2.0 }),
  percentage("main-cunningham-position", "Main Cunningham Position", 0.35, {
    target: 0.4,
    warningLow: 0,
  }),
  tonne("main-runner-load-ps", "Main Runner Load Port Side", 2.1, { target: 2.5, alarmHigh: 5.0 }),
  percentage("main-runner-position-ps", "Main Runner Position Port Side", 0.42),
  tonne("main-runner-load-sb", "Main Runner Load Starboard Side", 0.3, {
    target: 2.5,
    alarmHigh: 5.0,
  }),
  percentage("main-runner-position-sb", "Main Runner Position Starboard Side", 0.15),
  tonne("main-checkstay-load-ps", "Main Checkstay Load Port Side", 3.8, {
    target: 3.5,
    alarmHigh: 6.0,
  }),
  tonne("main-checkstay-load-sb", "Main Checkstay Load Starboard Side", 0.8, {
    target: 3.5,
    alarmHigh: 6.0,
  }),
  percentage("main-checkstay-position-sb", "Main Checkstay Position Starboard Side", 0.25),
  tonne("main-checkstay-deflector-load-ps", "Main Checkstay Deflector Load Port Side", 1.3, {
    target: 1.5,
    alarmHigh: 3.0,
  }),
  percentage(
    "main-checkstay-deflector-position-ps",
    "Main Checkstay Deflector Position Port Side",
    0.58,
    { target: 0.6, warningLow: 0 },
  ),
  tonne("main-checkstay-deflector-load-sb", "Main Checkstay Deflector Load Starboard Side", 0.4, {
    target: 1.5,
    alarmHigh: 3.0,
  }),
  percentage(
    "main-checkstay-deflector-position-sb",
    "Main Checkstay Deflector Position Starboard Side",
    0.22,
    { target: 0.6, warningLow: 0 },
  ),
  onOff("main-headboard-lock", "Main Headboard Lock", false),
  onOff("main-headboard-overhoist", "Main Headboard Overhoist", false),
  onOff("main-reef-1-lock", "R1", true),
  onOff("main-reef-1-overhoist", "Main Reef 1 Overhoist", false),
  onOff("main-reef-2-lock", "R2", false),
  onOff("main-reef-2-overhoist", "Main Reef 2 Overhoist", true),
  onOff("main-reef-3-lock", "R3", false),
  onOff("main-reef-3-overhoist", "Main Reef 3 Overhoist", false),
  onOff("main-boom-reef-1-lock", "Main Boom Reef 1 Lock", false),
  onOff("main-boom-reef-1-overhoist", "Main Boom Reef 1 Overhoist", false),
  onOff("main-boom-reef-2-lock", "Main Boom Reef 2 Lock", false),
  onOff("main-boom-reef-2-overhoist", "Main Boom Reef 2 Overhoist", false),
  onOff("main-boom-reef-3-lock", "Main Boom Reef 3 Lock", false),
  onOff("main-boom-reef-3-overhoist", "Main Boom Reef 3 Overhoist", false),
  tonne("mizzen-sheet-load", "Mizzen Sheet Load", 1.5, { target: 1.8, alarmHigh: 3.5 }),
  percentage("mizzen-sheet-position", "Mizzen Sheet Position", 0.38, {
    target: 0.4,
    warningLow: 0,
  }),
  tonne("mizzen-preventer-load", "Mizzen Preventer Load", 0.8),
  tonne("mizzen-vang-load", "Mizzen Vang Load", 1.2, { target: 1.5, alarmHigh: 3.0 }),
  percentage("mizzen-vang-position", "Mizzen Vang Position", 0.48, { target: 0.5, warningLow: 0 }),
  tonne("mizzen-outhaul-load", "Mizzen Outhaul Load", 0.6, { target: 0.8, alarmHigh: 2.0 }),
  percentage("mizzen-outhaul-position", "Mizzen Outhaul Position", 0.72, {
    target: 0.7,
    warningLow: 0,
  }),
  tonne("mizzen-halyard-load", "Mizzen Halyard Load", 2.4, { target: 2.8, alarmHigh: 5.0 }),
  percentage("mizzen-halyard-position", "Mizzen Halyard Position", 0.92, {
    target: 1.0,
    warningLow: 0.8,
  }),
  tonne("mizzen-cunningham-load", "Mizzen Cunningham Load", 0.5, { target: 0.6, alarmHigh: 1.5 }),
  percentage("mizzen-cunningham-position", "Mizzen Cunningham Position", 0.32, {
    target: 0.4,
    warningLow: 0,
  }),
  tonne("mizzen-runner-load-ps", "Mizzen Runner Load Port Side", 1.6, {
    target: 2.0,
    alarmHigh: 4.0,
  }),
  percentage("mizzen-runner-position-ps", "Mizzen Runner Position Port Side", 0.55),
  tonne("mizzen-runner-load-sb", "Mizzen Runner Load Starboard Side", 0.4, {
    target: 2.0,
    alarmHigh: 4.0,
  }),
  percentage("mizzen-runner-position-sb", "Mizzen Runner Position Starboard Side", 0.18),
  tonne("mizzen-checkstay-load-ps", "Mizzen Checkstay Load Port Side", 2.8, {
    target: 2.5,
    alarmHigh: 5.0,
  }),
  percentage("mizzen-checkstay-position-ps", "Mizzen Checkstay Position Port Side", 0.62),
  tonne("mizzen-checkstay-load-sb", "Mizzen Checkstay Load Starboard Side", 0.6, {
    target: 2.5,
    alarmHigh: 5.0,
  }),
  percentage("mizzen-checkstay-position-sb", "Mizzen Checkstay Position Starboard Side", 0.28),
  tonne("mizzen-checkstay-deflector-load-ps", "Mizzen Checkstay Deflector Load Port Side", 0.9, {
    target: 1.2,
    alarmHigh: 2.5,
  }),
  percentage(
    "mizzen-checkstay-deflector-position-ps",
    "Mizzen Checkstay Deflector Position Port Side",
    0.48,
    { target: 0.5, warningLow: 0 },
  ),
  tonne(
    "mizzen-checkstay-deflector-load-sb",
    "Mizzen Checkstay Deflector Load Starboard Side",
    0.3,
    {
      target: 1.2,
      alarmHigh: 2.5,
    },
  ),
  percentage(
    "mizzen-checkstay-deflector-position-sb",
    "Mizzen Checkstay Deflector Position Starboard Side",
    0.19,
    { target: 0.5, warningLow: 0 },
  ),
  onOff("mizzen-headboard-lock", "Mizzen Headboard Lock", false),
  onOff("mizzen-headboard-overhoist", "Mizzen Headboard Overhoist", false),
  onOff("mizzen-reef-1-lock", "Mizzen Reef 1 Lock", false),
  onOff("mizzen-reef-1-overhoist", "Mizzen Reef 1 Overhoist", false),
  onOff("mizzen-reef-2-lock", "Mizzen Reef 2 Lock", false),
  onOff("mizzen-reef-2-overhoist", "Mizzen Reef 2 Overhoist", false),
  onOff("mizzen-boom-reef-1-lock", "Mizzen Boom Reef 1 Lock", false),
  onOff("mizzen-boom-reef-1-overhoist", "Mizzen Boom Reef 1 Overhoist", false),
  onOff("mizzen-boom-reef-2-lock", "Mizzen Boom Reef 2 Lock", false),
  onOff("mizzen-boom-reef-2-overhoist", "Mizzen Boom Reef 2 Overhoist", false),
  tonne("vang-load", "Vang Load", -3.4, { target: 0.5, alarmLow: 0 }),
  percentage("vang-position", "Vang Position", 0, { target: 0.3, warningLow: 0 }),
  tonne("outhaul-load", "Outhaul Load", 0.8, { target: 1, alarmHigh: 2.8 }),
  percentage("outhaul-position", "Outhaul Position", 0.65, { target: 0.7, warningLow: 0 }),
  tonne("cunningham-load", "Cunningham Load", 1, { target: 1, alarmHigh: 2.8 }),
  percentage("cunningham-position", "Cunningham Position", 0.69, {
    target: 0.7,
    warningLow: 0,
  }),
  tonne("halyard-load", "Halyard Load", 1, { target: 1, alarmHigh: 2.8 }),
  tonne("runner-ps-load", "Runner PS Load", 0.5, { target: 1, alarmHigh: 2.8 }),
  tonne("runner-sb-load", "Runner SB Load", 0.6, { target: 1, alarmHigh: 2.8 }),
  tonne("checkstay-ps-load", "Checkstay PS Load", 4.2, { target: 3, alarmHigh: 5 }),
  tonne("checkstay-sb-load", "Checkstay SB Load", 4.0, { target: 3, alarmHigh: 5 }),
  tonne("checkstay-deflector-ps-load", "Checkstay Deflector PS Load", 1.5, {
    target: 1,
    alarmHigh: 2.8,
  }),
  percentage("checkstay-deflector-ps-position", "Checkstay Deflector PS Position", 0.3, {
    target: 0.5,
    warningLow: 0,
  }),
  tonne("checkstay-deflector-sb-load", "Checkstay Deflector SB Load", 1.4, {
    target: 1,
    alarmHigh: 2.8,
  }),
  percentage("checkstay-deflector-sb-position", "Checkstay Deflector SB Position", 0.6, {
    target: 0.5,
    warningLow: 0,
  }),
];
