import allRooms from "../../data/all-rooms";
import { toAmplifierStatus } from "../../lib/helpers";
import { expect, test as testBase } from "../../mocks/playwright";
import { getAllRooms, getVersion } from "../../mocks/queries";
import RoomsPage from "./page";

const test = testBase.extend<{ roomsPage: RoomsPage }>({
  roomsPage: [
    async ({ page, worker, subscriptions }, use) => {
      worker.use(getAllRooms, getVersion);

      const roomsPage = new RoomsPage(page, subscriptions);

      await use(roomsPage);
    },
    { auto: true },
  ],
});

const dutchCabin = allRooms.rooms.find((room) => room.id === "dutch-cabin")!;

test.describe("Rooms", () => {
  test.describe("as a user", () => {
    test.beforeEach(async ({ auth, roomsPage }) => {
      await auth.asUser();

      roomsPage.updateRoom(dutchCabin);
    });

    test("subscribes to a room", async ({ roomsPage }) => {
      expect(roomsPage.subscribers).toHaveLength(1);
      expect(roomsPage.subscribers[0].payload!.variables).toEqual({});
    });

    test("shows the current room", async ({ roomsPage }) => {
      await expect(roomsPage.title).toHaveText(dutchCabin.name);
    });

    test("shows the correct state of the audio system", async ({ roomsPage }) => {
      roomsPage.updateRoom(dutchCabin, { roomsControls: [toAmplifierStatus(false)] });

      await expect(roomsPage.audioSystemToggle).toHaveAttribute("data-state", "unchecked");

      roomsPage.updateRoom(dutchCabin, { roomsControls: [toAmplifierStatus(true)] });

      await expect(roomsPage.audioSystemToggle).toHaveAttribute("data-state", "checked");
    });
  });

  test.describe("as admin", () => {
    test.beforeEach(async ({ auth, subscriptions }) => {
      await auth.asAdmin();
      subscriptions.dispatch("SubscribeToRoom", allRooms);
    });

    test("subscribes to a room", async ({ roomsPage }) => {
      expect(roomsPage.subscribers).toHaveLength(1);
      expect(roomsPage.subscribers[0].payload!.variables).toEqual({});
    });

    test.describe("room selection", () => {
      test("it shows the side navigation", async ({ page, roomsPage }) => {
        await expect(roomsPage.dialog).toHaveClass("show");
        await page.screenshot({ path: "screenshots/rooms_admin.png" });
      });

      test("it shows the correct amount of rooms", async ({ roomsPage }) => {
        await expect(roomsPage.roomList).toHaveCount(allRooms.rooms.length);
      });
    });
  });
});
