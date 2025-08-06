import { Locator, Page } from "@playwright/test";

import { SubscriptionInterceptor } from "@foundation-zero/graphql-subscriptions-mock";
import { Room } from "../../../src/@types";
import allRooms from "../../data/all-rooms";
import { isLightControl } from "../../lib/helpers";
import { ZeroSubscriptions } from "../../mocks/playwright";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class LightsPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionInterceptor<ZeroSubscriptions>,
  ) {}

  public open(): Promise<void> {
    return this.page.getByRole("tab").getByText("Lights").click();
  }

  private get subscribeToRoom() {
    return this.subscriptions.subscribe("SubscribeToRoom");
  }

  public setLightLevels(
    lightLevels: number[],
    room: Room = allRooms.rooms.find(
      (room) => room.roomsControls.filter(isLightControl).length === lightLevels.length,
    )!,
  ): void {
    const lights = room.roomsControls.filter(isLightControl);

    this.subscribeToRoom.dispatch({
      rooms: [
        {
          ...room,
          roomsControls: lights.map((light, index) => ({
            ...light,
            value: lightLevels[index] !== undefined ? lightLevels[index] : light.value,
            time: Date.now(),
          })),
        },
      ],
    });
  }

  public get sliders(): Locator {
    return this.page.getByRole("slider");
  }

  public get tracks(): Locator {
    return this.page.getByTestId("slider-track");
  }

  public get switches(): Locator {
    return this.page.getByRole("switch");
  }

  public async getValue(index: number): Promise<string | null> {
    return this.sliders.nth(index).getAttribute("aria-valuenow");
  }

  public async getControl(index: number): Promise<LightControl> {
    const slider = this.sliders.nth(index);
    const track = this.tracks.nth(index);
    const switchControl = this.switches.nth(index);
    const sliderValue = await slider.getAttribute("aria-valuenow");

    return [slider, track, switchControl, sliderValue];
  }
}
