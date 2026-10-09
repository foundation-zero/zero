import { getField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { ControllerStateComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../shared";

const createHeatBattery = (
  title: string,
  heatExchanger: ModuleField<SensorComponentType.HeatTransferDevice>,
  controller: ModuleField<ControllerStateComponentType.PcmChargeController>,
) =>
  toInstance<MimicComponentType.Pcm>({
    source: heatExchanger,
    sensors: { heatTransfer: heatExchanger },
    controls: {},
    controllerState: { chargeController: controller },
    parameters: {},
    custom: {},
    get tooltip() {
      return fieldTooltip(this.source, {
        title: title,
        componentType: "PCM",
      });
    },
  });

export const PCM_HEAT_BATTERIES_DATA = toFieldsMap({
  [MimicComponentType.Pcm]: {
    "1049": createHeatBattery(
      "Heat battery 1",
      getField(SensorComponentType.HeatTransferDevice, "pcm", "pcmHeatModule1"),
      getField(
        ControllerStateComponentType.PcmChargeController,
        "pcm",
        "pcmModule1ChargeController",
      ),
    ),
    "1050": createHeatBattery(
      "Heat battery 2",
      getField(SensorComponentType.HeatTransferDevice, "pcm", "pcmHeatModule2"),
      getField(
        ControllerStateComponentType.PcmChargeController,
        "pcm",
        "pcmModule2ChargeController",
      ),
    ),
    "1051": createHeatBattery(
      "Heat battery 3",
      getField(SensorComponentType.HeatTransferDevice, "pcm", "pcmHeatModule3"),
      getField(
        ControllerStateComponentType.PcmChargeController,
        "pcm",
        "pcmModule3ChargeController",
      ),
    ),
    "1052": createHeatBattery(
      "Heat battery 4",
      getField(SensorComponentType.HeatTransferDevice, "pcm", "pcmHeatModule4"),
      getField(
        ControllerStateComponentType.PcmChargeController,
        "pcm",
        "pcmModule4ChargeController",
      ),
    ),
  },
});
