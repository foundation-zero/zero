export type Stamped<T> = { value: T; timestamp: Date };

export type Field<T> = Record<string, Stamped<T>>;
export type Component = Record<string, Field<number>>;
