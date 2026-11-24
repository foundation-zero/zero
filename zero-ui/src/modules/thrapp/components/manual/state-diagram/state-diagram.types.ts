export type DiagramSection = {
  heading?: string;
  items: Array<string>;
};

export type DiagramState = {
  id: string;
  title: string;
  /** Mode badge colour, from the diagram's `class <state> <ModeBadgeMode>` line. */
  mode?: string;
  sections: Array<DiagramSection>;
};

export type DiagramTransition = {
  from: string;
  to: string;
  /** The label's lines, split where the source has `<br/>`. */
  label: Array<string>;
};

export type StateDiagram = {
  initial?: string;
  /** In drawing order, left to right: the initial state first, then as declared. */
  states: Array<DiagramState>;
  transitions: Array<DiagramTransition>;
};

export type EdgeSide = "top" | "bottom";

/** A transition with its route: above the row of states when it runs right, below when left. */
export type PlannedEdge = DiagramTransition & {
  side: EdgeSide;
  /** 0 is the lane nearest the states. */
  lane: number;
  /** Where the edge leaves and enters its states, as a fraction of their width. */
  fromPort: number;
  toPort: number;
};
