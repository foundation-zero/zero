import { DcAutomaticMode, type PvtAutomaticMode } from "@/modules/thrapp/stores/automation";

export type PvtGroup = keyof PvtAutomaticMode;
export type DcConverterGroup = keyof DcAutomaticMode;
