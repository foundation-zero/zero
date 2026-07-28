import { keysOf } from "@/modules/common/lib/utils";
import { ENV } from "@/settings";
import { Client, fetchExchange, OperationResult, TypedDocumentNode } from "@urql/vue";
import { describe, expect, test } from "vitest";
import { mutationWithoutValue, mutationWithValue } from "../graphql";
import { DEFINITIONS, QUERY_ALL, THRS } from "../lib/consts";
import { CONTROL_QUERY, ControlStatus } from "../stores/automation";
import { SimulationStatus, STATUS_QUERY } from "../stores/simulation";
import { ParameterDefinitions } from "../types";

const client = new Client({
  url: ENV.VITE_THRS_API_SERVER,
  exchanges: [fetchExchange],
  fetchOptions: {},
});

export default client;

describe("THRS API", () => {
  describe("Simulation", () => {
    const getStatus = async () => await client.query<SimulationStatus>(STATUS_QUERY, {});

    describe("Status", () => {
      test("query does not return errors", async () => {
        const status = await getStatus();

        expect(status.error).toBeUndefined();
      });

      test("query returns data", async () => {
        const status = await getStatus();

        expect(status.data).toBeDefined();
        expect(status.data!.simulation).toBeDefined();
        expect(status.data!.simulation.status).toBeDefined();
        expect(status.data!.simulation.time).toBeDefined();
      });
    });

    describe("Control (mutations)", () => {
      const executeMutation = async (
        mutation: TypedDocumentNode,
        variables: Record<string, unknown> = {},
      ) => {
        return await client.mutation(mutation, variables).toPromise();
      };

      const play = async (playbackRate: number = 1) =>
        await executeMutation(mutationWithValue("simulationPlay", "playbackRate", "Float"), {
          value: playbackRate,
        });

      const pause = async () => await executeMutation(mutationWithoutValue("simulationPause"), {});

      const step = async (seconds: number = 1) =>
        await executeMutation(mutationWithValue("simulationStep", "seconds", "Float!"), {
          value: seconds,
        });

      describe("Play", () => {
        test("does not return errors and changes state", async ({ skip }) => {
          let status = await getStatus();

          if (status.data?.simulation.status === "running") {
            return skip("Simulation is already running, skipping play mutation test");
          }

          const response = await play();

          expect(response.error).toBeUndefined();
          status = await getStatus();
          expect(status.data?.simulation.status).toBe("running");
        });
      });

      describe("Pause", () => {
        test("does not return errors and changes state", async ({ skip }) => {
          let status = await getStatus();

          if (status.data?.simulation.status === "available") {
            return skip("Simulation is already paused, skipping pause mutation test");
          }

          const response = await pause();

          expect(response.error).toBeUndefined();
          status = await getStatus();
          expect(status.data?.simulation.status).toBe("available");
        });
      });

      describe("Step", () => {
        test("does not return errors", async ({ skip }) => {
          const status = await getStatus();

          if (status.data?.simulation.status === "running") {
            return skip("Simulation is running, skipping step mutation test");
          }

          const response = await step();

          expect(response.error).toBeUndefined();
        });
      });
    });
  });

  describe("Modules", () => {
    let _definitions: OperationResult<THRS>;

    const getAll = async () => {
      return (_definitions ??= await client.query<THRS>(QUERY_ALL, {}));
    };

    test("query does not return errors", async () => {
      const definitions = await getAll();

      expect(definitions.error).toBeUndefined();
    });

    test("query returns data", async () => {
      const definitions = await getAll();

      expect(definitions.data).toBeDefined();
      expect(definitions.data?.modules).toBeDefined();
    });

    describe("Automatic control", () => {
      let _status: OperationResult<ControlStatus>;

      const getStatus = async () => {
        return (_status ??= await client.query<ControlStatus>(CONTROL_QUERY, {}));
      };

      test("query does not return errors", async () => {
        const status = await getStatus();

        expect(status.error).toBeUndefined();
      });

      test("query returns data", async () => {
        const status = await getStatus();

        expect(status.data).toBeDefined();
        expect(status.data!.modules).toBeDefined();
      });

      describe.each(keysOf(DEFINITIONS))("%s", (moduleName) => {
        test("has control mode", async () => {
          const status = await getStatus();
          expect(status.data?.modules[moduleName]).toBeDefined();
          expect(status.data?.modules[moduleName].controlMode).toBeDefined();
        });
      });
    });

    describe.each(keysOf(DEFINITIONS))("%s", (moduleName) => {
      test("module has definitions", async () => {
        const definitions = await getAll();
        expect(definitions.data?.modules[moduleName]).toBeDefined();
      });

      describe.each(keysOf(DEFINITIONS[moduleName]))("%s", (componentName) => {
        test("component has definitions", async () => {
          const definitions = await getAll();
          expect(definitions.data?.modules[moduleName][componentName]).toBeDefined();
        });

        describe.each(keysOf(DEFINITIONS[moduleName][componentName] as ParameterDefinitions))(
          "field '%s'",
          (fieldName) => {
            test("field has definitions", async ({ skip }) => {
              const definitions = await getAll();

              const component = definitions.data?.modules[moduleName][componentName];

              if (component == null) {
                skip("Component is null, skipping field tests");
                return;
              }

              expect(component[fieldName as keyof typeof component]).toBeDefined();
            });
          },
        );
      });
    });
  });
});
