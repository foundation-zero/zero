import { SensorComponentType } from "@/modules/thrs/types";
import { RiTempHotLine } from "@remixicon/vue";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.Asset>({
  controls: {},
  custom: {
    icon: RiTempHotLine,
    width: 200,
    height: 164,
  },
  parameters: {},
  sensors: {
    heatExchanger: getField(SensorComponentType.HeatExchanger, "boilers", "boilersHeatpump"),
  },
  tooltip: tooltip({
    title: "Heat Pump",
    yardTag: "1035",
    technicalName: "boilers-heatpump",
  }),
});
