import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { ModuleField } from "../../providers";

export type DcConverterStatusProps = {
  sources: ModuleField<
    | SensorComponentType.Brightloop
    | SensorComponentType.Ugrid
    | SensorComponentType.ShorePowerConverter
  >[];
};

export type DcConverterTitleKey = "group1" | "group2" | "group3";
