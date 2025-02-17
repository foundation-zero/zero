import { graphql, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { createPinia, setActivePinia } from "pinia";
import { afterAll, afterEach, beforeAll, beforeEach, describe, expect, test } from "vitest";
import allRooms from "./all-rooms.test.json";
import { useRoomStore } from "./rooms";

const restHandlers = [
  graphql.query("GetAllRooms", () => {
    return HttpResponse.json({ data: allRooms });
  }),
];

const server = setupServer(...restHandlers);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));

// Close server after all tests
afterAll(() => server.close());

// Reset handlers after each test for test isolation
afterEach(() => server.resetHandlers());

describe(useRoomStore, () => {
  let store: ReturnType<typeof useRoomStore>;

  beforeEach(async () => {
    setActivePinia(createPinia());
    store = useRoomStore();
    await store.init();
  });

  test("it fetches list of rooms", () => {
    expect(store.rooms).toHaveLength(22);
  });
});
