import {
  ControlComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toManualPump, toPump } from "../../helpers";
import {
  pvtMainAftPumpController,
  pvtMainFwdPumpController,
  pvtOwnersPumpController,
} from "../controllers";

export const PVT_PUMP_DATA = toFieldsMap({
  [MimicComponentType.Pump]: {
    "1018": toPump({
      custom: { temperatureController: pvtMainFwdPumpController },
      source: getField(SensorComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainFwd"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainFwdMinimumPumpDutypoint"),
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
    }),
    "1019": toPump({
      custom: { temperatureController: pvtMainAftPumpController },
      source: getField(SensorComponentType.Pump, "pvt", "pvtPumpMainAft"),
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpMainAft"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "mainAftMinimumPumpDutypoint"),
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
    }),
    "1021": toPump({
      custom: { temperatureController: pvtOwnersPumpController },
      source: getField(SensorComponentType.Pump, "pvt", "pvtPumpOwners"),
      controls: {
        pump: getField(ControlComponentType.Pump, "pvt", "pvtPumpOwners"),
      },
      parameters: {
        flow: getField(ParametersType.Dutypoint, "pvt", "ownersMinimumPumpDutypoint"),
        temperature: getField(ParametersType.Temperature, "pvt", "recoveryTemperature"),
      },
    }),
  },
  [MimicComponentType.ManualPump]: {
    "1182": toManualPump("1182"),
  },
});
