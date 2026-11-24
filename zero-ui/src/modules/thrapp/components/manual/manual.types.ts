/** The control version a manual describes, as stamped by the thrs-module-manual skill. */
export type ManualStamp = {
  version: string;
  /** ISO date the manual was stamped, `YYYY-MM-DD`. */
  issued: string;
};

export type ManualSection = {
  id: string;
  title: string;
};
