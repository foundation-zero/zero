import { MOCK_ANNOTATIONS, MOCK_RANGE } from "@/modules/thrapp/monitoring/monitoring.mock";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { ref } from "vue";
import { AnnotationToolbar } from ".";

const meta = {
  title: "THRS/Monitoring/AnnotationToolbar",
  component: AnnotationToolbar,
  parameters: { layout: "padded" },
  args: {
    annotations: MOCK_ANNOTATIONS,
    defaultTime: MOCK_RANGE.end,
    shown: ["CREW", "PARAMETERS", "ALARM"],
    author: "",
  },
  render: (args) => ({
    components: { AnnotationToolbar },
    setup: () => ({ args, shown: ref(args.shown), author: ref(args.author) }),
    template: `<AnnotationToolbar v-bind="args" v-model:shown="shown" v-model:author="author" />`,
  }),
} satisfies Meta<typeof AnnotationToolbar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const AlarmsHidden: Story = { args: { shown: ["CREW", "PARAMETERS"] } };
export const SaveFailed: Story = { args: { error: "GreptimeDB timed out" } };
