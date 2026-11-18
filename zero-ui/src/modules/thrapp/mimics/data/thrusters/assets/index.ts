import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField } from "../../../providers";

export const THRUSTERS_ASSET_DATA = toFieldsMap({
  [MimicComponentType.Thruster]: {
    "15001002": toInstance<MimicComponentType.Thruster>({
      controls: {},
      controllerState: {},
      custom: {
        titleKey: "fwdTitle",
      },
      parameters: {},
      source: getField(SensorComponentType.Thruster, "thrusters", "placeholder"),
      sensors: {
        pcs: getField(SensorComponentType.Pcs, "thrusters", "placeholder"),
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
    "15001001": toInstance<MimicComponentType.Thruster>({
      controls: {},
      controllerState: {},
      custom: {
        titleKey: "aftTitle",
      },
      parameters: {},
      source: getField(SensorComponentType.Thruster, "thrusters", "placeholder"),

      sensors: {
        pcs: getField(SensorComponentType.Pcs, "thrusters", "placeholder"),
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
