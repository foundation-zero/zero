import { TooltipContent } from "@/modules/heat/components/tooltip";
import { ModuleField } from "@/modules/heat/mimics/providers";
import { DcConverterGroup } from "@/modules/heat/state";
import { MimicComponentType } from "@/modules/heat/types";
import { SensorComponentType } from "@/modules/heat-simulation/types";
import { toFieldsMap, toInstance } from "../../..";
import { DcConverterTitleKey } from "../../../../components/dc-converter";
import { getField } from "../../../../providers";

const dcConverter = (
  converters: ModuleField<SensorComponentType.Ugrid | SensorComponentType.Brightloop>[],
  heatTransfer: ModuleField<SensorComponentType.HeatTransferDevice, "dc">,
  power: ModuleField<SensorComponentType.Pvt, "dc">,
  temperature: ModuleField<SensorComponentType.Temperature, "dc">,
  group: DcConverterGroup,
  titleKey: DcConverterTitleKey,
) =>
  toInstance<MimicComponentType.DcConverter>({
    controls: {},
    controllerState: {},
    custom: { converters, group },
    parameters: {},
    sensors: {
      heatTransfer: heatTransfer,
      power: power,
      temperature: temperature,
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
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcAftHeat"),
      getField(SensorComponentType.Pvt, "dc", "placeholder"),
      getField(SensorComponentType.Temperature, "dc", "placeholder"),
      "brightloopsAft",
      "group1",
    ),
    ugrid: dcConverter(
      [
        getField(SensorComponentType.Ugrid, "dc", "dcUgrid1"),
        getField(SensorComponentType.Ugrid, "dc", "dcUgrid2"),
      ],
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcUgridHeat"),
      getField(SensorComponentType.Pvt, "dc", "placeholder"),
      getField(SensorComponentType.Temperature, "dc", "placeholder"),
      "ugrids",
      "group2",
    ),
    fwd: dcConverter(
      [
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd1"),
        getField(SensorComponentType.Brightloop, "dc", "dcBrightloopFwd2"),
      ],
      getField(SensorComponentType.HeatTransferDevice, "dc", "dcFwdHeat"),
      getField(SensorComponentType.Pvt, "dc", "placeholder"),
      getField(SensorComponentType.Temperature, "dc", "placeholder"),
      "brightloopsFwd",
      "group3",
    ),
  },
});
