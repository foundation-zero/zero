import { useAuthStore } from "@/modules/common/stores/auth";
import { Roles } from "@/modules/common/types";
import { createTestingPinia } from "@pinia/testing";
import { tokens } from "@tests/lib/auth";
import { setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";
import client from "../graphql/client";
import { verifyToken } from "./auth";

vi.mock("../graphql/client", () => ({
  default: { query: vi.fn() },
}));

describe("verifyToken", () => {
  beforeEach(() => {
    localStorage.clear();
    setActivePinia(createTestingPinia({ stubActions: false }));
    vi.mocked(client.query).mockReset();
  });

  it("accepts a token the API accepts", async () => {
    vi.mocked(client.query).mockResolvedValue({} as never);
    useAuthStore().setToken(tokens[Roles.User]);

    await expect(verifyToken()).resolves.toBeUndefined();
  });

  it("rejects a token the API refuses", async () => {
    vi.mocked(client.query).mockResolvedValue({ error: new Error("Unauthorized") } as never);
    useAuthStore().setToken(tokens[Roles.User]);

    await expect(verifyToken()).rejects.toThrow("Token verification failed");
  });

  it("rejects without calling the API when the token has no roles", async () => {
    await expect(verifyToken()).rejects.toThrow("No roles defined in token");
    expect(client.query).not.toHaveBeenCalled();
  });
});
