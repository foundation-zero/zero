import { flushPromises, mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { Component, defineComponent, h } from "vue";
import { createI18n } from "vue-i18n";
import { createMemoryHistory, createRouter } from "vue-router";
import { TOOLTIPS } from ".";
import {
  createTooltipContext,
  provideTooltipContext,
  TooltipContext,
} from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import {
  AirTrapVesselInstance,
  ExpansionTankInstance,
  ExpansionValveInstance,
  PyranometerInstance,
} from "../instances";
import { MimicComponentFieldsMap } from "../modules";
import { DC_EXPANSION_TANK_DATA } from "../modules/dc/data/expansion-tanks";
import { DC_EXPANSION_VALVE_DATA } from "../modules/dc/data/expansion-valves";
import { DRIVES_EXPANSION_TANK_DATA } from "../modules/drives/data/expansion-tanks";
import { DRIVES_EXPANSION_VALVE_DATA } from "../modules/drives/data/expansion-valves";
import { PCM_AIR_TRAP_VESSEL_DATA } from "../modules/pcm/data/air-trap-vessels";
import { PVT_EXPANSION_TANK_DATA } from "../modules/pvt/data/expansion-tanks";
import { PVT_EXPANSION_VALVE_DATA } from "../modules/pvt/data/expansion-valves";
import { PVT_PYRANOMETER_DATA } from "../modules/pvt/data/pyranometers";
import { THRUSTERS_EXPANSION_TANK_DATA } from "../modules/thrusters/data/expansion-tanks";
import { THRUSTERS_EXPANSION_VALVE_DATA } from "../modules/thrusters/data/expansion-valves";
import { deserializeField, serializeField } from "../providers";

const DC_MIMIC_DATA = { ...DC_EXPANSION_TANK_DATA, ...DC_EXPANSION_VALVE_DATA };
const DRIVES_MIMIC_DATA = { ...DRIVES_EXPANSION_TANK_DATA, ...DRIVES_EXPANSION_VALVE_DATA };
const PCM_MIMIC_DATA = PCM_AIR_TRAP_VESSEL_DATA;
const PVT_MIMIC_DATA = {
  ...PVT_EXPANSION_TANK_DATA,
  ...PVT_EXPANSION_VALVE_DATA,
  ...PVT_PYRANOMETER_DATA,
};
const THRUSTERS_MIMIC_DATA = {
  ...THRUSTERS_EXPANSION_TANK_DATA,
  ...THRUSTERS_EXPANSION_VALVE_DATA,
};

const cases: {
  module: string;
  data: Partial<MimicComponentFieldsMap>;
  type: MimicComponentType;
  tag: string;
  instance: Component;
}[] = [
  {
    module: "pvt",
    data: PVT_MIMIC_DATA,
    type: MimicComponentType.ExpansionTank,
    tag: "1040-01",
    instance: ExpansionTankInstance,
  },
  {
    module: "pvt",
    data: PVT_MIMIC_DATA,
    type: MimicComponentType.ExpansionValve,
    tag: "1041-01",
    instance: ExpansionValveInstance,
  },
  {
    module: "pvt",
    data: PVT_MIMIC_DATA,
    type: MimicComponentType.Pyranometer,
    tag: "9044",
    instance: PyranometerInstance,
  },
  {
    module: "pvt",
    data: PVT_MIMIC_DATA,
    type: MimicComponentType.Pyranometer,
    tag: "9043",
    instance: PyranometerInstance,
  },
  {
    module: "dc",
    data: DC_MIMIC_DATA,
    type: MimicComponentType.ExpansionTank,
    tag: "1040-05",
    instance: ExpansionTankInstance,
  },
  {
    module: "dc",
    data: DC_MIMIC_DATA,
    type: MimicComponentType.ExpansionValve,
    tag: "1041-06",
    instance: ExpansionValveInstance,
  },
  {
    module: "drives",
    data: DRIVES_MIMIC_DATA,
    type: MimicComponentType.ExpansionTank,
    tag: "1040-04",
    instance: ExpansionTankInstance,
  },
  {
    module: "drives",
    data: DRIVES_MIMIC_DATA,
    type: MimicComponentType.ExpansionValve,
    tag: "1041-05",
    instance: ExpansionValveInstance,
  },
  {
    module: "thrusters",
    data: THRUSTERS_MIMIC_DATA,
    type: MimicComponentType.ExpansionTank,
    tag: "1092",
    instance: ExpansionTankInstance,
  },
  {
    module: "thrusters",
    data: THRUSTERS_MIMIC_DATA,
    type: MimicComponentType.ExpansionValve,
    tag: "1041-04",
    instance: ExpansionValveInstance,
  },
  {
    module: "pcm",
    data: PCM_MIMIC_DATA,
    type: MimicComponentType.AirTrapVessel,
    tag: "1084",
    instance: AirTrapVesselInstance,
  },
];

describe("equipment tooltips", () => {
  it.each(cases)(
    "opens $module $type $tag from its instance",
    async ({ data, type, tag, instance }) => {
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [{ path: "/", component: { render: () => null } }],
      });
      await router.push("/");
      await router.isReady();

      let context: TooltipContext | undefined;
      const componentData = data[type]![tag]!;
      const wrapper = mount(
        defineComponent({
          setup() {
            context = createTooltipContext(data);
            provideTooltipContext(context);
            return () => h("svg", [h(instance, componentData)]);
          },
        }),
        {
          global: {
            plugins: [router, createI18n({ legacy: false, locale: "en", messages: { en: {} } })],
          },
        },
      );

      expect(componentData.tooltip?.yardTag).toBe(tag);
      expect(TOOLTIPS[type]).toBeDefined();
      await wrapper.find("g").trigger("click");
      await flushPromises();

      const serialized = serializeField(componentData.source);
      expect(router.currentRoute.value.query.tooltip).toBe(serialized);
      expect(context?.findTooltipContext(deserializeField(String(serialized))!)?.[0]).toBe(type);
      expect(context?.data.value?.tooltip?.yardTag).toBe(tag);
      expect(context?.component.value).not.toBeNull();
      wrapper.unmount();
    },
  );
});
