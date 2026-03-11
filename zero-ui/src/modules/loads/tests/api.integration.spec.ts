import { ENV } from "@/settings";
import { Client, fetchExchange, OperationResult } from "@urql/vue";
import { describe, expect, test } from "vitest";
import { VARIABLE_ACTUALS, VARIABLE_DEFINITIONS } from "../graphql/queries/variables";
import { AWA_VALUES, AWS_VALUES } from "../lib/consts";
import { DASHBOARDS } from "../lib/consts.dashboards";
import { SailId } from "../lib/consts.sails";
import { AWA, NumRangeId } from "../types";
import {
  QueryVariableActual,
  QueryVariableDefinition,
  QueryVariableReference,
} from "../types/queries";

const client = new Client({
  url: ENV.VITE_LOADS_API_SERVER,
  exchanges: [fetchExchange],
  fetchOptions: {},
});

export default client;

let _definitions: OperationResult<QueryVariableDefinition>;

const getDefinitions = async () => {
  return (_definitions ??= await client.query<QueryVariableDefinition>(VARIABLE_DEFINITIONS, {}));
};

const getVariables = async () => {
  const definitions = await getDefinitions();
  return definitions.data?.variables ?? [];
};

const getVariableIds = async () => {
  const variables = await getVariables();
  return variables.map((v) => v.id) ?? [];
};

let _actuals: OperationResult<QueryVariableActual>;

const getActuals = async (variables: string[]) => {
  return (_actuals ??= await client.query<QueryVariableActual>(VARIABLE_ACTUALS, { variables }));
};

let _referenceValues: OperationResult<QueryVariableReference>;

const getReferenceValues = async (
  variables: string[],
  sailset: SailId[],
  awaRange: AWA = AWA_VALUES[0].id,
  awsRange: NumRangeId = AWS_VALUES[0].id,
) => {
  return (_referenceValues ??= await client.query<QueryVariableReference>(VARIABLE_ACTUALS, {
    variables,
    sailset,
    awaRange,
    awsRange,
  }));
};

describe("Loads API", () => {
  describe("Definitions", () => {
    test("query does not return errors", async () => {
      const definitions = await getDefinitions();

      expect(definitions.error).toBeUndefined();
    });

    test("query returns data", async () => {
      const definitions = await getDefinitions();

      expect(definitions.data).toBeDefined();
      expect(definitions.data?.variables).toBeInstanceOf(Array);
      expect(definitions.data?.variables.length).toBeGreaterThan(0);
    });
  });

  const usedVariables = Array.from(
    new Set(DASHBOARDS.flatMap((d) => d.groups.flatMap((g) => g.variables))),
  ).sort();

  describe("Dashboards", () => {
    test.each(usedVariables)(`variable '%s' is defined`, async (variable) => {
      const variables = await getVariableIds();

      expect(variables).toContain(variable);
    });
  });

  describe("Actuals", () => {
    test("query does not return errors", async () => {
      const actuals = await getActuals(usedVariables);

      expect(actuals.error).toBeUndefined();
    });

    test("query returns data", async () => {
      const actuals = await getActuals(usedVariables);

      expect(actuals.data).toBeDefined();
      expect(actuals.data?.variables).toBeInstanceOf(Array);
      expect(actuals.data?.variables.length).toEqual(usedVariables.length);
    });
  });

  describe("Reference values", () => {
    test("query does not return errors", async () => {
      const referenceValues = await getReferenceValues(usedVariables, [SailId.FullMain]);

      expect(referenceValues.error).toBeUndefined();
    });

    test("query returns data", async () => {
      const referenceValues = await getReferenceValues(usedVariables, [SailId.FullMain]);

      expect(referenceValues.data).toBeDefined();
      expect(referenceValues.data?.variables).toBeInstanceOf(Array);
      expect(referenceValues.data?.variables.length).toEqual(usedVariables.length);
    });
  });
});
