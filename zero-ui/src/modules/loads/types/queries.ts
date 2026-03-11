import { Alarm, Sail, Variable } from ".";
import { SailId } from "../lib/consts.sails";

export type QueryVariables<T extends keyof Variable> = {
  variables: Pick<Variable, "id" | T>[];
};

export type QueryVariableActual = QueryVariables<"actual">;
export type QueryVariableDefinition = QueryVariables<"variable">;
export type QueryVariableReference = QueryVariables<"reference">;

export type QuerySails = {
  sails: Sail<SailId>[];
};

export type QueryAlarms = {
  alarms: Alarm[];
};
