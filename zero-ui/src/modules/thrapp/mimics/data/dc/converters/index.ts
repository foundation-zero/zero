import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { DcConverterGroup } from "@/modules/thrapp/state";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../../modules";
import { getField } from "../../../providers";

const dcConverter = (
  converters: ModuleField<SensorComponentType.Ugrid | SensorComponentType.Brightloop>[],
  heatTransfer: ModuleField<SensorComponentType.HeatTransferDevice, "dc">,
  group: DcConverterGroup,
  tooltip: TooltipContent,
) =>
  toInstance<MimicComponentType.DcConverter>({
    controls: {},
    controllerState: {},
    custom: { converters, group },
    parameters: {},
    sensors: {
      heatTransfer: heatTransfer,
    },
    source: converters[0], // TODO: Fix this!
    get tooltip(): TooltipContent {
      return {
        componentType: "DC converter",
        ...tooltip,
      };
    },
  });

export const DC_CONVERTER_DATA = toFieldsMap({
  [MimicComponentType.DcConverter]: {
    aft: dcConverter(
      [
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft1"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft2"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft3"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopAft4"),
      ],
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcAftHeat"),
      "brightloopsAft",
      { title: "group1", technicalName: "dc-brightloop-aft", mqttTopic: "dc-brightloop-aft" },
    ),
    ugrid: dcConverter(
      [
        getField(SensorComponentType.Ugrid, "dc", "dcUgrid1"),
        getField(SensorComponentType.Ugrid, "dc", "dcUgrid2"),
      ],
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcUgridHeat"),
      "ugrids",
      { title: "group2", technicalName: "dc-ugrids", mqttTopic: "dc-ugrids" },
    ),
    fwd: dcConverter(
      [
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd1"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd2"),
      ],
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcFwdHeat"),
      "brightloopsFwd",
      { title: "group3", technicalName: "dc-brightloop-fwd", mqttTopic: "dc-brightloop-fwd" },
    ),
  },
});
