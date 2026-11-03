import { ENV } from "@/settings";
import { Client, fetchExchange, OperationResult } from "@urql/vue";
import { describe, expect, test } from "vitest";
import { VARIABLE_ACTUALS, VARIABLE_DEFINITIONS } from "../graphql/queries/variables";
import { RIG_COLUMNS } from "../lib/consts";
import { QueryVariableActual, QueryVariableDefinition } from "../types";

const client = new Client({
  url: ENV.VITE_LOADS_API_SERVER,
  exchanges: [fetchExchange],
});

let _definitions: OperationResult<QueryVariableDefinition>;

const getDefinitions = async () =>
  (_definitions ??= await client.query<QueryVariableDefinition>(VARIABLE_DEFINITIONS, {}));

const getDefinedIds = async () => {
  const definitions = await getDefinitions();
  return definitions.data?.variables.map((v) => v.id) ?? [];
};

let _actuals: OperationResult<QueryVariableActual>;

const getActuals = async (variables: string[]) =>
  (_actuals ??= await client.query<QueryVariableActual>(VARIABLE_ACTUALS, { variables }));

const usedVariables = Array.from(
  new Set(
    RIG_COLUMNS.flatMap((column) =>
      column.cards.flatMap((card) => card.rows.flatMap((row) => row.variableIds)),
    ),
  ),
).sort();

describe("Rig API", () => {
  describe("Definitions", () => {
    test("query does not return errors", async () => {
      const definitions = await getDefinitions();

      expect(definitions.error).toBeUndefined();
    });

    test.each(usedVariables)(`variable '%s' is defined`, async (variable) => {
      expect(await getDefinedIds()).toContain(variable);
    });
  });

  describe("Actuals", () => {
    test("query does not return errors", async () => {
      const actuals = await getActuals(usedVariables);

      expect(actuals.error).toBeUndefined();
    });

    test("query returns every requested variable", async () => {
      const actuals = await getActuals(usedVariables);

      expect(actuals.data?.variables.map((v) => v.id).sort()).toEqual(usedVariables);
    });
  });
});
