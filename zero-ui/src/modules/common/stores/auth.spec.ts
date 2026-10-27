import { Roles } from "@/modules/common/types";
import { createTestingPinia } from "@pinia/testing";
import { tokens } from "@tests/lib/auth";
import { setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";
import { useAuthStore } from "./auth";

describe("auth store", () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  it("is logged out without a token", () => {
    const auth = useAuthStore();

    expect(auth.isLoggedIn).toBe(false);
    expect(auth.roles).toEqual([]);
    expect(auth.isAdmin).toBe(false);
  });

  it("reads the roles from an admin token", () => {
    const auth = useAuthStore();

    auth.setToken(tokens[Roles.Admin]);

    expect(auth.isLoggedIn).toBe(true);
    expect(auth.isAdmin).toBe(true);
    expect(auth.isUser).toBe(true);
    expect(auth.cabin).toBeNull();
  });

  it("reads the cabin from a user token", () => {
    const auth = useAuthStore();

    auth.setToken(tokens[Roles.User]);

    expect(auth.isAdmin).toBe(false);
    expect(auth.isUser).toBe(true);
    expect(auth.cabin).toBe("dutch-cabin");
  });

  it("restores the token from local storage and forgets it when cleared", async () => {
    localStorage.setItem("token", tokens[Roles.User]);
    const auth = useAuthStore();

    expect(auth.isLoggedIn).toBe(true);

    auth.clearToken();
    await nextTick();

    expect(auth.isLoggedIn).toBe(false);
    expect(localStorage.getItem("token")).toBeNull();
  });
});
