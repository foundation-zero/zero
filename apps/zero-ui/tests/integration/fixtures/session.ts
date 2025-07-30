import { PlaywrightTestArgs, TestFixture } from "@playwright/test";
import { Rooms } from "../../../src/gql/graphql";

export interface SessionFixture {
  setRoom(room: Rooms): Promise<void>;
}

export const createSessionFixture = (): [
  TestFixture<SessionFixture, PlaywrightTestArgs>,
  {
    scope: "test";
    auto: boolean;
  },
] => [
  async ({ page }, use) => {
    const setRoom = async (room: Rooms) => {
      await page.evaluate((room) => window.localStorage.setItem("currentRoomId", room.id), room);
    };

    use({ setRoom });
  },
  {
    scope: "test",
    auto: true,
  },
];
