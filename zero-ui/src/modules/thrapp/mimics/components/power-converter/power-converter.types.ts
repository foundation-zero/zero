import { SensorComponentType } from "@/modules/thrapp/types/thrs";

export type PowerConverterSourceType =
  | SensorComponentType.Brightloop
  | SensorComponentType.Ugrid
  | SensorComponentType.ShorePowerConverter;
