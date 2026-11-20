import type { Alarm } from "../types";

export function isActive(alarm: Pick<Alarm, "active"> | null): boolean {
  return !!alarm?.active;
}

/** Calls of the returned function while `request` is still running are skipped. */
export function skipWhilePending(request: () => Promise<void>): () => Promise<void> {
  let pending = false;
  return async () => {
    if (pending) {
      return;
    }
    pending = true;
    try {
      await request();
    } finally {
      pending = false;
    }
  };
}
