import { MOCK_LEVELS } from "@/modules/thrapp/monitoring/monitoring.mock";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { LatestValuesTable } from ".";

const meta = {
  title: "THRS/Monitoring/LatestValuesTable",
  component: LatestValuesTable,
  parameters: { layout: "padded" },
  args: { rows: MOCK_LEVELS, valueHeader: "Level", unit: "L", totals: true },
  render: (args) => ({
    components: { LatestValuesTable },
    setup: () => ({ args }),
    template: `<div class="w-[367px]"><LatestValuesTable v-bind="args" /></div>`,
  }),
} satisfies Meta<typeof LatestValuesTable>;

export default meta;
type Story = StoryObj<typeof meta>;

/** Tank 3 has not reported for 10 minutes, so its age turns orange. */
export const TankLevels: Story = {};

export const Temperatures: Story = {
  args: {
    valueHeader: "Temperature",
    unit: "°C",
    totals: false,
    rows: [
      {
        asset: "[50001038-45] dhw-temperature-tank1",
        value: 58.2441,
        timestamp: Date.now() - 2_000,
      },
      {
        asset: "[50001038-44] dhw-temperature-tank2",
        value: 49.4854,
        timestamp: Date.now() - 3_000,
      },
    ],
  },
};

export const NeverReported: Story = {
  args: { totals: false, rows: [{ asset: "Tank 1", value: null, timestamp: null }] },
};
