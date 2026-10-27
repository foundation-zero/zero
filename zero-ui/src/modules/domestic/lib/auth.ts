import { useAuthStore } from "@/modules/common/stores/auth";
import client from "../graphql/client";
import { getVersion } from "../graphql/queries/app";

/** Checks that the current token has roles and is accepted by the domestic API. */
export const verifyToken = async () => {
  if (!useAuthStore().isLoggedIn) throw new Error("No roles defined in token");

  const response = await client.query(getVersion, {});

  if (response.error) {
    throw new Error("Token verification failed");
  }
};
