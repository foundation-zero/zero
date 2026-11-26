import type { DcConverterGroup, PvtGroup } from "@/modules/thrapp/state/state.types";
import { ModeBadgeMode } from "./mode-badge.consts";

/** A target of a module that controls several, e.g. a PVT group. */
export type ModeTarget = PvtGroup | DcConverterGroup;

export type ModuleModeBadge = { mode: ModeBadgeMode; label?: string };
