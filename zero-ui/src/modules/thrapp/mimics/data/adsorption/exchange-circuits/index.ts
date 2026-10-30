import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap, toInstance } from "../../../modules";
import { fieldTooltip } from "../../../modules/shared";
import { getCustomField, getField } from "../../../providers";
import { toExchangeCircuit, toSeawaterCircuit } from "../../helpers";

export const ADSORPTION_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.SeawaterCircuit]: {
    seawater: toSeawaterCircuit({
      custom: { circuitName: "Seawater" },
      source: getField(
        SensorComponentType.Temperature,
        "adsorption",
        "adsorptionAvailableSeawaterTemperature",
      ),
    }),
  },
  [MimicComponentType.ExchangeCircuit]: {
    domesticHotWater: toExchangeCircuit(
      {
        custom: { circuitName: "Domestic Hot", modeModule: "dhw" },
        source: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwAdsorptionExchanger"),
      },
      { componentType: "Domestic Hot Water loop" },
    ),
    highTemperature: toExchangeCircuit(
      {
        custom: { circuitName: "High Temp", modeModule: "pcm" },
        source: getField(
          SensorComponentType.HeatTransferDevice,
          "adsorption",
          "adsorptionHtExchanger",
        ),
      },
      { componentType: "High Temperature loop" },
    ),
  },
  [MimicComponentType.FreshwaterCircuit]: {
    cooling: toInstance<MimicComponentType.FreshwaterCircuit>({
      controls: {},
      controllerState: {},
      custom: { circuitName: "Cooling" },
      parameters: {},
      source: getCustomField("adsorption", {}),
      sensors: {
        flowIn: getField(SensorComponentType.Flow, "adsorption", "coolingFlowAdsorption"),
        tIn: getField(
          SensorComponentType.Temperature,
          "adsorption",
          "coolingTemperatureAdsorptionReturn",
        ),
        flowOut: getField(SensorComponentType.Flow, "adsorption", "coolingFlowAdsorption"),
        tOut: getField(
          SensorComponentType.Temperature,
          "adsorption",
          "coolingTemperatureAdsorptionSupply",
        ),
      },
      get tooltip() {
        return fieldTooltip(this.source, { title: "Cooling circuit" });
      },
    }),
  },
});
