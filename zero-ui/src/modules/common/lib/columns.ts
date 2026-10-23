import { useResizeObserver } from "@vueuse/core";
import { isEqual } from "lodash";
import { computed, type MaybeRefOrGetter, onUpdated, type Ref, ref, toValue, watch } from "vue";

/** Marks the element of a group; its value is the group key. */
export const COLUMN_GROUP_ATTRIBUTE = "data-column-group";
/** Marks the element of an item inside a group, in the same order as the group's items. */
export const COLUMN_ITEM_ATTRIBUTE = "data-column-item";

export type ColumnGroup<Item> = { key: string; items: Item[] };
export type ColumnSegmentedGroup<Item> = { key: string; segments: Item[][] };

/**
 * Splits groups that are laid out in CSS columns into segments, one per column the group spans, so
 * each segment can start with its own (repeated) header.
 *
 * Render every group with `COLUMN_GROUP_ATTRIBUTE` set to its key and every item with
 * `COLUMN_ITEM_ATTRIBUTE`. After layout, the items that start a new column are measured, and the
 * returned groups are split at those items. Rendering a header moves content, so the measurement
 * settles over a few passes; `maxPasses` prevents oscillation when a header tips an item back and
 * forth between columns.
 */
export const useColumnSegments = <Item>(
  container: Readonly<Ref<HTMLElement | null | undefined>>,
  groups: MaybeRefOrGetter<ColumnGroup<Item>[]>,
  { maxPasses = 3 }: { maxPasses?: number } = {},
) => {
  const columnBreaks = ref<Record<string, number[]>>({});
  let passes = 0;

  const measure = () => {
    if (!container.value || passes >= maxPasses) return;
    passes++;

    const next = Object.fromEntries(
      [...container.value.querySelectorAll<HTMLElement>(`[${COLUMN_GROUP_ATTRIBUTE}]`)].map(
        (group) => {
          const lefts = [...group.querySelectorAll<HTMLElement>(`[${COLUMN_ITEM_ATTRIBUTE}]`)].map(
            (item) => Math.round(item.getBoundingClientRect().left),
          );
          const breaks = lefts.flatMap((left, index) =>
            index > 0 && left > lefts[index - 1] ? [index] : [],
          );
          return [group.getAttribute(COLUMN_GROUP_ATTRIBUTE)!, breaks];
        },
      ),
    );

    if (!isEqual(next, columnBreaks.value)) columnBreaks.value = next;
  };

  useResizeObserver(container, () => {
    passes = 0;
    measure();
  });
  watch(
    () => toValue(groups),
    () => {
      columnBreaks.value = {};
      passes = 0;
    },
  );
  onUpdated(measure);

  return computed<ColumnSegmentedGroup<Item>[]>(() =>
    toValue(groups).map(({ key, items }) => {
      const starts = [0, ...(columnBreaks.value[key] ?? [])];
      return {
        key,
        segments: starts.map((start, index) => items.slice(start, starts[index + 1])),
      };
    }),
  );
};
