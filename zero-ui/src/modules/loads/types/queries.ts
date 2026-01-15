import { Variable } from ".";

export type QueryVariables<T extends keyof Variable> = {
  variables: Pick<Variable, "id" | T>[];
};

export type QueryVariableActual = QueryVariables<"actual">;
export type QueryVariableDefinition = QueryVariables<"variable">;
export type QueryVariableReference = QueryVariables<"reference">;
