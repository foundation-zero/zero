import { Roles, Room } from "@/@types";
import client from "@/graphql/client";
import { setBlindsLevelMutation } from "@/graphql/queries/blinds";
import { setLightingGroupsLevelMutation } from "@/graphql/queries/light-groups";
import {
  setAmplifierForRoomMutation,
  setAmplifierMutation,
  setTemperatureSetpointForRoomMutation,
  setTemperatureSetpointMutation,
  subscribeToRooms,
} from "@/graphql/queries/rooms";

import {
  extractActualCO2,
  extractActualHumidity,
  extractActualTemperature,
  extractAmplifierStatus,
  extractTemperatureSetpoint,
} from "@/lib/utils";
import { createTestingPinia, TestingPinia } from "@pinia/testing";
import * as urql from "@urql/vue";
import { graphql, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { afterEach } from "node:test";
import { setActivePinia } from "pinia";
import { afterAll, beforeAll, beforeEach, describe, expect, Mock, test, vi } from "vitest";
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import allRooms from "../../tests/data/all-rooms";
import { tokens } from "../../tests/lib/auth";
import {
  toAmplifierStatus,
  toBlindsControl,
  toCO2Sensor,
  toHumiditySensor,
  toLightingControl,
  toTemperatureControl,
  toTemperatureSensor,
} from "../../tests/lib/helpers";
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

  let pinia: TestingPinia;
  const useSubscription = urql.useSubscription as Mock<typeof urql.useSubscription>;
  const useMutation = urql.useMutation as Mock<typeof urql.useMutation>;
  const executeMutation = vi.fn();
  let subscriptionCallback: urql.SubscriptionHandler<{ rooms: Room[] }, Room[]>;
  const data = ref<Room[]>();

  const setupStore = (role: Roles, roomData?: Room[], currentRoomId?: string) => {
    data.value = roomData;
    localStorage.setItem("token", tokens[role]);
    localStorage.setItem("currentRoomId", currentRoomId ?? "");
    pinia = createTestingPinia({ stubActions: false });
    setActivePinia(pinia);
    useSubscription.mockImplementation((_, cb) => {
      subscriptionCallback = cb as urql.SubscriptionHandler<{ rooms: Room[] }, Room[]>;
      return { data } as urql.UseSubscriptionResponse;
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

    store = useRoomStore(pinia);
    vi.spyOn(client, "executeMutation");
  };

  describe("setup", () => {
    beforeEach(() => {
      setupStore(Roles.Admin, allRooms.rooms);
    });
    test("it fetches list of rooms", () => {
      expect(store.areas.flatMap((area) => area.rooms)).toHaveLength(allRooms.rooms.length);
    });

    test('it subscribes to "subscribeToRoom" query', () => {
      expect(useSubscription).toHaveBeenCalled();
      expect(useSubscription.mock.calls[0][0].query).toEqual(subscribeToRooms);
      expect(useSubscription.mock.calls[0][0].variables).toEqual(undefined);
    });
  });

  describe("streaming data", () => {
    const room = allRooms.rooms[0];

    beforeEach(() => {
      setupStore(Roles.Admin, allRooms.rooms, room.id);
    });

    test("it updates the control data", async () => {
      const controls: Room["roomsControls"] = [
        toAmplifierStatus(false),
        toTemperatureControl(99),
        toBlindsControl(0.5),
        toLightingControl(50),
      ];

      data.value = subscriptionCallback([], {
        rooms: [
          {
            ...room,
            roomsControls: controls,
            roomsSensors: [],
          },
        ],
      });

      expect(store.currentRoom.roomsControls).toMatchObject(controls);
      expect(extractTemperatureSetpoint(store.currentRoom)).toBe(99);
      expect(extractAmplifierStatus(store.currentRoom)).toBe(0);
    });

    test("it updates the sensor data", async () => {
      const sensors: Room["roomsSensors"] = [
        toTemperatureSensor(25),
        toHumiditySensor(50),
        toCO2Sensor(400),
      ];

      data.value = subscriptionCallback([], {
        rooms: [
          {
            ...room,
            roomsControls: [],
            roomsSensors: sensors,
          },
        ],
      });

      expect(store.currentRoom.roomsSensors).toMatchObject(sensors);
      expect(extractActualHumidity(store.currentRoom)).toBe(50);
      expect(extractActualTemperature(store.currentRoom)).toBe(25);
      expect(extractActualCO2(store.currentRoom)).toBe(400);
    });
  });

  describe("control", () => {
    const room = allRooms.rooms[0];

    describe("as an admin", () => {
      beforeEach(() => {
        setupStore(Roles.Admin, allRooms.rooms, room.id);
      });
      test("it sends a mutation to change the temperature setpoint", async () => {
        const nextTemperature = 99;

        await store.setTemperatureSetpoint(nextTemperature);

        expect(useMutation).toHaveBeenCalledWith(setTemperatureSetpointForRoomMutation);
        expect(executeMutation).toHaveBeenCalledWith({
          ids: room.id,
          temperature: nextTemperature,
        });
      });

      test("it sends a mutation to change the amplifier state", async () => {
        const nextState = true;

        await store.toggleAmplifier(nextState, room.id);

        expect(useMutation).toHaveBeenCalledWith(setAmplifierForRoomMutation);
        expect(executeMutation).toHaveBeenCalledWith({
          ids: [room.id],
          on: nextState,
        });
      });
    });

    describe("as a user", () => {
      beforeEach(async () => {
        setupStore(Roles.User);
      });

      test("it sends a mutation to change the temperature setpoint", async () => {
        const nextTemperature = 99;

        await store.setTemperatureSetpoint(nextTemperature);

        expect(useMutation).toHaveBeenCalledWith(setTemperatureSetpointMutation);
        expect(executeMutation).toHaveBeenCalledWith({
          id: undefined,
          temperature: nextTemperature,
        });
      });

      test("it sends a mutation to change the amplifier state", async () => {
        const nextState = true;

        await store.toggleAmplifier(nextState, room.id);

        expect(useMutation).toHaveBeenCalledWith(setAmplifierMutation);
        expect(executeMutation).toHaveBeenCalledWith({
          id: undefined,
          on: nextState,
        });
      });

      test("it sends a mutation to change the blinds level", async () => {
        const nextLevel = 0.75;

        await store.setBlindsLevel("1", nextLevel);

        expect(useMutation).toHaveBeenCalledWith(setBlindsLevelMutation);
        expect(executeMutation).toHaveBeenCalledWith({
          ids: "1",
          level: nextLevel,
        });
      });

      test("it sends a mutation to change the light level", async () => {
        const nextLevel = 0.75;

        await store.setLightLevel("1", nextLevel);

        expect(useMutation).toHaveBeenCalledWith(setLightingGroupsLevelMutation);
        expect(executeMutation).toHaveBeenCalledWith({
          ids: "1",
          level: nextLevel,
        });
      });
    });
  });
});
