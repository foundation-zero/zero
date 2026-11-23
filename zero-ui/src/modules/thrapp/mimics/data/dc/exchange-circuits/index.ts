import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { toFieldsMap } from "../../../modules";
import { getField } from "../../../providers";
import { toConnectingCircuit, toExchangeCircuit, toSeawaterCircuit } from "../../helpers";

export const DC_EXCHANGE_CIRCUIT_DATA = toFieldsMap({
  [MimicComponentType.SeawaterCircuit]: {
    seawater: toSeawaterCircuit({
      custom: { circuitName: "Seawater" },
      source: getField(SensorComponentType.Temperature, "dc", "placeholder"),
    }),
  },
  [MimicComponentType.ExchangeCircuit]: {
    domesticHotWater: toExchangeCircuit(
      {
        custom: { circuitName: "Domestic Hot Water", modeModule: "dhw" },
        source: getField(SensorComponentType.HeatTransferDevice, "dhw", "dhwDcExchanger"),
      },
      { componentType: "Domestic Hot Water loop" },
    ),
  },
  // The converter groups as their sub-mimics see them.
  [MimicComponentType.ConnectingCircuit]: {
    aft: toConnectingCircuit(
      {
        custom: { circuitName: "DC converters", modeModule: "dc" },
        source: getField(SensorComponentType.HeatTransferDevice, "dc", "dcAftHeat"),
      },
      { componentType: "DC/DC group 1 loop" },
    ),
    ugrid: toConnectingCircuit(
      {
        custom: { circuitName: "DC converters", modeModule: "dc" },
        source: getField(SensorComponentType.HeatTransferDevice, "dc", "dcUgridHeat"),
      },
      { componentType: "DC/AC group 1 loop" },
    ),
    fwd: toConnectingCircuit(
      {
        custom: { circuitName: "DC converters", modeModule: "dc" },
        source: getField(SensorComponentType.HeatTransferDevice, "dc", "dcFwdHeat"),
      },
      { componentType: "DC/DC group 2 loop" },
    ),
  },
});
