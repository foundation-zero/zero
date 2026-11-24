import { MODE_COLORS, ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge";
import {
  DiagramState,
  DiagramTransition,
  EdgeSide,
  PlannedEdge,
  StateDiagram,
} from "./state-diagram.types";

/*
 * The manuals' state diagrams are Mermaid `stateDiagram-v2` sources, drawn here
 * as the design has them, on screen and in print alike: the states in a row as
 * cards, transitions to the right routed above the row and transitions to the
 * left below it, in lanes. Only the subset of the syntax the manuals use is
 * read; anything else falls back to Mermaid.
 */

type Line =
  | { kind: "state"; id: string; title: string }
  | { kind: "description"; id: string; text: string }
  | { kind: "transition"; from: string; to: string; label?: string }
  | { kind: "class"; ids: Array<string>; mode: string }
  | { kind: "ignored" };

const IGNORED = /^(?:$|stateDiagram-v2$|direction\s+\w+$|%%)/;
const STATE = /^state\s+"(?<title>[^"]+)"\s+as\s+(?<id>\w+)$/;
const TRANSITION = /^(?<from>\[\*\]|\w+)\s*-->\s*(?<to>\[\*\]|\w+)(?:\s*:\s*(?<label>.+))?$/;
const DESCRIPTION = /^(?<id>\w+)\s*:\s*(?<text>.+)$/;
const CLASS = /^class\s+(?<ids>[\w,]+)\s+(?<mode>\w+)$/;
const HEADING = /^<b>(?<heading>.*)<\/b>$/;
const LINE_BREAK = /<br\s*\/?>/;
const INITIAL = "[*]";

const stripTags = (text: string) => text.replace(/<[^>]+>/g, "").trim();

const parseLine = (line: string): Line | undefined => {
  if (IGNORED.test(line)) return { kind: "ignored" };
  const state = STATE.exec(line)?.groups;
  if (state) return { kind: "state", id: state.id, title: state.title };
  const transition = TRANSITION.exec(line)?.groups;
  if (transition) return { kind: "transition", ...transition } as Line;
  const description = DESCRIPTION.exec(line)?.groups;
  if (description) return { kind: "description", id: description.id, text: description.text };
  const assignment = CLASS.exec(line)?.groups;
  if (assignment) return { kind: "class", ids: assignment.ids.split(","), mode: assignment.mode };
  return undefined;
};

/** Reads a diagram, or says why this drawing cannot draw it. */
const readStateDiagram = (source: string): StateDiagram | string => {
  const raw = source.split("\n").map((line) => line.trim());
  const lines = raw.map(parseLine);
  const unsupported = lines.findIndex((line) => line === undefined);
  if (unsupported !== -1) return `unsupported line "${raw[unsupported]}"`;

  const states = new Map<string, DiagramState>();
  const stateOf = (id: string) =>
    states.get(id) ?? states.set(id, { id, title: id, sections: [] }).get(id)!;
  const transitions: Array<DiagramTransition> = [];
  const initials: Array<string> = [];

  for (const line of lines as Array<Line>) {
    if (line.kind === "state") stateOf(line.id).title = line.title;
    if (line.kind === "class") line.ids.forEach((id) => (stateOf(id).mode = line.mode));
    if (line.kind === "description") {
      const { sections } = stateOf(line.id);
      const heading = HEADING.exec(line.text)?.groups?.heading;
      if (heading !== undefined) sections.push({ heading: stripTags(heading), items: [] });
      else {
        if (sections.length === 0) sections.push({ items: [] });
        sections[sections.length - 1].items.push(stripTags(line.text).replace(/^•\s*/, ""));
      }
    }
    if (line.kind === "transition") {
      if (line.to === INITIAL) return `a final state, "${line.from} --> [*]"`;
      if (line.from === line.to) return `a transition from ${line.from} to itself`;
      if (line.from === INITIAL) initials.push(stateOf(line.to).id);
      else {
        const duplicate = transitions.some(({ from, to }) => from === line.from && to === line.to);
        if (duplicate) return `two transitions from ${line.from} to ${line.to}`;
        stateOf(line.from);
        stateOf(line.to);
        const label = (line.label ?? "").split(LINE_BREAK).map(stripTags).filter(Boolean);
        transitions.push({ from: line.from, to: line.to, label });
      }
    }
  }
  if (initials.length > 1) return `more than one start marker: ${initials.join(", ")}`;
  if (states.size === 0) return "no states";

  const [initial] = initials;
  const ordered = [...states.values()].sort(
    (a, b) => Number(b.id === initial) - Number(a.id === initial),
  );
  return { initial, states: ordered, transitions };
};

/** Reads a diagram, or gives undefined when it uses syntax this drawing does not support. */
export const parseStateDiagram = (source: string): StateDiagram | undefined => {
  const diagram = readStateDiagram(source);
  return typeof diagram === "string" ? undefined : diagram;
};

/** Why a diagram falls back to Mermaid, or undefined when it is drawn as cards. */
export const stateDiagramProblem = (source: string): string | undefined => {
  const diagram = readStateDiagram(source);
  return typeof diagram === "string" ? diagram : undefined;
};

const overlaps = (a: [number, number], b: [number, number]) => a[0] < b[1] && b[0] < a[1];

/**
 * Routes each transition: the side of the row it runs on, its lane there (the
 * shortest transitions nearest the states, so lines do not cross), and where it
 * leaves and enters its states.
 */
export const planEdges = ({ states, transitions }: StateDiagram): Array<PlannedEdge> => {
  const index = new Map(states.map(({ id }, i) => [id, i]));
  const span = ({ from, to }: DiagramTransition): [number, number] => {
    const [a, b] = [index.get(from)!, index.get(to)!];
    return [Math.min(a, b), Math.max(a, b)];
  };
  const sideOf = ({ from, to }: DiagramTransition): EdgeSide =>
    index.get(from)! < index.get(to)! ? "top" : "bottom";
  const length = (transition: DiagramTransition) => span(transition)[1] - span(transition)[0];

  const lanes = new Map<DiagramTransition, number>();
  (["top", "bottom"] as const).forEach((side) => {
    const taken: Array<Array<[number, number]>> = [];
    transitions
      .filter((transition) => sideOf(transition) === side)
      .sort((a, b) => length(a) - length(b))
      .forEach((transition) => {
        const free = taken.findIndex((spans) => !spans.some((s) => overlaps(s, span(transition))));
        const lane = free === -1 ? taken.push([]) - 1 : free;
        taken[lane].push(span(transition));
        lanes.set(transition, lane);
      });
  });

  // On each side of a state, edges heading left attach left of edges heading
  // right; and the further out an edge's lane, the further it attaches from the
  // way it heads, so its vertical run stays clear of the nearer lanes.
  const ports = new Map<string, number>();
  states.forEach(({ id }, position) =>
    (["top", "bottom"] as const).forEach((side) => {
      const attached = transitions.flatMap((transition, i) =>
        (["from", "to"] as const)
          .filter((end) => transition[end] === id && sideOf(transition) === side)
          .map((end) => ({
            key: `${i}:${end}`,
            left: index.get(transition[end === "from" ? "to" : "from"])! < position,
            lane: lanes.get(transition)!,
          })),
      );
      attached
        .sort((a, b) =>
          a.left !== b.left ? (a.left ? -1 : 1) : a.left ? a.lane - b.lane : b.lane - a.lane,
        )
        .forEach(({ key }, k) => ports.set(key, (k + 1) / (attached.length + 1)));
    }),
  );

  return transitions.map((transition, i) => ({
    ...transition,
    side: sideOf(transition),
    lane: lanes.get(transition)!,
    fromPort: ports.get(`${i}:from`)!,
    toPort: ports.get(`${i}:to`)!,
  }));
};

// Spacing from the design, in px.
const LANE_CLEARANCE = 32; // between the states and the labels of the lane nearest them
const LANE_GAP = 52; // between the labels of adjacent lanes
const INITIAL_INSET = 40; // left of the first state, for the initial-state dot
const INITIAL_DOT = 7; // its radius
const INITIAL_Y = 25; // its height below the top of the first state, level with the badge

const SVG = "http://www.w3.org/2000/svg";
const PARAMETER = /\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b/g;
let diagrams = 0;

const element = <K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
  children: Array<Node | string | undefined> = [],
) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  node.append(...children.filter((child) => child !== undefined));
  return node;
};

const svgElement = (tag: string, attributes: Record<string, string | number>) => {
  const node = document.createElementNS(SVG, tag);
  Object.entries(attributes).forEach(([name, value]) => node.setAttribute(name, String(value)));
  return node;
};

/** Text with parameter names as code, which the manual then links to their row. */
const richText = (text: string): Array<Node | string> =>
  text
    .split(new RegExp(`(${PARAMETER.source})`))
    .map((part, i) => (i % 2 ? element("code", undefined, [part]) : part));

const stateCard = ({ id, title, mode, sections }: DiagramState) => {
  const color = MODE_COLORS[mode as ModeBadgeMode] ?? "";
  const badge = element("span", undefined, [title]);
  badge.dataset.mode = mode ?? "";
  badge.style.backgroundColor = color;

  const card = element("div", "state-diagram-state", [
    badge,
    element("hr"),
    ...sections.map(({ heading, items }) =>
      element("div", "state-diagram-section", [
        heading ? element("p", undefined, [heading]) : undefined,
        element(
          "ul",
          undefined,
          items.map((item) => element("li", undefined, richText(item))),
        ),
      ]),
    ),
  ]);
  card.dataset.state = id;
  card.style.borderColor = color;
  return card;
};

const transitionLabel = ({ label }: PlannedEdge) =>
  element(
    "div",
    "state-diagram-label",
    label.map((line) => element("span", undefined, richText(line))),
  );

const decodeEntities = (html: string) =>
  html
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, "&");

/** A diagram's source as Mermaid reads it: the fragment's <b> and <br/> parse as markup. */
export const diagramSource = (pre: Element) => decodeEntities(pre.innerHTML);

/**
 * Draws the diagram in `pre` after it, and hides the source. Returns false,
 * drawing nothing, for a diagram to leave to Mermaid. With `fit`, a diagram
 * wider than its container is scaled down to fit, as on a printed page.
 */
export const drawStateDiagram = async (pre: HTMLElement, { fit }: { fit?: boolean } = {}) => {
  const diagram = parseStateDiagram(diagramSource(pre));
  if (!diagram) return false;
  const edges = planEdges(diagram);

  const id = `state-diagram-${++diagrams}`;
  const svg = svgElement("svg", { class: "state-diagram-edges", "aria-hidden": "true" });
  const marker = svgElement("marker", {
    id: `${id}-arrow`,
    viewBox: "0 0 10 10",
    refX: 9,
    refY: 5,
    markerWidth: 10,
    markerHeight: 10,
    markerUnits: "userSpaceOnUse",
    orient: "auto-start-reverse",
  });
  marker.append(svgElement("path", { d: "M1 1 L9 5 L1 9" }));
  const defs = svgElement("defs", {});
  defs.append(marker);
  svg.append(defs);

  const cards = diagram.states.map(stateCard);
  const row = element("div", "state-diagram-row", cards);
  const labels = edges.map(transitionLabel);
  const canvas = element("div", "state-diagram", [svg, row, ...labels]);
  pre.hidden = true;
  pre.dataset.processed = "true";
  const scroll = element("div", "state-diagram-scroll", [canvas]);
  pre.after(scroll);

  await document.fonts.ready;
  layOut({ diagram, edges, svg, row, cards, labels, markerId: marker.id });
  const scale = scroll.clientWidth / canvas.offsetWidth;
  if (fit && scale < 1) canvas.style.zoom = String(scale);
  return true;
};

type Layout = {
  diagram: StateDiagram;
  edges: Array<PlannedEdge>;
  svg: SVGElement;
  row: HTMLElement;
  cards: Array<HTMLElement>;
  labels: Array<HTMLElement>;
  markerId: string;
};

const layOut = ({ diagram, edges, svg, row, cards, labels, markerId }: Layout) => {
  const heights = labels.map((label) => label.offsetHeight);
  // Each lane is as tall as its tallest label; returns lane centres measured
  // out from the row, and how far the outermost label reaches.
  const lanesOn = (side: EdgeSide) =>
    edges
      .reduce<Array<number>>((lanes, edge, i) => {
        if (edge.side === side) lanes[edge.lane] = Math.max(lanes[edge.lane] ?? 0, heights[i]);
        return lanes;
      }, [])
      .reduce<{ centres: Array<number>; reach: number }>(
        ({ centres, reach }, height) => {
          const centre = reach + (centres.length ? LANE_GAP : LANE_CLEARANCE) + height / 2;
          return { centres: [...centres, centre], reach: centre + height / 2 };
        },
        { centres: [], reach: 0 },
      );
  const above = lanesOn("top");
  const below = lanesOn("bottom");

  row.style.paddingTop = `${above.reach}px`;
  row.style.paddingBottom = `${below.reach}px`;
  row.style.paddingLeft = diagram.initial ? `${INITIAL_INSET}px` : "0";

  // Layout offsets rather than client rects, which a CSS zoom around the manual would scale.
  // The cards' offset parent is the canvas, with the row at its origin.
  const origin = { width: row.offsetWidth, height: row.offsetHeight };
  const boxes = new Map(
    cards.map((card) => [
      card.dataset.state!,
      {
        left: card.offsetLeft - row.offsetLeft,
        width: card.offsetWidth,
        bottom: card.offsetTop - row.offsetTop + card.offsetHeight,
      },
    ]),
  );
  const top = above.reach;
  const bottom = Math.max(...[...boxes.values()].map((box) => box.bottom));

  svg.setAttribute("width", String(origin.width));
  svg.setAttribute("height", String(origin.height));
  svg.setAttribute("viewBox", `0 0 ${origin.width} ${origin.height}`);

  edges.forEach((edge, i) => {
    const from = boxes.get(edge.from)!;
    const to = boxes.get(edge.to)!;
    const x1 = from.left + from.width * edge.fromPort;
    const x2 = to.left + to.width * edge.toPort;
    const [y1, y2, lane] =
      edge.side === "top"
        ? [top, top, top - above.centres[edge.lane]]
        : [from.bottom, to.bottom, bottom + below.centres[edge.lane]];
    svg.append(
      svgElement("path", {
        d: `M${x1} ${y1} V${lane} H${x2} V${y2}`,
        "marker-end": `url(#${markerId})`,
      }),
    );
    labels[i].style.left = `${(x1 + x2) / 2}px`;
    labels[i].style.top = `${lane}px`;
  });

  if (diagram.initial) {
    const first = boxes.get(diagram.initial)!;
    const y = top + INITIAL_Y;
    svg.append(svgElement("circle", { class: "initial", cx: INITIAL_DOT, cy: y, r: INITIAL_DOT }));
    svg.append(
      svgElement("path", {
        d: `M${INITIAL_DOT * 2} ${y} H${first.left}`,
        "marker-end": `url(#${markerId})`,
      }),
    );
  }
};
