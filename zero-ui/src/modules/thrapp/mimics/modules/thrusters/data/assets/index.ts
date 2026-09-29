import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

export const THRUSTERS_ASSET_DATA = toFieldsMap({
  [MimicComponentType.Thruster]: {
    "9001-01": toInstance<MimicComponentType.Thruster>({
      controls: {},
      controllerState: {},
      custom: {
        titleKey: "fwdTitle",
      },
      parameters: {},
      source: getField(SensorComponentType.Thruster, "thrusters", "thrustersThrusterFwd"),
      sensors: {
        pcs: getField(SensorComponentType.Pcs, "thrusters", "thrustersPcs"),
        heatTransfer: getField(
          SensorComponentType.HeatTransferDevice,
          "thrusters",
          "thrustersThrusterFwdHeat",
        ),
      },
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Thruster FWD",
          componentType: "thrusters",
        });
      },
    }),
    "9002-01": toInstance<MimicComponentType.Thruster>({
      controls: {},
      controllerState: {},
      custom: {
        titleKey: "aftTitle",
      },
      parameters: {},
      source: getField(SensorComponentType.Thruster, "thrusters", "thrustersThrusterAft"),

      sensors: {
        pcs: getField(SensorComponentType.Pcs, "thrusters", "thrustersPcs"),
        heatTransfer: getField(
          SensorComponentType.HeatTransferDevice,
          "thrusters",
          "thrustersThrusterAftHeat",
        ),
      },
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Thruster AFT",
          componentType: "thrusters",
        });
      },
    }),
  },
});
