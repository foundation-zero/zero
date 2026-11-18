import { CONTROLLED_MODULES } from "@/modules/thrapp/lib/consts";
import { MQTT_GRAPHQL_DEFINITIONS } from "@/modules/thrapp/lib/definitions.generated";
import * as Fragments from "@/modules/thrapp/lib/mqtt-graphql-queries.generated";
import { valueAt } from "@/modules/thrapp/lib/mqtt-graphql.utils";
import { CONTROL_QUERY, ControlResponse } from "@/modules/thrapp/stores/automation";
import { ENV } from "@/settings";
import { Client, fetchExchange, gql, OperationResult } from "@urql/vue";
import { describe, expect, test } from "vitest";

const client = new Client({
  url: `${ENV.VITE_MQTT_GRAPHQL_API_SERVER}/graphql`,
  exchanges: [fetchExchange],
});

// Every generated fragment spread in one query, as the views spread the ones they show.
const FRAGMENTS = Object.values(Fragments);
const FRAGMENT_NAMES = FRAGMENTS.map((fragment) => /fragment (\w+) on/.exec(fragment)![1]);
const ALL_FRAGMENTS_QUERY = gql`
  query AllFragments {
    ${FRAGMENT_NAMES.map((name) => `...${name}`).join("\n")}
  }
  ${FRAGMENTS.join("\n")}
`;

const DEFINITIONS = MQTT_GRAPHQL_DEFINITIONS as Record<
  string,
  Record<string, Record<string, { path: readonly string[] }>>
>;

describe("MQTT GraphQL API", () => {
  describe("Modules", () => {
    let _definitions: OperationResult;

    const getAll = async () => {
      return (_definitions ??= await client.query(ALL_FRAGMENTS_QUERY, {}));
    };

    test("query does not return errors", async () => {
      const definitions = await getAll();

      expect(definitions.error).toBeUndefined();
    });

    test("query returns data", async () => {
      const definitions = await getAll();

      expect(definitions.data).toBeDefined();
    });

    // thrapp's automation mode: every module with a controller, null until it has published one.
    describe("Automatic control", () => {
      let _status: OperationResult<ControlResponse>;

      const getStatus = async () =>
        (_status ??= await client.query<ControlResponse>(CONTROL_QUERY, {}));

      test("query does not return errors", async () => {
        const status = await getStatus();

        expect(status.error).toBeUndefined();
      });

      test("query returns data", async () => {
        const status = await getStatus();

        expect(status.data?.thrs?.controller).toBeDefined();
      });

      test.each(CONTROLLED_MODULES)("answers %s's automation mode", async (module) => {
        const status = await getStatus();

        expect(status.data?.thrs?.controller).toHaveProperty([module, "automationMode"]);
      });
    });

    describe.each(Object.keys(DEFINITIONS))("%s", (moduleName) => {
      const parts = Object.keys(DEFINITIONS[moduleName]).filter(
        (partName) => Object.keys(DEFINITIONS[moduleName][partName]).length > 0,
      );

      describe.each(parts)("%s", (partName) => {
        // A component comes back at its path, null when the API has no value. Parameters and
        // control values are one topic each: null as a whole until thrs-control has published it.
        test.for(Object.keys(DEFINITIONS[moduleName][partName]))(
          "component '%s' is answered",
          async (componentName, { skip }) => {
            const definitions = await getAll();
            const { path } = DEFINITIONS[moduleName][partName][componentName];

            if (valueAt(definitions.data, path.slice(0, -1)) === null) {
              skip(`${partName} are null, skipping component tests`);
              return;
            }

            expect(valueAt(definitions.data, path)).not.toBeUndefined();
          },
        );
      });
    });
  });
});
