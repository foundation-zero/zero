import { ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import { MonitoringCard } from "@/modules/thrapp/monitoring/components/monitoring-card";
import {
  MOCK_BOOSTING,
  MOCK_FILLING,
  MOCK_RANGE,
  MOCK_TANKS,
} from "@/modules/thrapp/monitoring/monitoring.mock";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { StateTimeline } from ".";

const meta = {
  title: "THRS/Monitoring/StateTimeline",
  component: StateTimeline,
  parameters: { layout: "padded" },
  args: {
    range: MOCK_RANGE,
    rows: [{ label: "Boosting", segments: MOCK_BOOSTING }],
  },
  render: (args) => ({
    components: { MonitoringCard, StateTimeline },
    setup: () => ({ args }),
    template: `
      <MonitoringCard title="Module mode timeline" class="max-w-[920px]">
        <StateTimeline v-bind="args" />
      </MonitoringCard>`,
  }),
} satisfies Meta<typeof StateTimeline>;

export default meta;
type Story = StoryObj<typeof meta>;

export const BoostMode: Story = {};
export const FillingMode: Story = {
  args: { rows: [{ label: "Filling", segments: MOCK_FILLING }] },
};
export const TankStates: Story = {
  args: {
    rows: MOCK_TANKS.map((segments, index) => ({ label: `Tank ${index + 1}`, segments })),
  },
};

/** Short segments drop their label and keep it in the hover title. */
export const ManyShortSegments: Story = {
  args: {
    rows: [
      {
        label: "Boosting",
        segments: Array.from({ length: 40 }, (_, index) => ({
          state: index % 2 ? "idle" : "boosting_heatpump",
          label: index % 2 ? "Idle" : "Boosting HP",
          mode: index % 2 ? ModeBadgeMode.Idle : ModeBadgeMode.BoostingHigh,
          start: MOCK_RANGE.start + index * 6 * 60_000,
          end: MOCK_RANGE.start + (index + 1) * 6 * 60_000,
        })),
      },
    ],
  },
};

/** A signal that stopped reporting leaves the rest of the bar empty. */
export const StoppedReporting: Story = {
  args: { rows: [{ label: "Boosting", segments: MOCK_BOOSTING.slice(0, 3) }] },
};
export const Empty: Story = { args: { rows: [{ label: "Boosting", segments: [] }] } };
export const Loading: Story = { args: { loading: true } };
export const Failed: Story = { args: { error: "GreptimeDB timed out" } };
