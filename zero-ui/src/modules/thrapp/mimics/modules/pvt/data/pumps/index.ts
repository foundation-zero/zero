import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Pump",
  itemName: "Circulation pump",
  yardTag,
  technicalName,
});

export const PVT_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1182": toInstance<MimicComponentType.Pump>({
      custom: {},
      source: getField(SensorComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      controllerState: {
        flowController: ["pidController", "pvt", "pvtMainFwdFlowController"],
        temperatureController: ["pidController", "pvt", "pvtMainFwdTemperatureController"],
      },
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      parameters: {
        flow: getField(ParametersType.Flow, "pvt", "mainFwdMinimumPumpDutypoint"),
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
      sensors: {
        pressure: getField(SensorComponentType.Pressure, "pvt", "pvtPressureSystem"),
        flowMeasurement: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainFwdRecovery"),
        temperatureMeasurement: getField(
          SensorComponentType.Temperature,
          "pvt",
          "pvtTemperatureSupply",
        ),
      },
      tooltip: tooltip("1182", "pvt-main-circulation-pump"),
    }),
  },
});
