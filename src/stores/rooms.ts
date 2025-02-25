import { Room, RoomGroup, ShipArea } from "@/@types";
import {
  Blinds,
  LightingGroups,
  MutationRootSetAmplifierArgs,
  MutationRootSetBlindArgs,
  MutationRootSetLightingGroupArgs,
  MutationRootSetRoomTemperatureSetpointArgs,
  QueryRoot,
  Rooms,
} from "@/gql/graphql";
import client from "@/graphql/client";
import { setBlindsLevelMutation } from "@/graphql/queries/blinds";
import { setLightLevelMutation } from "@/graphql/queries/light-groups";
import {
  getAll,
  setAmplifierMutation,
  setTemperatureSetpointMutation,
  subscribeToRoom,
} from "@/graphql/queries/rooms";
import { createArea, toRoom } from "@/lib/mappers";
import { useMutation, UseMutationResponse, useSubscription } from "@urql/vue";
import { useDebounceFn, useLocalStorage, useTimeoutFn } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

const MUTATION_DELAY_IN_MS = 500;

type GetAllRoomsQuery = Pick<QueryRoot, "rooms">;

const EMPTY_ROOM: Room = {
  name: "empty",
  group: RoomGroup.AFT,
  amplifierOn: false,
  temperatureSetpoint: 23,
  actualTemperature: 21,
  actualHumidity: 40,
  blinds: [],
  lights: [],
  id: "empty",
};

export const useRoomStore = defineStore("rooms", () => {
  const currentRoomId = useLocalStorage("currentRoomId", () => EMPTY_ROOM.id);
  const currentRoom = ref<Room>(EMPTY_ROOM);
  const areas = ref<ShipArea[]>([]);
  const hasPendingMutations = ref(false);

  const setRoom = (room: Room) => {
    currentRoomId.value = room.id;
  };

  // We debounce the mutation to prevent hammering the server with requests.
  // The UI will also be blocked during the pending mutation.
  const useDebounceMutation = <T extends object = object, Args extends unknown[] = unknown[]>(
    query: UseMutationResponse<unknown, T>,
    fn: (...args: Args) => T,
  ) =>
    useDebounceFn((...args: Args) => {
      hasPendingMutations.value = true;
      useTimeoutFn(() => (hasPendingMutations.value = false), 2000);
      return query.executeMutation(fn(...args));
    }, MUTATION_DELAY_IN_MS);

  const setTemperatureSetpoint = useDebounceMutation(
    useMutation<Rooms, MutationRootSetRoomTemperatureSetpointArgs>(setTemperatureSetpointMutation),
    (temperature: number) => ({
      id: currentRoomId.value,
      temperature,
    }),
  );

  const toggleAmplifier = useDebounceMutation(
    useMutation<Rooms, MutationRootSetAmplifierArgs>(setAmplifierMutation),
    (amplifierOn: boolean) => ({
      id: currentRoomId.value,
      on: amplifierOn,
    }),
  );

  const setLightLevel = useDebounceMutation(
    useMutation<LightingGroups, MutationRootSetLightingGroupArgs>(setLightLevelMutation),
    (lightId: string, level: number) => ({ id: lightId, level }),
  );

  const setBlindsLevel = useDebounceMutation(
    useMutation<Blinds, MutationRootSetBlindArgs>(setBlindsLevelMutation),
    (blindId: string, level: number) => ({ id: blindId, level }),
  );

  useSubscription<GetAllRoomsQuery, Room>(
    {
      query: subscribeToRoom,
      variables: { roomId: currentRoomId },
      pause: computed(() => currentRoomId.value === EMPTY_ROOM.id),
    },
    (_prev, result) => {
      if (result.rooms.length > 0) {
        currentRoom.value = toRoom(result.rooms[0]);
      }

      hasPendingMutations.value = false;

      return currentRoom.value;
    },
  );

  // We need this ready state mainly for testing purposes.
  const isReady = (async function init() {
    const { data } = await client.query<GetAllRoomsQuery>(getAll, {});
    const rooms = data?.rooms.map(toRoom) ?? [];

    areas.value = [
      createArea(RoomGroup.AFT, "Aftship", rooms),
      createArea(RoomGroup.MID, "Midship", rooms),
      createArea(RoomGroup.FORE, "Foreship", rooms),
      createArea(RoomGroup.UPPERDECK, "Upperdeck", rooms),
      createArea(RoomGroup.HALLWAYS, "Hallways", rooms),
    ];

    if (currentRoomId.value === EMPTY_ROOM.id && rooms.length > 0) {
      currentRoomId.value = rooms[0].id;
    }
  })();

  return {
    areas,
    currentRoom,
    setRoom,
    hasPendingMutations,
    setTemperatureSetpoint,
    toggleAmplifier,
    setLightLevel,
    setBlindsLevel,
    isReady,
  };
});
