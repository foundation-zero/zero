import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { MimicKey } from "@/modules/thrapp/router/mimics";
import { DcConverterGroup } from "@/modules/thrapp/state";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField } from "../../../providers";

const dcConverter = (
  source: ModuleField<SensorComponentType.UgridGroup | SensorComponentType.BrightloopGroup, "dc">,
  converters: ModuleField<SensorComponentType.Ugrid | SensorComponentType.Brightloop>[],
  heatTransfer: ModuleField<SensorComponentType.HeatTransferDevice, "dc">,
  group: DcConverterGroup,
  mimic: MimicKey,
  tooltip: TooltipContent,
) =>
  toInstance<MimicComponentType.DcConverter>({
    controls: {},
    controllerState: {},
    custom: { converters, group, mimic },
    parameters: {},
    sensors: {
      heatTransfer: heatTransfer,
    },
    // TODO: design how a group tile shows its total (summed power, max temperature)
    source,
    get tooltip(): TooltipContent {
      return {
        componentType: "DC converter",
        ...tooltip,
      };
    },
  });

const powerConverter = (
  source: ModuleField<SensorComponentType.Brightloop | SensorComponentType.Ugrid>,
  title: string,
) =>
  toInstance<MimicComponentType.PowerConverter>({
    controls: {},
    controllerState: {},
    custom: {},
    parameters: {},
    sensors: {
      // The converters only report their power and temperatures; heat is measured per group.
      heatTransfer: getField(SensorComponentType.HeatTransferDevice, "dc", "placeholder"),
    },
    source,
    get tooltip() {
      return fieldTooltip(this.source, { title, componentType: "DC converter" });
    },
  });

export const DC_CONVERTER_DATA = toFieldsMap({
  [MimicComponentType.DcConverter]: {
    aft: dcConverter(
      getField(SensorComponentType.BrightloopGroup, "dc", "dcAftBrightloops"),
      [
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft1"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft2"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft3"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft4"),
      ],
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcAftHeat"),
      "brightloopsAft",
      "dc-aft",
      { title: "group1", technicalName: "dc-brightloop-aft", mqttTopic: "dc-brightloop-aft" },
    ),
    ugrid: dcConverter(
      getField(SensorComponentType.UgridGroup, "dc", "dcUgrids"),
      [
        getField(SensorComponentType.Ugrid, "dcAcConverter", "_05_11U101"),
        getField(SensorComponentType.Ugrid, "dcAcConverter", "_05_12U101"),
      ],
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcUgridHeat"),
      "ugrids",
      "dc-ugrid",
      { title: "group2", technicalName: "dc-ugrids", mqttTopic: "dc-ugrids" },
    ),
    fwd: dcConverter(
      getField(SensorComponentType.BrightloopGroup, "dc", "dcFwdBrightloops"),
      [
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd1"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd2"),
      ],
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcFwdHeat"),
      "brightloopsFwd",
      "dc-fwd",
      { title: "group3", technicalName: "dc-brightloop-fwd", mqttTopic: "dc-brightloop-fwd" },
    ),
  },
  [MimicComponentType.PowerConverter]: {
    "aft-1": powerConverter(
      getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft1"),
      "Brightloop AFT 1",
    ),
    "aft-2": powerConverter(
      getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft2"),
      "Brightloop AFT 2",
    ),
    "aft-3": powerConverter(
      getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft3"),
      "Brightloop AFT 3",
    ),
    "aft-4": powerConverter(
      getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft4"),
      "Brightloop AFT 4",
    ),
    "ugrid-1": powerConverter(
      getField(SensorComponentType.Ugrid, "dcAcConverter", "_05_11U101"),
      "U-Grid 1",
    ),
    "ugrid-2": powerConverter(
      getField(SensorComponentType.Ugrid, "dcAcConverter", "_05_12U101"),
      "U-Grid 2",
    ),
    "fwd-1": powerConverter(
      getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd1"),
      "Brightloop FWD 1",
    ),
    "fwd-2": powerConverter(
      getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd2"),
      "Brightloop FWD 2",
    ),
  },
});
