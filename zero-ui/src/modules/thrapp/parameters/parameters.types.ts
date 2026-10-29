import {
  ControllerStateComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrapp/types/thrs";
import { ModuleField } from "../mimics/providers";

export type PidControllerTuning = {
  type: SensorComponentType.Temperature | SensorComponentType.Flow;
  controller: ModuleField<ControllerStateComponentType.PIDController>;
  parameter: ModuleField<ParametersType.Tuning>;
  transform?: (value: number) => number;
};
