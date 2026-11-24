import { Nullable } from "@/modules/common/types";
import { mqttGraphqlContext } from "../graphql/client";

import { gql, useClientHandle, useQuery } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { OperationResult } from "graphql-ws";
import { Maybe } from "graphql/jsutils/Maybe";

import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { CONTROLLED_MODULES, ControlledModule, DEFINITIONS } from "../lib/consts";
import { automationModeMutation } from "../lib/mqtt-graphql.utils";
import { AmcsControlModeSensor, DcMode, PvtMode, SensorComponentType } from "../types/thrs";

export type ThrustersAutomaticMode = { mode: string };
export type PcmAutomaticMode = { mode: string };
export type PvtAutomaticMode = {
  aft: { mode: PvtMode };
  fwd: { mode: PvtMode };
  owners: { mode: PvtMode };
};
export type AdsorptionAutomaticMode = { mode: string };
export type ConsumersAutomaticMode = Record<string, never>;
export type ConvertersAutomaticMode = { mode: DcMode };
export type DcAutomaticMode = {
  brightloopsAft: ConvertersAutomaticMode;
  brightloopsFwd: ConvertersAutomaticMode;
  ugrids: ConvertersAutomaticMode;
};
export type DhwAutomaticMode = { boostingMode: string; fillingMode: string };
export type DrivesAutomaticMode = { mode: string };

export type AutomaticMode =
  | ThrustersAutomaticMode
  | PcmAutomaticMode
  | PvtAutomaticMode
  | AdsorptionAutomaticMode
  | ConsumersAutomaticMode
  | DcAutomaticMode
  | DhwAutomaticMode
  | DrivesAutomaticMode;

export type ControlMode<T extends AutomaticMode = AutomaticMode> = {
  automatic: boolean;
  automaticMode: Nullable<T>;
};

export type ControlModes = {
  thrusters: ThrustersAutomaticMode;
  pcm: PcmAutomaticMode;
  pvt: PvtAutomaticMode;
  adsorption: AdsorptionAutomaticMode;
  consumers: ConsumersAutomaticMode;
  dc: DcAutomaticMode;
  dhw: DhwAutomaticMode;
  drives: DrivesAutomaticMode;
};

export type ControlStatus = {
  modules: {
    [K in keyof ControlModes]: {
      controlMode: Nullable<ControlMode<ControlModes[K]>>;
      // The AMCS mode of the module's devices, if it has an AMCS mode device.
      sensorValues: { mode?: AmcsControlModeSensor };
    };
  };
};

// What each module's automatic controller is doing, as the selection of its automatic mode.
// Consumers' has no fields.
const AUTOMATIC_MODE_SELECTIONS: Record<ControlledModule, string> = {
  thrusters: "mode",
  pvt: "aft { mode } fwd { mode } owners { mode }",
  pcm: "mode",
  adsorption: "mode",
  consumers: "",
  dc: "brightloopsAft { mode } brightloopsFwd { mode } ugrids { mode }",
  dhw: "boostingMode fillingMode",
  drives: "mode",
};

// A module's AMCS mode device is `<module>Mode`, when the generated definitions have one.
const hasAmcsMode = (module: ControlledModule): boolean =>
  Object.entries(DEFINITIONS[module].sensorValues).some(
    ([key, { componentType }]) =>
      key === `${module}Mode` && componentType === SensorComponentType.AmcsControlMode,
  );

type ControllerModes = {
  [K in keyof ControlModes]?: {
    automationMode?: { mode?: "MANUAL" | "AUTOMATIC" | null } | null;
    controlMode?: ControlModes[K] | null;
  } | null;
};

type DeviceModes = { [K in ControlledModule]?: { mode?: AmcsControlModeSensor | null } | null };

export type ControlResponse = {
  thrs?: { controller?: ControllerModes | null } | null;
  marpower?: { _500000Thrs?: DeviceModes | null } | null;
};

// A module's automation mode and, when it has fields, its automatic mode. An empty selection is
// invalid, so consumers' control mode is not queried.
const controllerSelection = (module: ControlledModule): string => {
  const automaticMode = AUTOMATIC_MODE_SELECTIONS[module];
  const controlMode = automaticMode ? `controlMode { ${automaticMode} }` : "";
  return `${module} { automationMode { mode } ${controlMode} }`;
};

const deviceModeSelection = (module: ControlledModule): string =>
  `${module} { mode { mode { value } } }`;

export const CONTROL_QUERY = gql`
  query ControlStatus {
    thrs {
      controller {
        ${CONTROLLED_MODULES.map(controllerSelection).join("\n")}
      }
    }
    marpower {
      _500000Thrs {
        ${CONTROLLED_MODULES.filter(hasAmcsMode).map(deviceModeSelection).join("\n")}
      }
    }
  }
`;

// The control status from the MQTT GraphQL response, in the shape the views have read since
// thrs-api: a module is automatic when its automation mode is, and its control mode is unknown
// (`null`) until the module has published an automation mode. The automatic mode says what the
// automatic controller is doing, so a manual module has none.
const toControlStatus = (response: ControlResponse): ControlStatus => {
  const modules = Object.fromEntries(
    CONTROLLED_MODULES.map((module) => {
      const controller = response.thrs?.controller?.[module];
      const automationMode = controller?.automationMode?.mode;
      const automatic = automationMode === "AUTOMATIC";
      const automaticMode = automatic ? (controller?.controlMode ?? null) : null;
      const sensorValues = hasAmcsMode(module)
        ? { mode: response.marpower?._500000Thrs?.[module]?.mode ?? undefined }
        : {};
      return [
        module,
        {
          controlMode: automationMode ? { automatic, automaticMode } : null,
          sensorValues,
        },
      ];
    }),
  );
  return { modules: modules as ControlStatus["modules"] };
};

export const useAutomationStore = defineStore("automation", () => {
  // For some reason the injected client does not come from the component in the outer scope.
  // This means we need to manually provide the context to each query and mutation.
  const { client } = useClientHandle();
  const isProcessing = ref(false);

  const controlQuery = useQuery<ControlResponse>({
    query: CONTROL_QUERY,
    context: mqttGraphqlContext,
  });
  const control = computed(
    () => controlQuery.data.value && toControlStatus(controlQuery.data.value),
  );

  // Use network-only policy to always get the latest control mode
  const updateControl = () => controlQuery.executeQuery({ requestPolicy: "network-only" });

  useIntervalFn(updateControl, 5000, {
    immediate: true,
  });

  const setAutomatedControl = (module: string) => {
    const mutation = automationModeMutation(module);

    return async (automatic: boolean) => {
      if (isProcessing.value) return;

      isProcessing.value = true;
      let result: Maybe<OperationResult> = undefined;

      try {
        const input = { mode: automatic ? "AUTOMATIC" : "MANUAL" };
        result = await client.mutation(mutation, { input }, mqttGraphqlContext);
        await updateControl();
      } catch (error) {
        console.error("Error executing mutation:", error);
      } finally {
        isProcessing.value = false;
      }

      return result;
    };
  };

  return {
    setAutomatedControl,
    control,
    isProcessing,
  };
});
