import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const PVT_ASSET_DATA = toFieldsMap({
  [MimicComponentType.Pvt]: {
    "9001-01": toInstance<MimicComponentType.Pvt>({
      controls: {},
      controllerState: {},
      custom: { group: "fwd" },
      parameters: {},
      source: getField(SensorComponentType.HeatExchanger, "pvt", "pvtPvtMainFwd"),
      sensors: {
        flow: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtFlowMainFwdStrings"),
        incoming: getField(
          SensorComponentType.CalculatedTemperature,
          "pvt",
          "pvtTemperatureMainFwdStringsSupply",
        ),
        outgoing: getField(
          SensorComponentType.CalculatedTemperature,
          "pvt",
          "pvtTemperatureMainFwdStringsReturn",
        ),
      },
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "PVT FWD",
          componentType: "PVT",
        });
      },
    }),
    "9002-01": toInstance<MimicComponentType.Pvt>({
      controls: {},
      controllerState: {},
      custom: { group: "aft" },
      parameters: {},
      source: getField(SensorComponentType.HeatExchanger, "pvt", "pvtPvtMainAft"),

      sensors: {
        flow: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtFlowMainAftStrings"),
        incoming: getField(
          SensorComponentType.CalculatedTemperature,
          "pvt",
          "pvtTemperatureMainAftStringsSupply",
        ),
        outgoing: getField(
          SensorComponentType.CalculatedTemperature,
          "pvt",
          "pvtTemperatureMainAftStringsReturn",
        ),
      },
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "PVT AFT",
          componentType: "PVT",
        });
      },
    }),
    "9001-03": toInstance<MimicComponentType.Pvt>({
      controls: {},
      controllerState: {},
      custom: { group: "owners" },
      parameters: {},
      source: getField(SensorComponentType.HeatExchanger, "pvt", "pvtPvtOwners"),

      sensors: {
        flow: getField(SensorComponentType.CalculatedFlow, "pvt", "pvtFlowOwnersStrings"),
        incoming: getField(
          SensorComponentType.CalculatedTemperature,
          "pvt",
          "pvtTemperatureOwnersStringsSupply",
        ),
        outgoing: getField(
          SensorComponentType.CalculatedTemperature,
          "pvt",
          "pvtTemperatureOwnersStringsReturn",
        ),
      },
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "PVT OWNERS",
          componentType: "PVT",
        });
      },
    }),
  },
});
