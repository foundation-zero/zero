export type ReferenceThresholds = {
  warningLow: number;
  warningHigh: number;
  alarmLow: number;
  alarmHigh: number;
  target: number;
};

export const enum VariableUnit {
  Percentage = "percentage",
  Tonne = "tonne",
  OnOff = "on-off",
}

export const enum VariableState {
  Neutral = "neutral",
  Warning = "warning",
  Alarm = "alarm",
  Unknown = "unknown",
}

export type NumRangeId = `[${number},${number | ""})`;

export type Range = {
  id: NumRangeId;
  from: number;
  to: number;
};

export type VariableDef = {
  id: string;
  name: string;
  unit: VariableUnit;
};

export type VariableActual<T extends number | boolean = number> = {
  id: string;
  value: T;
};

export type VariableReference = {
  reference?: Partial<ReferenceThresholds>;
  variable: VariableDef;
};

export type PickChild<T, K1 extends keyof T, K2 extends keyof T[K1]> = {
  [P in K2]: T[K1][P];
};

export type Variable<T extends number | boolean = number> = {
  id: string;
  reference: VariableReference;
  actual: VariableActual<T>;
};

export type QueryVariableActual = Pick<Variable, "id" | "actual">;
export type QueryVariableDefinition = Pick<Variable, "id"> &
  PickChild<Variable, "reference", "variable">;
export type QueryVariableReference = Pick<Variable, "id"> &
  PickChild<Variable, "reference", "reference">;

export type CardType = "numerical" | "graphical";

export type SailPosition = {
  name: string;
  groups: SailGroup[];
};

export type SailGroup = {
  sails: Sail[];
};

export type Sail = {
  name: string;
  id: string;
};

export type MastLock = {
  id: string;
  name: string;
  locked: MastLockState;
  overhoist: MastLockState;
};

export type MastLockState = boolean | "error";
