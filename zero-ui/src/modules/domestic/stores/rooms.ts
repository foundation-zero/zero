import { setBlindsLevelMutation } from "@/modules/domestic/graphql/queries/blinds";
import { setLightingGroupsLevelMutation } from "@/modules/domestic/graphql/queries/light-groups";
import {
  setAmplifierForRoomMutation,
  setAmplifierMutation,
  setCO2SetpointMutation,
  setHumiditySetpointMutation,
  setTemperatureSetpointForRoomMutation,
  setTemperatureSetpointMutation,
  subscribeToRooms,
} from "@/modules/domestic/graphql/queries/rooms";
import {
  DomesticBlinds,
  DomesticLightingGroups,
  MutationRootDomesticSetAmplifiersArgs,
  MutationRootDomesticSetBlindsArgs,
  MutationRootDomesticSetLightingGroupsArgs,
  MutationRootDomesticSetRoomCo2SetpointsArgs,
  MutationRootDomesticSetRoomHumiditySetpointsArgs,
  MutationRootDomesticSetRoomTemperatureSetpointsArgs,
} from "@/modules/domestic/graphql/types.generated";
import { createArea } from "@/modules/domestic/lib/mappers";
import { Room, RoomGroup, ShipArea } from "@/modules/domestic/types";
import { useMutation, UseMutationResponse, useSubscription } from "@urql/vue";
import { useDebounceFn, useLocalStorage, useTimeoutFn } from "@vueuse/core";

import { defineStore } from "pinia";
import { computed, MaybeRefOrGetter, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useAuthStore } from "./auth";

const MUTATION_DELAY_IN_MS = 5;

type GetAllRoomsQuery = { rooms: Room[] };

export const useRoomStore = defineStore("rooms", () => {
  const { t } = useI18n();
  const { isAdmin, cabin } = toRefs(useAuthStore());

  const emptyRoom: Room = {
    name: t("labels.emptyRoom"),
    group: RoomGroup.AFT,
    lightingGroups: [],
    blinds: [],
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
    useMutation<Room, MutationRootDomesticSetRoomTemperatureSetpointsArgs>(
      isAdmin.value ? setTemperatureSetpointForRoomMutation : setTemperatureSetpointMutation,
    ),
    (temperature: number) => ({
      ids: [currentRoomId.value],
      temperature,
    }),
  );

  const toggleAmplifier = useDebounceMutation(
    useMutation<Room, MutationRootDomesticSetAmplifiersArgs>(
      isAdmin.value ? setAmplifierForRoomMutation : setAmplifierMutation,
    ),
    (amplifierOn: boolean, roomId: string) => ({
      ids: isAdmin.value ? [roomId] : [currentRoomId.value],
      on: amplifierOn,
    }),
    0,
  );

  const setLightingGroupsLevel = useDebounceMutation(
    useMutation<DomesticLightingGroups, MutationRootDomesticSetLightingGroupsArgs>(
      setLightingGroupsLevelMutation,
    ),
    (lightIds: string[], level: number) => ({ ids: lightIds, level }),
    0,
  );

  const setBlindsLevel = useDebounceMutation(
    useMutation<DomesticBlinds, MutationRootDomesticSetBlindsArgs>(setBlindsLevelMutation),
    (blindId: string, level: number) => ({ ids: [blindId], level }),
  );

  const setHumiditySetpoints = useDebounceMutation(
    useMutation<Room, MutationRootDomesticSetRoomHumiditySetpointsArgs>(
      setHumiditySetpointMutation,
    ),
    (roomIds: string[], humidity: number) => ({
      ids: roomIds,
      humidity,
    }),
  );

  const setCO2Setpoints = useDebounceMutation(
    useMutation<Room, MutationRootDomesticSetRoomCo2SetpointsArgs>(setCO2SetpointMutation),
    (roomIds: string[], co2: number) => ({
      ids: roomIds,
      co2,
    }),
  );

  const { data: roomData, error: roomError } = useSubscription<GetAllRoomsQuery, Room[]>(
    {
      query: subscribeToRooms,
    },
    (_prev, result) => result.rooms ?? [],
  );
  watch(roomError, (val) => {
    console.error(val);
  });

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
    rooms,
    currentRoom,
    currentRoomId,
    setRoom,
    hasPendingRequests,
    setTemperatureSetpoint,
    toggleAmplifier,
    setLightingGroupsLevel,
    setBlindsLevel,
    setHumiditySetpoints,
    setCO2Setpoints,
  };
});
