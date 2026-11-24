import { MonitoringCard } from "@/modules/thrapp/monitoring/components/monitoring-card";
import {
  MOCK_BOOSTING_TOTALS,
  MOCK_TANK_TOTALS,
} from "@/modules/thrapp/monitoring/monitoring.mock";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { StateDistribution } from ".";

const meta = {
  title: "THRS/Monitoring/StateDistribution",
  component: StateDistribution,
  parameters: { layout: "padded" },
  args: { header: "Mode", totals: MOCK_BOOSTING_TOTALS },
  render: (args) => ({
    components: { MonitoringCard, StateDistribution },
    setup: () => ({ args }),
    template: `
      <MonitoringCard title="Boost mode distribution" class="max-w-[920px]">
        <StateDistribution v-bind="args" />
      </MonitoringCard>`,
  }),
} satisfies Meta<typeof StateDistribution>;

export default meta;
type Story = StoryObj<typeof meta>;

export const BoostMode: Story = {};
export const TankStates: Story = { args: { header: "Tank state", totals: MOCK_TANK_TOTALS } };
export const OneState: Story = { args: { totals: MOCK_BOOSTING_TOTALS.slice(0, 1) } };
export const Empty: Story = { args: { totals: [] } };
export const Loading: Story = { args: { loading: true } };
export const Failed: Story = { args: { error: "GreptimeDB timed out" } };
