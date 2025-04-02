import { Locator, Page } from "@playwright/test";
import { Rooms } from "../../../src/gql/graphql";
import allRooms from "../../data/all-rooms";
import { SubscriptionFixture } from "../../mocks/graphql";
import { ZeroSubscriptions } from "../../mocks/playwright";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class LightsPage {
  public constructor(
    private readonly page: Page,
    private readonly subscriptions: SubscriptionFixture<ZeroSubscriptions>,
  ) {}

  public setLightLevels(
    lightLevels: number[],
    room: Rooms = allRooms.rooms.find((room) => room.lightingGroups.length === lightLevels.length)!,
  ): void {
    this.subscriptions.dispatch("SubscribeToRoom", {
      rooms: [
        {
          ...room,
          lightingGroups: room.lightingGroups.map((light, index) => ({
            ...light,
            level: lightLevels[index] !== undefined ? lightLevels[index] : light.level,
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
