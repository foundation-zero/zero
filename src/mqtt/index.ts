import mqtt, { type IClientPublishOptions } from "mqtt";
import { fromEvent, merge, Observable } from "rxjs";
import { filter, ignoreElements, map, share } from "rxjs/operators";

type Message = {
  topic: string;
  message: string;
};

type Authentication = {
  username?: string;
  password?: string;
};

export class MqttClient {
  private messages: Observable<Message>;
  private constructor(private client: mqtt.MqttClient) {
    this.messages = fromEvent(client, "message", (topic, msg) => ({
      topic: topic as unknown as string,
      message: msg.toString(),
    })).pipe(share());
  }

  static async connect(url: string, auth: Authentication = {}): Promise<MqttClient> {
    const clientId = `hmi-${Math.random().toString(16).substring(2, 8)}`;
    const client = await mqtt.connectAsync(url, {
      ...auth,
      clientId,
    });

    return new MqttClient(client);
  }

  async publish<T = unknown>(
    topic: string,
    data: T,
    opts?: IClientPublishOptions,
  ): Promise<boolean> {
    try {
      const message = JSON.stringify(data);
      await this.client.publishAsync(topic, message, opts);
      return true;
    } catch (_e) {
      return false;
    }
  }

  topic(topic: string): Observable<string> {
    return merge(
      new Observable(() => {
        this.client.subscribe(topic);

        return () => {
          this.client.unsubscribe(topic);
        };
      }).pipe(ignoreElements()),
      this.messages.pipe(
        filter((msg) => topic === msg.topic),
        map((msg) => msg.message),
      ),
    );
  }
}
