import { MimicComponentBaseProps } from "../components";

export type TitleProps = {
  title: string;
};
export type MimicComponentInstanceProps = MimicComponentBaseProps & {
  x?: number | string;
  y?: number | string;
  tagId?: string;
};
