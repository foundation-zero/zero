import type { useQuery } from "@urql/vue";
import { Mock, vi } from "vitest";
import { ref, Ref } from "vue";

export type FakeQueryResult<T = unknown> = {
  data: Ref<T | undefined>;
  fetching: Ref<boolean>;
  error: Ref<unknown>;
  executeQuery: Mock;
};

/**
 * Stand-in for urql's `useQuery` that returns one result per query document, so a test can set
 * the data a store receives and check when the store re-executes a query.
 */
export const createUseQueryFake = () => {
  const results = new Map<unknown, FakeQueryResult>();

  const resultOf = <T>(query: unknown): FakeQueryResult<T> => {
    if (!results.has(query)) {
      results.set(query, {
        data: ref(),
        fetching: ref(false),
        error: ref(),
        executeQuery: vi.fn(),
      });
    }
    return results.get(query) as FakeQueryResult<T>;
  };

  return {
    useQuery: (({ query }: { query: unknown }) => resultOf(query)) as unknown as typeof useQuery,
    resultOf,
    reset: () => results.clear(),
  };
};
