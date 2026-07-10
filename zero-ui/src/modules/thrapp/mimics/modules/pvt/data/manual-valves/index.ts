import { toFieldsMap, toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";

const tooltip = (yardTag: string, technicalName: string) => ({
  title: "Manual valve",
  itemName: "Manual valve",
  yardTag,
  technicalName,
});

const ids = ["1170-05", "1170-06", "1177-01", "1177-02"] as const;

export const PVT_MANUAL_VALVE_DATA = toFieldsMap({
  [MimicComponentType.ManualValve]: Object.fromEntries(
    ids.map((id) => [
      id,
      toInstance<MimicComponentType.ManualValve>({
        controls: {},
        controllerState: {},
        custom: {},
        parameters: {},
        sensors: {},
        source: undefined,
        tooltip: tooltip(id, `pvt-manual-valve-${id}`),
      }),
    ]),
  ),
});
