import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField } from "../../../providers";

const propdrive = (
  field:
    "drivesPropdriveAft1" | "drivesPropdriveAft2" | "drivesPropdriveFwd1" | "drivesPropdriveFwd2",
  heatField:
    | "drivesPropdriveAft1Heat"
    | "drivesPropdriveAft2Heat"
    | "drivesPropdriveFwd1Heat"
    | "drivesPropdriveFwd2Heat",
) =>
  toInstance<MimicComponentType.PropulsionDrive>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {
      heatTransfer: getField(SensorComponentType.HeatTransferDevice, "drives", heatField),
    },
    source: getField(SensorComponentType.PropulsionDrive, "drives", field),
    get tooltip() {
      return fieldTooltip(this.source, {
        title: "propdrive",
      });
    },
  });

export const DRIVES_ASSET_DATA = toFieldsMap({
  [MimicComponentType.PropulsionCooler]: {
    "1012": toInstance<MimicComponentType.PropulsionCooler>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getField(SensorComponentType.HeatTransferDevice, "drives", "drivesAftOilCoolerHeat"),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "aft",
        });
      },
    }),
    "1013": toInstance<MimicComponentType.PropulsionCooler>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {},
      source: getField(SensorComponentType.HeatTransferDevice, "drives", "drivesFwdOilCoolerHeat"),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "fwd",
        });
      },
    }),
  },
  [MimicComponentType.PropulsionDrive]: {
    propdriveAft1: propdrive("drivesPropdriveAft1", "drivesPropdriveAft1Heat"),
    propdriveAft2: propdrive("drivesPropdriveAft2", "drivesPropdriveAft2Heat"),
    propdriveFwd1: propdrive("drivesPropdriveFwd1", "drivesPropdriveFwd1Heat"),
    propdriveFwd2: propdrive("drivesPropdriveFwd2", "drivesPropdriveFwd2Heat"),
  },
  [MimicComponentType.ShorePowerConverter]: {
    shorepower: toInstance<MimicComponentType.ShorePowerConverter>({
      controls: {},
      controllerState: {},
      custom: {
        converters: [
          getField(SensorComponentType.ShorePowerConverter, "drives", "drivesShorepower1a"),
          getField(SensorComponentType.ShorePowerConverter, "drives", "drivesShorepower1b"),
          getField(SensorComponentType.ShorePowerConverter, "drives", "drivesShorepower2a"),
          getField(SensorComponentType.ShorePowerConverter, "drives", "drivesShorepower2b"),
        ],
      },
      parameters: {},
      sensors: {
        heatTransfer: getField(
          SensorComponentType.HeatTransferDevice,
          "drives",
          "drivesShorepowerHeat",
        ),
      },
      // TODO: design how a group tile shows its total (summed power, max temperature)
      source: getField(SensorComponentType.ShorePowerGroup, "drives", "drivesShorepower"),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "shorepower",
          componentType: "Shorepower converter",
        });
      },
    }),
  },
});
