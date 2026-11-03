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

export type RigColumn = { titleKey: string };

export type RigRow = {
  label?: string;
  variableIds: RigVariableId[];
};

export type RigCard = {
  titleKey: string;
  columns: RigColumn[];
  rows: RigRow[];
};

export type RigMastColumn = {
  titleKey: string;
  cards: RigCard[];
};
