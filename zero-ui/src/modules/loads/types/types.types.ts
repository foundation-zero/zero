import { Nullable } from "@/modules/common/types";
import { SailId } from "../lib/consts.sails";
import { PositionId, VariableUnit } from "./types.consts";

export type ReferenceThresholds = {
  warningLow?: number;
  warningHigh?: number;
  alarmLow?: number;
  alarmHigh?: number;
  target?: Nullable<number>;
};

export type VariableUnitMap = {
  [VariableUnit.Tonne]: number;
  [VariableUnit.Ratio]: number;
  [VariableUnit.Bool]: boolean;
};

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
  unit: VariableUnit;
  active: boolean | null;
  actualValue: number | null;
  thresholdValue: number | null;
  actual: {
    variable: {
      id: string;
    };
  };
};
