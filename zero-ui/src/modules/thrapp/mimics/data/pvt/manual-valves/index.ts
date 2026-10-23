import { MimicComponentType } from "@/modules/thrapp/types";
import { toFieldsMap } from "../../../modules";
import { toManualValve } from "../../helpers";
import { PVT_AFT_MANUAL_VALVE_TAGS } from "./_aft";

const manualValveTags = [
  "1169-05",
  "1169-04",
  "1168-12",
  "1168-30",
  "1168-31",
  "1168-32",
  "1069-06",
  "1169-07",
  "1169-08",
  "1169-09",
  "1191-01",
  "1191-02",
  "1170-05",
  "1170-06",
  "1177-01",
  "1177-02",
  "1167-11",
  "1168-19",
];

export const PVT_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    [...manualValveTags, ...PVT_AFT_MANUAL_VALVE_TAGS].map((tag) => [tag, toManualValve(tag)]),
  ),
});
