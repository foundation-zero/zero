import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField, ModuleField } from "../../../providers";

const toPvtString = (source: ModuleField<SensorComponentType.HeatTransferDevice, "pvt">) =>
  toInstance<MimicComponentType.PvtString>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: source,
    sensors: {},
    get tooltip() {
      const content = fieldTooltip(source, { componentType: "PVT string" });
      return { ...content, title: `PVT string ${content.yardTag ?? ""}` };
    },
  });

export const PVT_STRING_DATA = toFieldsMap({
  [MimicComponentType.PvtString]: {
    "aft-string-1.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString1_1Heat"),
    ),
    "aft-string-1.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString1_2Heat"),
    ),
    "aft-string-2.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString2_1Heat"),
    ),
    "aft-string-2.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString2_2Heat"),
    ),
    "aft-string-3": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString3Heat"),
    ),
    "aft-string-4": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString4Heat"),
    ),
    "aft-string-5.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString5_1Heat"),
    ),
    "aft-string-5.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString5_2Heat"),
    ),
    "aft-string-6.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString6_1Heat"),
    ),
    "aft-string-6.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString6_2Heat"),
    ),
    "aft-string-7.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString7_1Heat"),
    ),
    "aft-string-7.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString7_2Heat"),
    ),
    "aft-string-8.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString8_1Heat"),
    ),
    "aft-string-8.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString8_2Heat"),
    ),
    "aft-string-9": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString9Heat"),
    ),
    "aft-string-10": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString10Heat"),
    ),
    "aft-string-11.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString11_1Heat"),
    ),
    "aft-string-11.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString11_2Heat"),
    ),
    "aft-string-12": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString12Heat"),
    ),
    "aft-string-13": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString13Heat"),
    ),
    "owners-string-1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtOwnersString1Heat"),
    ),
    "owners-string-2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtOwnersString2Heat"),
    ),
    "owners-string-3": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtOwnersString3Heat"),
    ),
    "owners-string-4": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtOwnersString4Heat"),
    ),
    "owners-string-5": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtOwnersString5Heat"),
    ),
    "owners-string-6": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtOwnersString6Heat"),
    ),
  },
});
