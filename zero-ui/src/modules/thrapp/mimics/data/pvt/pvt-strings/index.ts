import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { MimicComponentType } from "../../../../types";
import { toFieldsMap, toInstance } from "../../../modules";
import { getField } from "../../../providers";

const toPvtString = (
  label: string,
  sensors: ReturnType<typeof toInstance<MimicComponentType.PvtString>>["sensors"],
) =>
  toInstance<MimicComponentType.PvtString>({
    controls: {},
    controllerState: {},
    custom: { label },
    parameters: {},
    source: undefined,
    sensors,
    tooltip: { title: `PVT string ${label}`, componentType: "PVT string" },
  });

// String 1.2 has no flow or return temperature field in thrsim yet (9006-02, 9005-02).
export const PVT_STRING_DATA = toFieldsMap({
  [MimicComponentType.PvtString]: {
    "aft-string-1.1": toPvtString("1.1", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString11"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString1Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString11Return",
      ),
    }),
    "aft-string-1.2": toPvtString("1.2", {
      flow: getField(SensorComponentType.Flow, "pvt", "placeholder"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString1Supply",
      ),
      returnTemperature: getField(SensorComponentType.Temperature, "pvt", "placeholder"),
    }),
    "aft-string-2.1": toPvtString("2.1", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString21"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString2Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString21Return",
      ),
    }),
    "aft-string-2.2": toPvtString("2.2", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString22"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString2Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString22Return",
      ),
    }),
    "aft-string-3": toPvtString("3", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString3"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString3Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString3Return",
      ),
    }),
    "aft-string-4": toPvtString("4", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString4"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString4Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString4Return",
      ),
    }),
    "aft-string-5.1": toPvtString("5.1", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString51"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString5Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString51Return",
      ),
    }),
    "aft-string-5.2": toPvtString("5.2", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString52"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString5Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString52Return",
      ),
    }),
    "aft-string-6.1": toPvtString("6.1", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString61"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString6Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString61Return",
      ),
    }),
    "aft-string-6.2": toPvtString("6.2", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString62"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString6Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString62Return",
      ),
    }),
    "aft-string-7.1": toPvtString("7.1", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString71"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString7Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString71Return",
      ),
    }),
    "aft-string-7.2": toPvtString("7.2", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString72"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString7Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString72Return",
      ),
    }),
    "aft-string-8.1": toPvtString("8.1", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString81"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString8Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString81Return",
      ),
    }),
    "aft-string-8.2": toPvtString("8.2", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString82"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString8Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString82Return",
      ),
    }),
    "aft-string-9": toPvtString("9", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString9"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString9Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString9Return",
      ),
    }),
    "aft-string-10": toPvtString("10", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString10"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString10Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString10Return",
      ),
    }),
    "aft-string-11.1": toPvtString("11.1", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString111"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString11Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString111Return",
      ),
    }),
    "aft-string-11.2": toPvtString("11.2", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString112"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString11Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString112Return",
      ),
    }),
    "aft-string-12": toPvtString("12", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString12"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString12Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString12Return",
      ),
    }),
    "aft-string-13": toPvtString("13", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowMainString13"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString13Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureMainString13Return",
      ),
    }),
    "owners-string-1": toPvtString("1", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString1"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString1Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString1Return",
      ),
    }),
    "owners-string-2": toPvtString("2", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString2"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString2Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString2Return",
      ),
    }),
    "owners-string-3": toPvtString("3", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString3"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString3Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString3Return",
      ),
    }),
    "owners-string-4": toPvtString("4", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString4"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString4Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString4Return",
      ),
    }),
    "owners-string-5": toPvtString("5", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString5"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString5Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString5Return",
      ),
    }),
    "owners-string-6": toPvtString("6", {
      flow: getField(SensorComponentType.Flow, "pvt", "pvtFlowOwnersString6"),
      supplyTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString6Supply",
      ),
      returnTemperature: getField(
        SensorComponentType.Temperature,
        "pvt",
        "pvtTemperatureOwnersString6Return",
      ),
    }),
  },
});
