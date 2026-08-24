import { SailId } from "../lib/consts.sails";

export type ReferenceThresholds = {
  warningLow?: number;
  warningHigh?: number;
  alarmLow?: number;
  alarmHigh?: number;
  target: number;
};

export const enum VariableUnit {
  Ratio = "ratio",
  Tonne = "tonne",
  Bool = "bool",
  Mm = "mm",
  Meter = "m",
  Knots = "knots",
  Degrees = "degrees",
  MicroMeterPerMeter = "um/m",
  DegreeCelsius = "degC",
  TonneMeter = "T.m",
  Percent = "%",
}

export type VariableUnitMap = {
  [VariableUnit.Tonne]: number;
  [VariableUnit.Ratio]: number;
  [VariableUnit.Bool]: boolean;
};

export const enum AWA {
  Upwind = "upwind",
  Reaching = "reaching",
  Downwind = "downwind",
}

export const enum VariableState {
  Neutral = "neutral",
  Warning = "warning",
  Alarm = "alarm",
  Unknown = "unknown",
}

export type NumRangeId = `${string}_${number}_${number | ""}`;

export type Range<Id extends string = NumRangeId> = {
  id: Id;
  name?: string;
  from: number;
  to: number;
};

export type VariableDefinition = {
  id: string;
  name: string;
  unit: VariableUnit;
  scaleMin: number;
  scaleMax: number;
  scaleMinLabel: Nullable<string>;
  scaleMaxLabel: Nullable<string>;
};

export type Nullable<T> = T | null;

export type VariableActual<T extends number | boolean = number> = {
  id: string;
  value: T;
};

export type VariableReference = ReferenceThresholds;

export type PickChild<T, K1 extends keyof T, K2 extends keyof T[K1]> = {
  [P in K2]: T[K1][P];
};

export type Variable<T extends number | boolean = number> = {
  id: string;
  reference: VariableReference;
  variable: VariableDefinition;
  actual: VariableActual<T>;
};

export type MaybeVariable<T extends number | boolean = number | boolean> = Partial<Variable<T>> &
  Pick<Variable<T>, "id">;

export type CardType = "numerical" | "graphical";

export const enum PositionId {
  Main = "main",
  ForeInner = "fore-inner",
  ForeOuter = "fore-outer",
  Mizzen = "mizzen",
  MizzenFore = "mizzen-fore",
}

export type SailPositionGroup = {
  name: string;
  positions: SailPosition[];
};

export type SailPosition = {
  sails: Sail<SailId>[];
  position: PositionId;
};

export type Sail<SailId extends string = string> = {
  name: string;
  id: SailId;
  abbreviation: string;
  positionId: PositionId;
  variantName: string;
};

export type MastLock = {
  id: string;
  name: string;
  locked: MastLockState;
  overhoist: MastLockState;
};

export type SailSelection = Record<PositionId, SailId | null>;

export type MastLockState = boolean | "error";

export type Alarm = {
  id: string;
  name: string;
  active: boolean | null;
  actualValue: number | null;
  thresholdValue: number | null;
  actual: {
    variable: {
      unit: VariableUnit;
    };
  };
};
