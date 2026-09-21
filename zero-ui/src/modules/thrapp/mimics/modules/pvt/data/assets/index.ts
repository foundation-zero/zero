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
      source: getField(SensorComponentType.Pvt, "pvt", "placeholder"),
      sensors: {
        heatExchanger: getField(SensorComponentType.HeatExchanger, "pvt", "pvtPvtMainFwd"),
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
      source: getField(SensorComponentType.Pvt, "pvt", "placeholder"),

      sensors: {
        heatExchanger: getField(SensorComponentType.HeatExchanger, "pvt", "pvtPvtMainAft"),
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
      source: getField(SensorComponentType.Pvt, "pvt", "placeholder"),

      sensors: {
        heatExchanger: getField(SensorComponentType.HeatExchanger, "pvt", "pvtPvtOwners"),
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
