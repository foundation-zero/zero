import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { getField } from "../../../../providers";
import { fieldTooltip } from "../../../shared";

const propdrive = (
  field:
    | "drivesPropdriveAft1"
    | "drivesPropdriveAft2"
    | "drivesPropdriveFwd1"
    | "drivesPropdriveFwd2",
  heatField:
    | "drivesPropdriveAft1Heat"
    | "drivesPropdriveAft2Heat"
    | "drivesPropdriveFwd1Heat"
    | "drivesPropdriveFwd2Heat",
  temperatureField: "placeholder" = "placeholder",
) =>
  toInstance<MimicComponentType.PropulsionDrive>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {
      heatTransfer: getField(SensorComponentType.HeatTransferDevice, "drives", heatField),
      power: getField(SensorComponentType.Pvt, "drives", "placeholder"),
      temperature: getField(SensorComponentType.Temperature, "drives", temperatureField),
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
    aft: toInstance<MimicComponentType.PropulsionCooler>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {
        heatTransfer: getField(
          SensorComponentType.HeatTransferDevice,
          "drives",
          "drivesAftOilCoolerHeat",
        ),
      },
      source: undefined,
      tooltip: { title: "aft", yardTag: "50001012" },
    }),
    fwd: toInstance<MimicComponentType.PropulsionCooler>({
      controls: {},
      controllerState: {},
      custom: {},
      parameters: {},
      sensors: {
        heatTransfer: getField(
          SensorComponentType.HeatTransferDevice,
          "drives",
          "drivesFwdOilCoolerHeat",
        ),
      },
      source: undefined,
      tooltip: { title: "fwd", yardTag: "50001013" },
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
        converters: [],
      },
      parameters: {},
      sensors: {
        heatTransfer: getField(
          SensorComponentType.HeatTransferDevice,
          "drives",
          "drivesShorepowerHeat",
        ),
        power: getField(SensorComponentType.Pvt, "drives", "placeholder"),
        temperature: getField(SensorComponentType.Temperature, "drives", "placeholder"),
      },
      source: getField(SensorComponentType.ShorePowerConverter, "drives", "drivesShorepower"),
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "shorepower",
          componentType: "Shorepower converter",
        });
      },
    }),
  },
});
