import { PlaywrightTestArgs, TestFixture, WebSocketRoute } from "@playwright/test";
import { SubscribeMessage, WebsocketMessage } from "../types";

export interface SubscriptionFixtureOptions {
  url: string;
  autoAck?: boolean;
}

export type Subscriptions = Record<string, unknown>;

export type SubscriptionDispatcher<Subs extends Subscriptions> = {
  <K extends keyof Subs>(key: K, data: Subs[K]): void;
  <K extends keyof Subs>(key: K): SubscriptionDispatch<Subs[K]>;
};

export type SubscriptionDispatch<T> = (data: T) => void;

// TODO: Make this fixture framework agnostic and implement Playwright adapter.
export interface SubscriptionFixture<Subs extends Subscriptions> {
  dispatch: SubscriptionDispatcher<Subs>;
  subscribers: <K extends keyof Subs>(key: K) => SubscribeMessage[];
  incoming: WebsocketMessage[];
  outgoing: WebsocketMessage[];
}

export const createSubscriptionFixture = <Subs extends Subscriptions>(
  options: SubscriptionFixtureOptions,
): [
  TestFixture<SubscriptionFixture<Subs>, PlaywrightTestArgs>,
  {
    scope: "test";
    auto: boolean;
  },
] => [
  async ({ page }, use) => {
    let socket: WebSocketRoute;
    const incoming: WebsocketMessage[] = [];
    const outgoing: WebsocketMessage[] = [];
    const sockets: WebSocketRoute[] = [];

    const dispatch = (message: WebsocketMessage) => {
      outgoing.push(message);
      socket!.send(JSON.stringify(message));
    };

    await page.routeWebSocket(options.url, (ws) => {
      socket = ws;
      sockets.push(ws);
      ws.onMessage((message) => {
        const msg: WebsocketMessage = JSON.parse(String(message));
        incoming.push(msg);

        if (options.autoAck && msg.type === "connection_init") {
          dispatch({ type: "connection_ack" });
        }
      });
    });

    const subscriptions = () =>
      incoming.filter((msg) => msg.type === "subscribe") as SubscribeMessage[];
    const subscribers = (key: keyof Subs) =>
      subscriptions().filter((sub) => sub.payload?.operationName === key);

    use({
      incoming,
      outgoing,
      subscribers,
      dispatch: <K extends keyof Subs>(key: K, data?: Subs[K]) => {
        const subscription = subscribers(key)[0];

        if (!subscription) {
          throw new Error(`No subscription found for operation: ${String(key)}`);
        }

        const send = (data: Subs[K]) =>
          dispatch({
            id: subscription.id,
            type: "next",
            payload: { data },
          });

        if (data) {
          send(data);
        }

        return send;
      },
    });
  },
  {
    scope: "test",
    auto: true,
  },
];
