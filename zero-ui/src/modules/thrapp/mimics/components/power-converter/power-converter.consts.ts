import { ZiDcConverter, ZiPlug3 } from "@/modules/common/components/icons";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { Component } from "vue";
import { PowerConverterSourceType } from "./power-converter.types";

export const POWER_CONVERTER_WIDTH = 200;
export const POWER_CONVERTER_HEIGHT = 196;

export const POWER_CONVERTER_TITLES: Record<PowerConverterSourceType, string> = {
  [SensorComponentType.Brightloop]: "thrapp.mimics.converters.brightloop",
  [SensorComponentType.Ugrid]: "thrapp.mimics.converters.ugrid",
  [SensorComponentType.ShorePowerConverter]: "thrapp.mimics.converters.shorePower",
};

export const POWER_CONVERTER_ICONS: Record<PowerConverterSourceType, Component> = {
  [SensorComponentType.Brightloop]: ZiDcConverter,
  [SensorComponentType.Ugrid]: ZiDcConverter,
  [SensorComponentType.ShorePowerConverter]: ZiPlug3,
};
