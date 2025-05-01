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
  setAmplifierForRoomMutation,
  setAmplifierMutation,
  setTemperatureSetpointForRoomMutation,
  setTemperatureSetpointMutation,
  subscribeToRoom,
} from "@/graphql/queries/rooms";
import { createArea, toRoom } from "@/lib/mappers";
import { useMutation, UseMutationResponse, useSubscription } from "@urql/vue";
import { useDebounceFn, useLocalStorage, useTimeoutFn } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed, ref, toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "./auth";

const MUTATION_DELAY_IN_MS = 500;

type GetAllRoomsQuery = Pick<QueryRoot, "rooms">;

export const useRoomStore = defineStore("rooms", () => {
  const { t } = useI18n();
  const { isAdmin, cabin } = toRefs(useAuthStore());

  const emptyRoom: Room = {
    name: t("labels.emptyRoom"),
    group: RoomGroup.AFT,
    amplifierOn: false,
    temperatureSetpoint: 23,
    actualTemperature: 21,
    actualHumidity: 40,
    actualCO2: 500,
    blinds: [],
    lights: [],
    id: "empty",
  };

  const currentRoomId = useLocalStorage("currentRoomId", () => emptyRoom.id);
  const currentRoom = ref<Room>(emptyRoom);
  const areas = ref<ShipArea[]>([]);
  const hasPendingRequests = ref(false);

  const setRoom = (roomId: string) => {
    if (currentRoomId.value !== roomId && (isAdmin.value || roomId === cabin.value)) {
      hasPendingRequests.value = true;
      currentRoomId.value = roomId;
    }
  };

  // We debounce the mutation to prevent hammering the server with requests.
  // The UI will also be blocked during the pending mutation.
  const useDebounceMutation = <T extends object = object, Args extends unknown[] = unknown[]>(
    query: UseMutationResponse<unknown, T>,
    fn: (...args: Args) => T,
  ) =>
    useDebounceFn((...args: Args) => {
      hasPendingRequests.value = true;
      useTimeoutFn(() => (hasPendingRequests.value = false), 2000);
      return query.executeMutation(fn(...args));
    }, MUTATION_DELAY_IN_MS);

  // TODO: Find a better way to handle admin and user mutations
  const setTemperatureSetpoint = useDebounceMutation(
    useMutation<Rooms, MutationRootSetRoomTemperatureSetpointArgs>(
      isAdmin.value ? setTemperatureSetpointForRoomMutation : setTemperatureSetpointMutation,
    ),
    (temperature: number) => ({
      id: isAdmin.value ? currentRoomId.value : undefined,
      temperature,
    }),
  );

  const toggleAmplifier = useDebounceMutation(
    useMutation<Rooms, MutationRootSetAmplifierArgs>(
      isAdmin.value ? setAmplifierForRoomMutation : setAmplifierMutation,
    ),
    (amplifierOn: boolean) => ({
      id: isAdmin.value ? currentRoomId.value : undefined,
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
      pause: computed(() => currentRoomId.value === emptyRoom.id),
    },
    (_prev, result) => {
      if (result.rooms.length > 0) {
        currentRoom.value = toRoom(result.rooms[0]);
      }

      hasPendingRequests.value = false;

      return currentRoom.value;
    },
  );

  // We need this ready state mainly for testing purposes.
  const isReady = (async function init() {
    // if (!isAdmin.value) return;

    const { data } = await client.query<GetAllRoomsQuery>(getAll, {});
    const rooms = data?.rooms.map(toRoom) ?? [];

    areas.value = [
      createArea(RoomGroup.AFT, t("labels.roomGroup.aftship"), rooms),
      createArea(RoomGroup.MID, t("labels.roomGroup.midship"), rooms),
      createArea(RoomGroup.FORE, t("labels.roomGroup.foreship"), rooms),
      createArea(RoomGroup.UPPERDECK, t("labels.roomGroup.upperdeck"), rooms),
      createArea(RoomGroup.HALLWAYS, t("labels.roomGroup.hallways"), rooms),
    ];

    if (currentRoomId.value === emptyRoom.id && rooms.length > 0) {
      currentRoomId.value = rooms[0].id;
    }
  })();

  return {
    areas,
    currentRoom,
    currentRoomId,
    setRoom,
    hasPendingRequests,
    setTemperatureSetpoint,
    toggleAmplifier,
    setLightLevel,
    setBlindsLevel,
    isReady,
  };
});
