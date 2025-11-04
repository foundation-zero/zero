from typing import Annotated

from .units import Load, LoadsModel, RelativePosition, component_meta


class SailSystems(LoadsModel):
    main_sheet_load: Annotated[Load, component_meta(name="main_sheet")]
    main_sheet_position: Annotated[RelativePosition, component_meta(name="main_sheet")]
