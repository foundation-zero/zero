import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { DcConverterGroup } from "@/modules/thrapp/state";
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrsim/types";
import { toFieldsMap, toInstance } from "../../..";
import { DcConverterTitleKey } from "../../../../components/dc-converter";
import { getField } from "../../../../providers";

const dcConverter = (
  converters: ModuleField<SensorComponentType.Ugrid | SensorComponentType.Brightloop>[],
  group: DcConverterGroup,
  titleKey: DcConverterTitleKey,
) =>
  toInstance<MimicComponentType.DcConverter>({
    controls: {},
    controllerState: {},
    custom: { converters, group },
    parameters: {},
    sensors: {
      heatTransfer: getField(SensorComponentType.HeatTransferDevice, "dc", "placeholder"),
      temperature: getField(SensorComponentType.Temperature, "dc", "placeholder"),
    },
    source: undefined,
    get tooltip(): TooltipContent {
      return {
        title: titleKey,
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
      "brightloopsAft",
      "group1",
    ),
    ugrid: dcConverter(
      [
        getField(SensorComponentType.Ugrid, "dc", "dcUgrid1"),
        getField(SensorComponentType.Ugrid, "dc", "dcUgrid2"),
      ],
      "ugrids",
      "group2",
    ),
    fwd: dcConverter(
      [
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd1"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd2"),
      ],
      "brightloopsFwd",
      "group3",
    ),
  },
});
