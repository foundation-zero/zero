import allRooms from "../../data/all-rooms";
import { expect, test as testBase } from "../../mocks/playwright";
import { getAllRooms } from "../../mocks/queries";
import RoomsPage from "./page";

const test = testBase.extend<{ roomsPage: RoomsPage }>({
  roomsPage: [
    async ({ page, worker, subscriptions, auth }, use) => {
      worker.use(getAllRooms);

      await page.goto("/");
      await auth.asUser();
      await use(new RoomsPage(page, subscriptions));
    },
    { auto: true },
  ],
});

test.describe("Rooms", () => {
  const room = allRooms.rooms[0];

  test("subscribes to a room", async ({ roomsPage }) => {
    expect(roomsPage.subscribers).toHaveLength(1);
    expect(roomsPage.subscribers[0].payload!.variables?.roomId).toBe(allRooms.rooms[0].id);
  });

  test("gets all rooms", async () => {
    expect(getAllRooms.isUsed).toBe(true);
  });

  test("shows the current room", async ({ roomsPage }) => {
    roomsPage.updateRoom(room);

    await expect(roomsPage.trigger).toHaveText(room.name);
  });

  test("shows the correct state of the audio system", async ({ roomsPage }) => {
    roomsPage.updateRoom(room, { amplifierOn: false });

    await expect(roomsPage.audioSystemToggle).toHaveAttribute("data-state", "unchecked");

    roomsPage.updateRoom(room, { amplifierOn: true });

    await expect(roomsPage.audioSystemToggle).toHaveAttribute("data-state", "checked");
  });

  test.describe("as admin", () => {
    test.beforeEach(async ({ auth, subscriptions, page }) => {
      await auth.asAdmin();
      subscriptions.reset();
      await page.reload();
      await page.waitForTimeout(1000);
    });

    test.describe("room selection", () => {
      test("it opens the room selection dialog", async ({ roomsPage }) => {
        await expect(roomsPage.dialog).not.toBeVisible();

        await roomsPage.trigger.click();

        await expect(roomsPage.dialog).toBeVisible();
      });

      test("it shows the correct amount of rooms", async ({ roomsPage }) => {
        await roomsPage.trigger.click();

        await expect(roomsPage.roomList).toHaveCount(allRooms.rooms.length);
      });

      test("updates the subscription", async ({ page, roomsPage }) => {
        await roomsPage.trigger.click();

        await roomsPage.roomItem(allRooms.rooms[1].id).click();
        await page.waitForTimeout(100);

        expect(roomsPage.subscribers).toHaveLength(2);
        expect(roomsPage.subscribers[1].payload!.variables?.roomId).toBe(allRooms.rooms[1].id);
      });
    });
  });
});
