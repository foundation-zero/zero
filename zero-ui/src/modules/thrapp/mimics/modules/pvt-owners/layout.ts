import { SolarPanelOrientation, SolarPanelSize } from "../../components/solar-panel";
import { BiminiString } from "../pvt-main/layout";

/**
 * Top-down layout of the owners bimini strings, in the coordinates of its Figma frame (302 x 445).
 * The owners bimini is drawn at about twice the scale of the main bimini, so its panels are given
 * their rendered size.
 */
export const OWNERS_BIMINI_STRINGS: BiminiString[] = [
  {
    string: "6",
    frame: { d: "M47.41 46.7H117.41V18.7H186.41V46.7H256.41V73.7H47.41V46.7Z" },
    label: { x: 151.91, y: 60.2 },
    panels: [
      {
        x: 47.41,
        y: 46.7,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
        width: 69,
        height: 27,
      },
      {
        x: 117.41,
        y: 46.7,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
        width: 69,
        height: 27,
      },
      {
        x: 117.41,
        y: 18.7,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
        width: 69,
        height: 27,
      },
      {
        x: 187.41,
        y: 46.7,
        size: SolarPanelSize.Small,
        orientation: SolarPanelOrientation.Landscape,
        width: 69,
        height: 27,
      },
    ],
  },
  {
    string: "5",
    frame: { x: 20.91, y: 75.7, width: 262, height: 66 },
    label: { x: 151.91, y: 108.7 },
    panels: [
      { x: 19.91, y: 74.7, width: 52, height: 68 },
      { x: 72.91, y: 74.7, width: 52, height: 68 },
      { x: 125.91, y: 74.7, width: 52, height: 68 },
      { x: 178.91, y: 74.7, width: 52, height: 68 },
      { x: 231.91, y: 74.7, width: 52, height: 68 },
    ],
  },
  {
    string: "4",
    frame: { x: 20.91, y: 144.7, width: 262, height: 66 },
    label: { x: 151.91, y: 177.7 },
    panels: [
      { x: 19.91, y: 143.7, width: 52, height: 68 },
      { x: 72.91, y: 143.7, width: 52, height: 68 },
      { x: 125.91, y: 143.7, width: 52, height: 68 },
      { x: 178.91, y: 143.7, width: 52, height: 68 },
      { x: 231.91, y: 143.7, width: 52, height: 68 },
    ],
  },
  {
    string: "3",
    frame: { d: "M30.41 212.7H273.41V264.7H204.41V280.7H99.41V264.7H30.41V212.7Z" },
    label: { x: 151.91, y: 246.7 },
    panels: [
      { x: 30.41, y: 212.7, orientation: SolarPanelOrientation.Landscape, width: 68, height: 52 },
      { x: 99.41, y: 212.7, width: 52, height: 68 },
      { x: 152.41, y: 212.7, width: 52, height: 68 },
      { x: 205.41, y: 212.7, orientation: SolarPanelOrientation.Landscape, width: 68, height: 52 },
    ],
  },
  {
    string: "2",
    frame: {
      d: "M30.41 265.7H98.41V281.7H205.41V265.7H273.41V317.7H204.41V349.7H99.41V317.7H30.41V265.7Z",
    },
    label: { x: 151.91, y: 315.7 },
    panels: [
      { x: 30.41, y: 265.7, orientation: SolarPanelOrientation.Landscape, width: 68, height: 52 },
      { x: 99.41, y: 281.7, width: 52, height: 68 },
      { x: 152.41, y: 281.7, width: 52, height: 68 },
      { x: 205.41, y: 265.7, orientation: SolarPanelOrientation.Landscape, width: 68, height: 52 },
    ],
  },
  {
    string: "1",
    frame: {
      d: "M46.41 318.7H98.41V350.7H205.41V318.7H257.41V386.7H204.41V418.7H99.41V386.7H46.41V318.7Z",
    },
    label: { x: 151.91, y: 384.7 },
    panels: [
      { x: 46.41, y: 318.7, width: 52, height: 68 },
      { x: 99.41, y: 350.7, width: 52, height: 68 },
      { x: 152.41, y: 350.7, width: 52, height: 68 },
      { x: 205.41, y: 318.7, width: 52, height: 68 },
    ],
  },
];
