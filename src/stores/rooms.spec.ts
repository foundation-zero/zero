import { Room } from "@/@types";
import { GetAllRoomsQuery, LightingGroups, Rooms } from "@/gql/graphql";
import client from "@/graphql/client";
import { setBlindsLevelMutation } from "@/graphql/queries/blinds";
import { setLightLevelMutation } from "@/graphql/queries/light-groups";
import {
  setAmplifierMutation,
  setTemperatureSetpointMutation,
  subscribeToRoom,
} from "@/graphql/queries/rooms";
import RoomStoreWrapper from "@/tests/helpers/RoomStoreWrapper.vue";
import * as urql from "@urql/vue";
import { mount } from "@vue/test-utils";
import { graphql, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { afterEach } from "node:test";
import { createPinia, setActivePinia } from "pinia";
import { afterAll, beforeAll, beforeEach, describe, expect, Mock, test, vi } from "vitest";
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import allRooms from "../../tests/data/all-rooms";
import { useRoomStore } from "./rooms";

vi.mock(import("vue-i18n"), async (importOriginal) => ({
  ...(await importOriginal()),
  useI18n: vi.fn(() => ({
    t: (key: string) => key,
  })) as unknown as typeof useI18n,
}));

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useSubscription: vi.fn(),
  useMutation: vi.fn(),
}));

const restHandlers = [
  graphql.query("GetAllRooms", () => {
    return HttpResponse.json({ data: allRooms });
  }),
];

const server = setupServer(...restHandlers);

beforeAll(() => server.listen({ onUnhandledRequest: "bypass" }));

// Close server after all tests
afterAll(() => server.close());

// Reset handlers after each test for test isolation
afterEach(() => server.resetHandlers());

describe("Rooms Store", () => {
  let store: ReturnType<typeof useRoomStore>;
  const useSubscription = urql.useSubscription as Mock<typeof urql.useSubscription>;
  const useMutation = urql.useMutation as Mock<typeof urql.useMutation>;
  const executeMutation = vi.fn();
  let subscriptionCallback: urql.SubscriptionHandler<GetAllRoomsQuery, Room>;

  beforeEach(async () => {
    setActivePinia(createPinia());
    useSubscription.mockImplementationOnce((_, cb) => {
      subscriptionCallback = cb as urql.SubscriptionHandler<GetAllRoomsQuery, Room>;
      return {} as urql.UseSubscriptionResponse;
    });

    useMutation.mockImplementation(<T>() => ({
      executeMutation,
      fetching: ref(false),
      stale: ref(false),
      error: ref(),
      data: ref<T | undefined>(),
      extensions: ref(),
      hasNext: ref(false),
      operation: ref(),
    }));

    vi.spyOn(client, "executeMutation");

    const wrapper = mount(RoomStoreWrapper, { global: { provide: { $urql: ref(client) } } });
    store = wrapper.vm.store;
    await store.isReady;
  });

  describe("setup", () => {
    test("it fetches list of rooms", () => {
      expect(store.areas.flatMap((area) => area.rooms)).toHaveLength(allRooms.rooms.length);
    });

    test('it subscribes to "subscribeToRoom" query', () => {
      expect(useSubscription).toHaveBeenCalled();
      expect(useSubscription.mock.calls[0][0].query).toEqual(subscribeToRoom);
      expect(useSubscription.mock.calls[0][0].variables).toEqual({ roomId: expect.any(Object) });
      expect(useSubscription.mock.calls[0][0].pause).toEqual(expect.any(Object));
    });
  });

  describe("streaming data", () => {
    test("it updates the current room data", async () => {
      const nextRoom: Room = store.areas[0].rooms[0];

      subscriptionCallback(nextRoom, {
        rooms: [
          {
            ...allRooms.rooms.find((room) => room.id === nextRoom.id),
            temperatureSetpoint: 99,
            amplifierOn: false,
            actualHumidity: 0.5,
            actualTemperature: 99,
            lightingGroups: [],
          } as Rooms,
        ],
      });

      expect(store.currentRoom.id).toBe(nextRoom.id);
      expect(store.currentRoom.temperatureSetpoint).toBe(99);
      expect(store.currentRoom.amplifierOn).toBe(false);
    });

    test("it updates the blinds data", async () => {
      const nextRoom: Room = store.areas[0].rooms[0];
      const nextBlinds = [{ id: "1", level: 99 }];

      subscriptionCallback(nextRoom, {
        rooms: [
          {
            ...allRooms.rooms.find((room) => room.id === nextRoom.id),
            blinds: nextBlinds,
            actualHumidity: 0.5,
            actualTemperature: 99,
            amplifierOn: false,
            temperatureSetpoint: 99,
          } as Rooms,
        ],
      });

      expect(store.currentRoom.blinds[0].controls).toMatchObject(nextBlinds);
    });

    test("it updates the lights data", async () => {
      const nextRoom: Room = store.areas[0].rooms[0];
      const nextLightingGroups: LightingGroups[] = [{ id: "1", level: 80, name: "Floor Lamp" }];

      subscriptionCallback(nextRoom, {
        rooms: [
          {
            ...allRooms.rooms.find((room) => room.id === nextRoom.id),
            lightingGroups: nextLightingGroups,
            actualHumidity: 0.5,
            actualTemperature: 99,
            blinds: [],
            amplifierOn: false,
            temperatureSetpoint: 99,
          } as Rooms,
        ],
      });

      expect(store.currentRoom.lights[0].controls).toMatchObject(nextLightingGroups);
    });
  });

  describe("control", () => {
    test("it sends a mutation to change the temperature setpoint", async () => {
      const nextTemperature = 99;

      await store.setTemperatureSetpoint(nextTemperature);

      expect(useMutation).toHaveBeenCalledWith(setTemperatureSetpointMutation);
      expect(executeMutation).toHaveBeenCalledWith({
        id: "owners-cabin",
        temperature: nextTemperature,
      });
    });

    test("it sends a mutation to change the amplifier state", async () => {
      const nextState = true;

      await store.toggleAmplifier(nextState);

      expect(useMutation).toHaveBeenCalledWith(setAmplifierMutation);
      expect(executeMutation).toHaveBeenCalledWith({
        id: "owners-cabin",
        on: nextState,
      });
    });

    test("it sends a mutation to change the blinds level", async () => {
      const nextLevel = 0.75;

      await store.setBlindsLevel("1", nextLevel);

      expect(useMutation).toHaveBeenCalledWith(setBlindsLevelMutation);
      expect(executeMutation).toHaveBeenCalledWith({
        id: "1",
        level: nextLevel,
      });
    });

    test("it sends a mutation to change the light level", async () => {
      const nextLevel = 0.75;

      await store.setLightLevel("1", nextLevel);

      expect(useMutation).toHaveBeenCalledWith(setLightLevelMutation);
      expect(executeMutation).toHaveBeenCalledWith({
        id: "1",
        level: nextLevel,
      });
    });
  });
});
