import { ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import {
  MOCK_BANDS,
  MOCK_FILLING,
  MOCK_MANY_SENSORS,
  MOCK_RANGE,
  MOCK_TANK_TEMPERATURES,
  MOCK_TEMPERATURE_LIMITS,
  MOCK_WITH_GAP,
} from "@/modules/thrapp/monitoring/monitoring.mock";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { TrendChart } from ".";

const meta = {
  title: "THRS/Monitoring/TrendChart",
  component: TrendChart,
  parameters: { layout: "padded" },
  args: {
    range: MOCK_RANGE,
    unit: "°C",
    lines: MOCK_TANK_TEMPERATURES,
    overlays: [
      { key: "BOOSTING_MODE", label: "Boost mode overlay", bands: MOCK_BANDS, shown: true },
      {
        key: "FILLING_MODE",
        label: "Fill mode overlay",
        bands: MOCK_FILLING.map(({ label, mode, start, end }) => ({ label, mode, start, end })),
        shown: false,
      },
    ],
    limits: MOCK_TEMPERATURE_LIMITS,
  },
  render: (args) => ({
    components: { TrendChart },
    setup: () => ({ args }),
    template: `<div class="max-w-[1500px]"><TrendChart v-bind="args" /></div>`,
  }),
} satisfies Meta<typeof TrendChart>;

export default meta;
type Story = StoryObj<typeof meta>;

export const TankTemperatures: Story = {};

export const TankLevels: Story = {
  args: {
    unit: "L",
    lines: MOCK_TANK_TEMPERATURES.map((line) => ({
      name: line.name.replace("temperature", "level"),
      points: line.points.map(([time, value]) => [time, value === null ? null : value * 3.4]),
    })),
    limits: {
      lower: { name: "Minimum fill", points: [[MOCK_RANGE.start, 60]] },
      upper: { name: "Maximum fill", points: [[MOCK_RANGE.start, 230]] },
    },
  },
};

/** Past eight series the hues repeat with a dashed line. */
export const ManySensors: Story = {
  args: { lines: MOCK_MANY_SENSORS, limits: {} },
};

/** Missing samples break the line instead of joining across the gap. */
export const WithGap: Story = {
  args: { unit: "bar", lines: MOCK_WITH_GAP, limits: {} },
};

/** A click on a group shows only its lines. */
export const Grouped: Story = {
  args: {
    lines: MOCK_MANY_SENSORS,
    limits: {},
    legendGroups: [
      { key: "boilers", label: "Boilers", names: MOCK_MANY_SENSORS.slice(0, 3).map((l) => l.name) },
      {
        key: "boosting",
        label: "Boosting circuit",
        names: MOCK_MANY_SENSORS.slice(3, 5).map((l) => l.name),
      },
    ],
  },
};

export const WithoutBands: Story = { args: { overlays: [], limits: {} } };

export const ManualPeriod: Story = {
  args: {
    overlays: [
      {
        key: "BOOSTING_MODE",
        label: "Boost mode overlay",
        shown: true,
        bands: [
          {
            label: "Manual",
            mode: ModeBadgeMode.ManualControl,
            start: MOCK_RANGE.start + 60 * 60_000,
            end: MOCK_RANGE.start + 120 * 60_000,
          },
        ],
      },
    ],
  },
};

/** Heat per source, stacked. */
export const Stacked: Story = {
  args: { kind: "stacked", unit: "kW", overlays: [], limits: {} },
};

export const Empty: Story = { args: { lines: [], limits: {} } };
export const Loading: Story = { args: { loading: true } };
export const Failed: Story = { args: { lines: [], error: "GreptimeDB timed out" } };
