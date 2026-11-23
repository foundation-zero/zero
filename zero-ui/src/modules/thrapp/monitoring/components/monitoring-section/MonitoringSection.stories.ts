import { MonitoringCard } from "@/modules/thrapp/monitoring/components/monitoring-card";
import { StateDistribution } from "@/modules/thrapp/monitoring/components/state-distribution";
import { StateTimeline } from "@/modules/thrapp/monitoring/components/state-timeline";
import {
  MOCK_BOOSTING,
  MOCK_BOOSTING_TOTALS,
  MOCK_RANGE,
} from "@/modules/thrapp/monitoring/monitoring.mock";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { MonitoringSection } from ".";

const meta = {
  title: "THRS/Monitoring/MonitoringSection",
  component: MonitoringSection,
  parameters: { layout: "padded" },
  args: { title: "Modes", storageKey: "storybook-modes", level: "section" },
  render: (args) => ({
    components: { MonitoringSection, MonitoringCard, StateDistribution, StateTimeline },
    setup: () => ({
      args,
      rows: [{ label: "Boosting", segments: MOCK_BOOSTING }],
      range: MOCK_RANGE,
      totals: MOCK_BOOSTING_TOTALS,
    }),
    template: `
      <MonitoringSection v-bind="args">
        <div class="grid gap-4 lg:grid-cols-2">
          <MonitoringCard title="Boost mode distribution">
            <StateDistribution header="Mode" :totals="totals" />
          </MonitoringCard>
          <MonitoringCard title="Module mode timeline">
            <StateTimeline :rows="rows" :range="range" />
          </MonitoringCard>
        </div>
      </MonitoringSection>`,
  }),
} satisfies Meta<typeof MonitoringSection>;

export default meta;
type Story = StoryObj<typeof meta>;

/** Click the heading to collapse; the choice is remembered per viewer. */
export const Section: Story = {};
export const Group: Story = {
  args: { title: "Tank temperatures", storageKey: "storybook-group", level: "group" },
};
