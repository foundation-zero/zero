import { MimicComponentType } from "@/modules/thrapp/types";
import { RegisterField } from "../../data";

/** The fields of the upper and the lower converter's branch, in that order. */
export type BranchFields<Type extends MimicComponentType> = [
  RegisterField<Type>,
  RegisterField<Type>,
];

/** The fields of a group of two DC converters, as the converter pair's layers draw them. */
export type DcConverterPairFields = {
  converters: BranchFields<MimicComponentType.PowerConverter>;
  circuit: RegisterField<MimicComponentType.ConnectingCircuit>;
  switchValves: BranchFields<MimicComponentType.SwitchValve>;
  manualValves: BranchFields<MimicComponentType.ManualValve>;
  temperatureSensors: BranchFields<MimicComponentType.TemperatureSensor>;
  flowSensors: BranchFields<MimicComponentType.FlowSensor>;
};
