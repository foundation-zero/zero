import { SensorComponentType } from "@/modules/thrs/types";
import { RiSnowflakeLine } from "@remixicon/vue";
import { toInstance } from "../../..";
import { MimicComponentType } from "../../../../../types";
import { getField } from "../../../../providers";
import { tooltip } from "./shared";

export default toInstance<MimicComponentType.Asset>({
  controls: {},
  custom: {
    icon: RiSnowflakeLine,
    hideMode: true,
  },
  parameters: {},
  sensors: {
    heatExchanger: getField(SensorComponentType.HeatExchanger, "boilers", "boilersHvacExchanger"),
  },
  tooltip: tooltip({
    title: "HVAC",
    yardTag: "41001001",
    technicalName: "boilers-hvac-exchanger",
  }),
});
