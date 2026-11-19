import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField } from "../../../providers";

const propdrive = (
  field: "pcsAftAra1" | "pcsAftAra2" | "pcsFwdAra1" | "pcsFwdAra2",
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
    source: getField(SensorComponentType.PropulsionDrive, "propulsionDrive", field),
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
    propdriveAft1: propdrive("pcsAftAra1", "drivesPropdriveAft1Heat"),
    propdriveAft2: propdrive("pcsAftAra2", "drivesPropdriveAft2Heat"),
    propdriveFwd1: propdrive("pcsFwdAra1", "drivesPropdriveFwd1Heat"),
    propdriveFwd2: propdrive("pcsFwdAra2", "drivesPropdriveFwd2Heat"),
  },
  [MimicComponentType.ShorePowerConverter]: {
    shorepower: toInstance<MimicComponentType.ShorePowerConverter>({
      controls: {},
      controllerState: {},
      custom: {
        converters: [
          getField(SensorComponentType.ShorePowerConverter, "dc700VShoreConverter", "_07_11Tbc1A"),
          getField(SensorComponentType.ShorePowerConverter, "dc700VShoreConverter", "_07_11Tbc1B"),
          getField(SensorComponentType.ShorePowerConverter, "dc700VShoreConverter", "_07_12Tbc1A"),
          getField(SensorComponentType.ShorePowerConverter, "dc700VShoreConverter", "_07_12Tbc1B"),
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
