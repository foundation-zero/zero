# DC Converter

The DC converter asset card displays a converter identifier, title, mode, heat, delta-T, internal temperature, power, and live status squares for its Brightloop, Ugrid, or Shorepower channels.

## Usage

DC converter cards are rendered by the DC and Drives mimic `Assets` layers through `DcConverterInstance`. The instance receives generated converter sensor fields and renders the separate `DcConverterStatus` graphic in the card header. A single converter displays its yard tag without a range separator.

## Icon Slot

The `icon` slot replaces the default `ZiDcConverter` icon without changing the shared card contents. Shorepower uses the existing `MimicComponentType.DcConverter`, not a separate mimic type or instance wrapper:

```vue
<DcConverterInstance v-bind="converters.shorepower">
	<template #icon>
		<ZiPlug3 />
	</template>
</DcConverterInstance>
```

`ZiPlug3` is exported from `@/modules/common/components/icons`. The Shorepower group reads its mode from the Drives automatic mode; DC groups retain their existing DC automatic-mode bindings.

Heat and delta-T both use `sensors.heatTransfer`, a `HeatTransferDevice` field. The current Shorepower schema exposes only its active status, so its heat-transfer, temperature, and power readings use typed placeholders until those fields become available.

## Layout

- Default card size: `200 x 205`, configurable through `width` and `height`.
- Shorepower card size: `198 x 222`.
- Status graphic: one `12 x 12` square per channel, with `4px` gaps.
- Active channels use the `constructive` semantic token; inactive channels use `muted`.

## Groups

- `2073-2076`: Aft Brightloop channels.
- `2081-2082`: Ugrid channels.
- `2077-2078`: Forward Brightloop channels.
