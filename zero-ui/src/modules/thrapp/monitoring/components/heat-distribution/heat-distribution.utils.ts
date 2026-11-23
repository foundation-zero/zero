import { TOOLTIP_CLASS } from "@/modules/thrapp/monitoring/monitoring.consts";
import type { TotalRow } from "@/modules/thrapp/monitoring/monitoring.types";
import type { EChartsOption } from "echarts";
import { formatReading } from "../latest-values-table/latest-values-table.utils";

/** Sources that delivered anything, so empty ones don't take a slice or a tile. */
export const delivered = (rows: TotalRow[]) => rows.filter((row) => row.value > 0);

export const share = (value: number, rows: TotalRow[]) => {
  const total = rows.reduce((sum, row) => sum + row.value, 0);
  return total > 0 ? Math.round((value / total) * 100) : 0;
};

const tooltip = (rows: TotalRow[], unit: string) => ({
  appendTo: "body",
  backgroundColor: "transparent",
  borderWidth: 0,
  padding: 0,
  extraCssText: "box-shadow: none;",
  formatter: (params: unknown) => {
    const { name, value } = params as { name: string; value: number };
    return `<div class="${TOOLTIP_CLASS}"><div class="font-semibold">${name}</div>${formatReading(value, unit)} · ${share(value, rows)}%</div>`;
  },
});

/** Tiles sized by energy, labelled with the source and its share. */
export function treemapOption(rows: TotalRow[], unit: string, labelColor: string): EChartsOption {
  const shown = delivered(rows);
  return {
    animation: false,
    tooltip: tooltip(shown, unit),
    series: [
      {
        type: "treemap",
        data: shown.map((row) => ({
          name: row.shortName ?? row.asset,
          value: row.value,
          itemStyle: { color: row.color },
        })),
        roam: false,
        nodeClick: false,
        breadcrumb: { show: false },
        width: "100%",
        height: "100%",
        top: 0,
        left: 0,
        itemStyle: { gapWidth: 2, borderColor: "transparent", borderRadius: 4 },
        label: {
          color: labelColor,
          fontSize: 13,
          fontWeight: 600,
          formatter: ({ name, value }: { name: string; value?: unknown }) =>
            `${name}\n${formatReading(Number(value), unit)} · ${share(Number(value), shown)}%`,
        },
        emphasis: { disabled: true },
      },
    ],
  };
}

/** A pie of the energy per source, with a surface gap between slices. */
export function pieOption(rows: TotalRow[], unit: string, gapColor: string): EChartsOption {
  const shown = delivered(rows);
  return {
    animation: false,
    tooltip: { trigger: "item", ...tooltip(shown, unit) },
    series: [
      {
        type: "pie",
        radius: ["0%", "92%"],
        data: shown.map((row) => ({
          name: row.shortName ?? row.asset,
          value: row.value,
          itemStyle: { color: row.color },
        })),
        label: { show: false },
        itemStyle: { borderColor: gapColor, borderWidth: 2 },
        emphasis: { scale: false },
      },
    ],
  };
}
