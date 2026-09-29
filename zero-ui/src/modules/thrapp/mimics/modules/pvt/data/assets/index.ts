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
      source: getField(SensorComponentType.Pvt, "pvt", "pvtPvtMainFwd"),
      sensors: {
        heatTransfer: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPvtMainFwdHeat"),
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
      source: getField(SensorComponentType.Pvt, "pvt", "pvtPvtMainAft"),

      sensors: {
        heatTransfer: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPvtMainAftHeat"),
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
      source: getField(SensorComponentType.Pvt, "pvt", "pvtPvtOwners"),

      sensors: {
        heatTransfer: getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtPvtOwnersHeat"),
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
