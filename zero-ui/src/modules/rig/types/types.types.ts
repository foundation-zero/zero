import { Nullable } from "@/modules/common/types";
import { RigVariableId } from "../lib/consts.variables";

export type QueryVariableDefinition = {
  variables: {
    id: string;
    variable: { name: Nullable<string>; unit: Nullable<string> };
  }[];
};

export type QueryVariableActual = {
  variables: {
    id: string;
    actual: Nullable<{ value: Nullable<number> }>;
  }[];
};

export type Mast = "main" | "mizzen";

export type RigTableColumn = { titleKey: string };

export type RigRow = {
  label?: string;
  variableIds: RigVariableId[];
};

export type RigCard = {
  titleKey: string;
  columns: RigTableColumn[];
  rows: RigRow[];
};

export type RigMast = {
  titleKey: string;
  cards: RigCard[];
};
