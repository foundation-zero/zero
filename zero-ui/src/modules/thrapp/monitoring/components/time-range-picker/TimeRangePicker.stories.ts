import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import { TimeRangePicker } from ".";

const HOUR = 3_600_000;

const meta = {
  title: "THRS/Monitoring/TimeRangePicker",
  component: TimeRangePicker,
  args: { modelValue: { span: 6 * HOUR, end: null }, interval: 30_000 },
  render: (args) => ({
    components: { TimeRangePicker },
    setup: () => {
      const range = ref(args.modelValue);
      const interval = ref(args.interval);
      return { range, interval, onRefresh: args.onRefresh };
    },
    template: `
      <div class="flex flex-col items-end gap-4">
        <TimeRangePicker v-model="range" v-model:interval="interval" @refresh="onRefresh" />
        <code class="text-muted-foreground text-xs">{{ range }} · every {{ interval }} ms</code>
      </div>`,
  }),
} satisfies Meta<typeof TimeRangePicker>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Live: Story = {};

/** After « the window ends in the past; » brings it back to now. */
export const PastWindow: Story = {
  args: { modelValue: { span: 6 * HOUR, end: Date.now() - 6 * HOUR }, interval: 0 },
};

/** Zoomed out from a preset to a span without a name. */
export const CustomSpan: Story = { args: { modelValue: { span: 48 * HOUR, end: null } } };
