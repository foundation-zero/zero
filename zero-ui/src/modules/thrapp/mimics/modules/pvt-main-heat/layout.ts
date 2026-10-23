import { SolarPanelOrientation, SolarPanelSize } from "../../components/solar-panel";
import { SolarPanelStringProps } from "../../components/solar-panel-string";

export type BiminiString = Omit<SolarPanelStringProps, "yieldRatio"> & { string: string };

/**
 * Top-down layout of the main bimini strings, in the coordinates of the mimic.
 * String 3 is split over the left and right side and therefore has two shapes.
 */
export const MAIN_BIMINI_STRINGS: BiminiString[] = [
  {
    string: "13",
    frame: { x: 51.91, y: 24.08, width: 181, height: 13 },
    label: { x: 142.67, y: 30.36 },
    panels: [
      {
        x: 51.41,
        y: 23.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
      {
        x: 87.91,
        y: 23.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
      {
        x: 124.41,
        y: 23.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
      {
        x: 160.91,
        y: 23.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
      {
        x: 197.41,
        y: 23.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
    ],
  },
  {
    string: "12",
    frame: { x: 51.91, y: 38.58, width: 181, height: 26 },
    label: { x: 142.67, y: 50.21 },
    panels: [
      { x: 51.41, y: 38.08, orientation: SolarPanelOrientation.Landscape },
      { x: 87.91, y: 38.08, orientation: SolarPanelOrientation.Landscape },
      { x: 124.41, y: 38.08, orientation: SolarPanelOrientation.Landscape },
      { x: 160.91, y: 38.08, orientation: SolarPanelOrientation.Landscape },
      { x: 197.41, y: 38.08, orientation: SolarPanelOrientation.Landscape },
    ],
  },
  {
    string: "11.1",
    frame: { x: 13.91, y: 66.08, width: 123, height: 35 },
    label: { x: 70.89, y: 82.96 },
    panels: [
      { x: 13.41, y: 65.58, size: SolarPanelSize.Small },
      { x: 27.91, y: 65.58 },
      { x: 55.41, y: 65.58 },
      { x: 82.91, y: 65.58 },
      { x: 110.41, y: 65.58 },
    ],
  },
  {
    string: "11.2",
    frame: { x: 146.91, y: 66.08, width: 123, height: 35 },
    label: { x: 206.27, y: 82.96 },
    panels: [
      { x: 146.41, y: 65.58 },
      { x: 173.91, y: 65.58 },
      { x: 201.41, y: 65.58 },
      { x: 228.91, y: 65.58 },
      { x: 256.41, y: 65.58, size: SolarPanelSize.Small },
    ],
  },
  {
    string: "9",
    frame: { x: 11.91, y: 102.58, width: 136, height: 35 },
    label: { x: 75.39, y: 117.9 },
    panels: [
      { x: 11.41, y: 102.08 },
      { x: 38.91, y: 102.08 },
      { x: 66.41, y: 102.08 },
      { x: 93.91, y: 102.08 },
      { x: 121.41, y: 102.08 },
    ],
  },
  {
    string: "10",
    frame: { x: 149.41, y: 102.58, width: 123, height: 35 },
    label: { x: 209.77, y: 117.9 },
    panels: [
      { x: 148.91, y: 102.08 },
      { x: 176.41, y: 102.08 },
      { x: 203.91, y: 102.08 },
      { x: 231.41, y: 102.08 },
      { x: 258.91, y: 102.08, size: SolarPanelSize.Small },
    ],
  },
  {
    string: "8.1",
    frame: { x: 18.91, y: 139.08, width: 108.5, height: 35 },
    label: { x: 72.39, y: 155.78 },
    panels: [
      { x: 18.41, y: 138.58 },
      { x: 45.91, y: 138.58 },
      { x: 73.41, y: 138.58 },
      { x: 100.91, y: 138.58 },
    ],
  },
  {
    string: "8.2",
    frame: { x: 156.41, y: 139.08, width: 108.5, height: 35 },
    label: { x: 209.98, y: 155.78 },
    panels: [
      { x: 155.91, y: 138.58 },
      { x: 183.41, y: 138.58 },
      { x: 210.91, y: 138.58 },
      { x: 238.41, y: 138.58 },
    ],
  },
  {
    string: "7.1",
    frame: { x: 18.91, y: 175.58, width: 108.5, height: 35 },
    label: { x: 73.39, y: 192.88 },
    panels: [
      { x: 18.41, y: 175.08 },
      { x: 45.91, y: 175.08 },
      { x: 73.41, y: 175.08 },
      { x: 100.91, y: 175.08 },
    ],
  },
  {
    string: "7.2",
    frame: { x: 156.41, y: 175.58, width: 108.5, height: 35 },
    label: { x: 210.48, y: 192.88 },
    panels: [
      { x: 155.91, y: 175.08 },
      { x: 183.41, y: 175.08 },
      { x: 210.91, y: 175.08 },
      { x: 238.41, y: 175.08 },
    ],
  },
  {
    string: "6.1",
    frame: { x: 18.91, y: 212.08, width: 108.5, height: 35 },
    label: { x: 72.39, y: 228.79 },
    panels: [
      { x: 18.41, y: 211.58 },
      { x: 45.91, y: 211.58 },
      { x: 73.41, y: 211.58 },
      { x: 100.91, y: 211.58 },
    ],
  },
  {
    string: "6.2",
    frame: { x: 156.41, y: 212.08, width: 108.5, height: 35 },
    label: { x: 209.98, y: 228.79 },
    panels: [
      { x: 155.91, y: 211.58 },
      { x: 183.41, y: 211.58 },
      { x: 210.91, y: 211.58 },
      { x: 238.41, y: 211.58 },
    ],
  },
  {
    string: "5.1",
    frame: { x: 18.91, y: 248.58, width: 108.5, height: 35 },
    label: { x: 72.39, y: 262.35 },
    panels: [
      { x: 18.41, y: 248.08 },
      { x: 45.91, y: 248.08 },
      { x: 73.41, y: 248.08 },
      { x: 100.91, y: 248.08 },
    ],
  },
  {
    string: "5.2",
    frame: { x: 156.41, y: 248.58, width: 108.5, height: 35 },
    label: { x: 209.98, y: 262.35 },
    panels: [
      { x: 155.91, y: 248.08 },
      { x: 183.41, y: 248.08 },
      { x: 210.91, y: 248.08 },
      { x: 238.41, y: 248.08 },
    ],
  },
  {
    string: "4",
    frame: { x: 128.91, y: 139.08, width: 26, height: 144.5 },
    label: { x: 141.83, y: 206.74, vertical: true },
    panels: [
      { x: 128.41, y: 138.58 },
      { x: 128.41, y: 175.08 },
      { x: 128.41, y: 211.58 },
      { x: 128.41, y: 248.08 },
    ],
  },
  {
    string: "1.1",
    frame: { x: 106.41, y: 285.08, width: 35, height: 108.5 },
    label: { x: 124.06, y: 336.86, vertical: true },
    panels: [
      { x: 105.91, y: 284.58, orientation: SolarPanelOrientation.Landscape },
      { x: 105.91, y: 312.08, orientation: SolarPanelOrientation.Landscape },
      { x: 105.91, y: 339.58, orientation: SolarPanelOrientation.Landscape },
      { x: 105.91, y: 367.08, orientation: SolarPanelOrientation.Landscape },
    ],
  },
  {
    string: "1.2",
    frame: { x: 142.91, y: 285.08, width: 35, height: 108.5 },
    label: { x: 159.89, y: 337.86, vertical: true },
    panels: [
      { x: 142.41, y: 284.58, orientation: SolarPanelOrientation.Landscape },
      { x: 142.41, y: 312.08, orientation: SolarPanelOrientation.Landscape },
      { x: 142.41, y: 339.58, orientation: SolarPanelOrientation.Landscape },
      { x: 142.41, y: 367.08, orientation: SolarPanelOrientation.Landscape },
    ],
  },
  {
    string: "2.1",
    frame: { x: 69.91, y: 285.08, width: 35, height: 123 },
    label: { x: 87.8, y: 337.86, vertical: true },
    panels: [
      { x: 69.41, y: 284.58, orientation: SolarPanelOrientation.Landscape },
      { x: 69.41, y: 312.08, orientation: SolarPanelOrientation.Landscape },
      { x: 69.41, y: 339.58, orientation: SolarPanelOrientation.Landscape },
      { x: 69.41, y: 367.08, orientation: SolarPanelOrientation.Landscape },
      {
        x: 69.41,
        y: 394.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
    ],
  },
  {
    string: "2.2",
    frame: { x: 179.41, y: 285.08, width: 35, height: 123 },
    label: { x: 197.81, y: 338.86, vertical: true },
    panels: [
      { x: 178.91, y: 284.58, orientation: SolarPanelOrientation.Landscape },
      { x: 178.91, y: 312.08, orientation: SolarPanelOrientation.Landscape },
      { x: 178.91, y: 339.58, orientation: SolarPanelOrientation.Landscape },
      { x: 178.91, y: 367.08, orientation: SolarPanelOrientation.Landscape },
      {
        x: 178.91,
        y: 394.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
    ],
  },
  // Left side
  {
    string: "3",
    frame: { d: "M68.9 320.58H41.41V357.6H68.9V371.58H32.86V357.11H27.4V284.58H68.9V320.58Z" },
    label: { x: 33.21, y: 328.7, vertical: true },
    panels: [
      { x: 41.91, y: 284.58 },
      { x: 27.41, y: 284.58, size: SolarPanelSize.Small },
      { x: 27.41, y: 321.08, size: SolarPanelSize.Small },
      {
        x: 32.91,
        y: 357.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
    ],
  },
  // Right side
  {
    string: "3",
    frame: {
      d: "M215.42 320.58H242.91V357.6H215.42V371.58H251.45V357.11H256.92V284.58H215.42V320.58Z",
    },
    label: { x: 248.72, y: 330.23, vertical: true },
    panels: [
      { x: 215.41, y: 284.58 },
      { x: 242.91, y: 284.58, size: SolarPanelSize.Small },
      { x: 242.91, y: 321.08, size: SolarPanelSize.Small },
      {
        x: 215.41,
        y: 357.58,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
      },
    ],
  },
];
