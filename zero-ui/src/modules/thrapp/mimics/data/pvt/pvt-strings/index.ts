import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField, ModuleField } from "../../../providers";

const toPvtString = (
  source: ModuleField<SensorComponentType.HeatTransferDevice, "pvt">,
  tooltip?: Partial<TooltipContent>,
) =>
  toInstance<MimicComponentType.PvtString>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    source: source,
    sensors: {},
    get tooltip() {
      const content = fieldTooltip(source, { componentType: "PVT string", ...tooltip });
      return { ...content, title: `PVT string ${content.yardTag ?? ""}` };
    },
  });

// String 1.2 has an naming conflict with string 12 and thus does not exist yet
export const PVT_STRING_DATA = toFieldsMap({
  [MimicComponentType.PvtString]: {
    "aft-string-1.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString11Heat"),
    ),
    "aft-string-1.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "placeholder"),
      { yardTag: "1.2" },
    ),
    "aft-string-2.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString21Heat"),
    ),
    "aft-string-2.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString22Heat"),
    ),
    "aft-string-3": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString3Heat"),
    ),
    "aft-string-4": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString4Heat"),
    ),
    "aft-string-5.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString51Heat"),
    ),
    "aft-string-5.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString52Heat"),
    ),
    "aft-string-6.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString61Heat"),
    ),
    "aft-string-6.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString62Heat"),
    ),
    "aft-string-7.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString71Heat"),
    ),
    "aft-string-7.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString72Heat"),
    ),
    "aft-string-8.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString81Heat"),
    ),
    "aft-string-8.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString82Heat"),
    ),
    "aft-string-9": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString9Heat"),
    ),
    "aft-string-10": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString10Heat"),
    ),
    "aft-string-11.1": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString111Heat"),
    ),
    "aft-string-11.2": toPvtString(
      getField(SensorComponentType.HeatTransferDevice, "pvt", "pvtMainString112Heat"),
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
