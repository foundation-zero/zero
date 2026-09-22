import { getField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { ControllerStateComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { fieldTooltip } from "../../../shared";

const createHeatBattery = (
  title: string,
  source: ModuleField<SensorComponentType.Pcm>,
  heatExchanger: ModuleField<SensorComponentType.HeatExchanger>,
  controller: ModuleField<ControllerStateComponentType.ChargeController>,
) =>
  toInstance<MimicComponentType.Pcm>({
    source,
    sensors: { heatExchanger: heatExchanger },
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
      getField(SensorComponentType.Pcm, "pcm", "pcmModule1"),
      getField(SensorComponentType.HeatExchanger, "pcm", "pcmHeatModule1"),
      getField(ControllerStateComponentType.ChargeController, "pcm", "module1ChargeController"),
    ),
    "1050": createHeatBattery(
      "Heat battery 2",
      getField(SensorComponentType.Pcm, "pcm", "pcmModule2"),
      getField(SensorComponentType.HeatExchanger, "pcm", "pcmHeatModule2"),
      getField(ControllerStateComponentType.ChargeController, "pcm", "module2ChargeController"),
    ),
    "1051": createHeatBattery(
      "Heat battery 3",
      getField(SensorComponentType.Pcm, "pcm", "pcmModule3"),
      getField(SensorComponentType.HeatExchanger, "pcm", "pcmHeatModule3"),
      getField(ControllerStateComponentType.ChargeController, "pcm", "module3ChargeController"),
    ),
    "1052": createHeatBattery(
      "Heat battery 4",
      getField(SensorComponentType.Pcm, "pcm", "pcmModule4"),
      getField(SensorComponentType.HeatExchanger, "pcm", "pcmHeatModule4"),
      getField(ControllerStateComponentType.ChargeController, "pcm", "module4ChargeController"),
    ),
  },
});
