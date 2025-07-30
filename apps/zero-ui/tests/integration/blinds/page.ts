import { Locator, Page } from "@playwright/test";
import { SubscriptionInterceptor } from "graphql-subscriptions-mock";
import { BlindsControl, Room } from "../../../src/@types";
import allRooms from "../../data/all-rooms";
import { isBlindsControl } from "../../lib/helpers";
import { ZeroSubscriptions } from "../../mocks/playwright";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class BlindsPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionInterceptor<ZeroSubscriptions>,
  ) {}

  public open(): Promise<void> {
    return this.page.getByRole("tab").getByText("Blinds").click();
  }

  private get subscribeToRoom() {
    return this.subscriptions.subscribe("SubscribeToRoom");
  }

  public setBlindLevels(
    blindLevels: number[],
    room: Room = allRooms.rooms.find(
      (room) => room.roomsControls.filter(isBlindsControl).length === blindLevels.length,
    )!,
  ): void {
    const blinds = room.roomsControls.filter(isBlindsControl);

    this.subscribeToRoom.dispatch({
      rooms: [
        {
          ...room,
          roomsControls: blinds.map<BlindsControl>((blind, index) => ({
            ...blind,
            time: Date.now(),
            value: blindLevels[index] !== undefined ? blindLevels[index] : blind.value,
          })),
        },
      ],
    });
  }

  public get listItems(): Locator {
    return this.page.getByTestId("blinds-control");
  }

  public async textValues() {
    return await this.page.getByTestId("blindsPosition").allTextContents();
  }
}
