import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../data";
import { BiminiString, MimicWithMiniMapProps, MiniMapLayout } from "./mini-map.types";

/**
 * Lays out a mini map beside the diagram, or above it on a portrait screen. The mini map is scaled
 * to `mapHeight` and the narrower (or lower) of the two is centred on the other.
 */
export function getMiniMapLayout(
  { diagram, map, mapHeight, gap = 40 }: MimicWithMiniMapProps,
  portrait: boolean,
): MiniMapLayout {
  const mapSize = { width: (mapHeight * map.width) / map.height, height: mapHeight };
  const diagramSize = { width: diagram.width, height: diagram.height };

  if (portrait) {
    const width = Math.max(mapSize.width, diagramSize.width);
    return {
      width,
      height: mapSize.height + gap + diagramSize.height,
      map: { ...mapSize, x: (width - mapSize.width) / 2, y: 0 },
      diagram: { ...diagramSize, x: (width - diagramSize.width) / 2, y: mapSize.height + gap },
    };
  }

  const height = Math.max(mapSize.height, diagramSize.height);
  return {
    width: mapSize.width + gap + diagramSize.width,
    height,
    map: { ...mapSize, x: 0, y: (height - mapSize.height) / 2 },
    diagram: { ...diagramSize, x: mapSize.width + gap, y: (height - diagramSize.height) / 2 },
  };
}

/** The props of the bimini strings on a mini map: their layout and their PVT string context. */
export function toBiminiStringProps(strings: BiminiString[]) {
  const getPvtString = getTooltipContext(MimicComponentType.PvtString);
  return strings.map(({ field, ...layout }) => ({ ...layout, ...getPvtString(field) }));
}
