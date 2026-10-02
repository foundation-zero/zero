# DC Converter

The DC converter asset card displays a converter group identifier, title, active status, and live status squares for its Brightloop or Ugrid channels.

## Usage

DC converter cards are rendered by the DC mimic `Assets` layer through `DcConverterInstance`. The instance receives generated `Brightloop` and `Ugrid` sensor fields and renders the separate `DcConverterStatus` graphic in the card header.

## Layout

- Card size: `200 x 198`.
- Status graphic: one `12 x 12` square per channel, with `4px` gaps.
- Active channels use the `constructive` semantic token; inactive channels use `muted`.

## Groups

- `2073-2076`: Aft Brightloop channels.
- `2081-2082`: Ugrid channels.
- `2077-2078`: Forward Brightloop channels.
