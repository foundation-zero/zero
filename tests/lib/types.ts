export type MessageType =
  | "connection_init"
  | "connection_ack"
  | "ping"
  | "pong"
  | "subscribe"
  | "next";

export interface KeepAlivePayload {
  message: "keepalive";
}

export interface ConnectionInitPayload {
  headers: Record<string, string>;
}

export interface GraphqlQueryPayload {
  query: string;
  variables?: Record<string, unknown>;
  operationName?: string;
}

export interface GraphqlDataPayload<T = unknown> {
  data: T;
}

export interface WebsocketMessage<
  Payload extends unknown | undefined = unknown,
  Type extends MessageType = MessageType,
> {
  id?: string;
  type: Type;
  payload?: Payload;
}

export type PingMessage = WebsocketMessage<KeepAlivePayload, "ping">;
export type PongMessage = WebsocketMessage<KeepAlivePayload, "pong">;
export type ConnectionInitMessage = WebsocketMessage<ConnectionInitPayload, "connection_init">;
export type SubscribeMessage = WebsocketMessage<GraphqlQueryPayload, "subscribe">;
export type ConnectionAckMessage = WebsocketMessage<undefined, "connection_ack">;
export type SubscriptionDataMessage = WebsocketMessage<GraphqlDataPayload, "next">;

export type Subscriptions = Record<string, unknown>;
export type Queries = Record<string, unknown>;

export interface MockSubscription<T> {
  subscribers: number;
  dispatch(data: T): void;
}
