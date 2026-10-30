import { MimicComponentType } from "@/modules/thrapp/types";
import { ControlComponentType, SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getField } from "../../../providers";

export const ADSORPTION_ASSET_DATA = toFieldsMap({
  [MimicComponentType.AdsorptionChiller]: {
    "1034": toInstance<MimicComponentType.AdsorptionChiller>({
      controls: {
        chiller: getField(
          ControlComponentType.AdsorptionChiller,
          "adsorption",
          "adsorptionChiller",
        ),
      },
      controllerState: {},
      custom: {},
      parameters: {},
      source: getField(SensorComponentType.AdsorptionChiller, "adsorption", "adsorptionChiller"),
      sensors: {
        highTemperature: getField(
          SensorComponentType.HeatTransferDevice,
          "adsorption",
          "adsorptionHotHeat",
        ),
        mediumTemperature: getField(
          SensorComponentType.HeatTransferDevice,
          "adsorption",
          "adsorptionWasteHeat",
        ),
        lowTemperature: getField(
          SensorComponentType.HeatTransferDevice,
          "adsorption",
          "adsorptionCoolingHeat",
        ),
      },
      get tooltip() {
        return fieldTooltip(this.source, {
          title: "Fahrenheit",
          componentType: "Adsorption chiller",
        });
      },
    }),
  },
});
