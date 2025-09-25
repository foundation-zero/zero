import { Locator, Page } from "@playwright/test";

export type LightControl = [slider: Locator, track: Locator, toggle: Locator, value: string | null];

export default class THRSPage {
  public constructor(private readonly page: Page) {}

  public get navigation(): Locator {
    return this.page.getByTestId("thrs-nav");
  }

  public get actions(): Locator {
    return this.page.getByTestId("thrs-actions");
  }

  public get breadcrumbs(): Locator {
    return this.page.getByTestId("breadcrumbs");
  }
}
