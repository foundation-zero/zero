import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField, ModuleField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";
import {
  pvtHeatDumpController,
  pvtMainAftWarmupMixController,
  pvtMainFwdWarmupMixController,
  pvtOwnersWarmupMixController,
} from "../controllers";

export const tooltip = (field: ModuleField<"custom">): TooltipContent =>
  fieldTooltip(field, {
    title: "Mix valve",
    componentType: "3 way valve DN 25",
  });

export const PVT_MIX_VALVE_DATA = toFieldsMap({
  [MimicComponentType.MixValve]: {
    "1044-01": toInstance<MimicComponentType.MixValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixMainFwd"),
      },
      controllerState: {},
      custom: { controller: pvtMainFwdWarmupMixController },
      parameters: {},
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixMainFwd"),
      sensors: {},
      // tooltip: tooltip("1044-01", "pvt-mix-main-fwd"),
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1044-02": toInstance<MimicComponentType.MixValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixMainAft"),
      },
      controllerState: {},
      custom: { controller: pvtMainAftWarmupMixController },
      parameters: {},
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixMainAft"),
      sensors: {},
      // tooltip: tooltip("1044-02", "pvt-mix-main-aft"),
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1043-01": toInstance<MimicComponentType.MixValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixOwners"),
      },
      controllerState: {},
      custom: { controller: pvtOwnersWarmupMixController },
      parameters: {},
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixOwners"),
      sensors: {},
      // tooltip: tooltip("1043-01", "pvt-mix-owners"),
      get tooltip() {
        return tooltip(this.source);
      },
    }),
    "1047-02": toInstance<MimicComponentType.MixValve>({
      controls: {
        valve: getField(ControlComponentType.Valve, "pvt", "pvtMixExchanger"),
      },
      controllerState: {},
      custom: { controller: pvtHeatDumpController },
      parameters: {},
      source: getField(SensorComponentType.Valve, "pvt", "pvtMixExchanger"),
      sensors: {},
      // tooltip: tooltip("1047-02", "pvt-mix-exchanger"),
      get tooltip() {
        return tooltip(this.source);
      },
    }),
  },
});
