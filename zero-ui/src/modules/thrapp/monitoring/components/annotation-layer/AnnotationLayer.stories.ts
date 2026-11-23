import { MOCK_ANNOTATIONS, MOCK_RANGE } from "@/modules/thrapp/monitoring/monitoring.mock";
import type { Meta, StoryObj } from "@storybook/vue3-vite";
import { AnnotationLayer } from ".";

const meta = {
  title: "THRS/Monitoring/AnnotationLayer",
  component: AnnotationLayer,
  parameters: { layout: "padded" },
  args: {
    annotations: MOCK_ANNOTATIONS,
    shown: new Set(["CREW", "PARAMETERS", "ALARM"]),
    range: MOCK_RANGE,
    top: 16,
    bottom: 16,
  },
  render: (args) => ({
    components: { AnnotationLayer },
    setup: () => ({ args }),
    template: `<div class="bg-background border-border relative h-60 max-w-[1200px] rounded-lg border"><AnnotationLayer v-bind="args" /></div>`,
  }),
} satisfies Meta<typeof AnnotationLayer>;

export default meta;
type Story = StoryObj<typeof meta>;

/** Hover an icon for the note; the crew note written here can be deleted. */
export const AllKinds: Story = {};

/** Kinds switched off in the toolbar leave no marker. */
export const OnlyCrewNotes: Story = { args: { shown: new Set(["CREW"]) } };
