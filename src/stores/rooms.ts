import { Room, RoomGroup, ShipArea } from "@/@types";
import {
  Blinds,
  LightingGroups,
  MutationRootSetAmplifierArgs,
  MutationRootSetBlindArgs,
  MutationRootSetLightingGroupArgs,
  MutationRootSetLightingGroupsArgs,
  MutationRootSetRoomTemperatureSetpointArgs,
  QueryRoot,
  Rooms,
} from "@/gql/graphql";
import { setBlindsLevelMutation } from "@/graphql/queries/blinds";
import {
  setLightingGroupsLevelMutation,
  setLightLevelMutation,
} from "@/graphql/queries/light-groups";
import {
  setAmplifierForRoomMutation,
  setAmplifierMutation,
  setTemperatureSetpointForRoomMutation,
  setTemperatureSetpointMutation,
  subscribeToRooms,
} from "@/graphql/queries/rooms";
import { createArea, toRoom } from "@/lib/mappers";
import { useMutation, UseMutationResponse, useSubscription } from "@urql/vue";
import { useDebounceFn, useLocalStorage, useTimeoutFn } from "@vueuse/core";

import { defineStore } from "pinia";
import { computed, MaybeRefOrGetter, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "./auth";

const MUTATION_DELAY_IN_MS = 5;

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

  const currentRoomId = useLocalStorage("currentRoomId", () => cabin.value ?? emptyRoom.id);
  const hasPendingRequests = ref(false);

  const setRoom = (roomId: string) => {
    currentRoomId.value = roomId;
  };

  // We debounce the mutation to prevent hammering the server with requests.
  // The UI will also be blocked during the pending mutation.
  const useDebounceMutation = <T extends object = object, Args extends unknown[] = unknown[]>(
    query: UseMutationResponse<unknown, T>,
    fn: (...args: Args) => T,
    delay: MaybeRefOrGetter<number> = MUTATION_DELAY_IN_MS,
  ) =>
    useDebounceFn((...args: Args) => {
      hasPendingRequests.value = true;
      const timeout = useTimeoutFn(() => (hasPendingRequests.value = false), 2000);
      watch(hasPendingRequests, () => timeout.stop(), { once: true });
      return query.executeMutation(fn(...args));
    }, delay);

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
    0,
  );

  const setLightLevel = useDebounceMutation(
    useMutation<LightingGroups, MutationRootSetLightingGroupArgs>(setLightLevelMutation),
    (lightId: string, level: number) => ({ id: lightId, level }),
  );

  const setLightingGroupsLevel = useDebounceMutation(
    useMutation<LightingGroups, MutationRootSetLightingGroupsArgs>(setLightingGroupsLevelMutation),
    (lightIds: string[], level: number) => ({ ids: lightIds, level }),
    0,
  );

  const setBlindsLevel = useDebounceMutation(
    useMutation<Blinds, MutationRootSetBlindArgs>(setBlindsLevelMutation),
    (blindId: string, level: number) => ({ id: blindId, level }),
  );

  const { data: roomData } = useSubscription<GetAllRoomsQuery, Room[]>(
    {
      query: subscribeToRooms,
    },
    (_prev, result) => result.rooms.map(toRoom) ?? [],
  );

  const rooms = computed(() => roomData.value ?? []);
  const currentRoom = computed<Room>(
    () => rooms.value.find((room) => room.id === currentRoomId.value) ?? emptyRoom,
  );

  const areas = computed<ShipArea[]>(() => [
    createArea(RoomGroup.AFT, t("labels.roomGroup.aftship"), rooms.value),
    createArea(RoomGroup.MID, t("labels.roomGroup.midship"), rooms.value),
    createArea(RoomGroup.FORE, t("labels.roomGroup.foreship"), rooms.value),
    createArea(RoomGroup.UPPERDECK, t("labels.roomGroup.upperdeck"), rooms.value),
    createArea(RoomGroup.HALLWAYS, t("labels.roomGroup.hallways"), rooms.value),
  ]);

  watch(rooms, (rooms) => {
    if (currentRoomId.value === emptyRoom.id && rooms.length > 0) {
      currentRoomId.value = rooms[0].id;
    }

    hasPendingRequests.value = false;
  });

  return {
    areas,
    currentRoom,
    currentRoomId,
    setRoom,
    hasPendingRequests,
    setTemperatureSetpoint,
    toggleAmplifier,
    setLightLevel,
    setLightingGroupsLevel,
    setBlindsLevel,
  };
});
