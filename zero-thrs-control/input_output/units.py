# Per https://docs.google.com/document/d/11EGlLqZ21uHy4ICmhvPx9uKOwm0guKgWxY6-1zSQ2mQ/edit?tab=t.0#heading=h.l7ph84h61wda
from typing import Annotated

from pydantic import Field

type Celsius = Annotated[float, Field(ge=-273.15)]
type LMin = Annotated[float, Field(ge=0)]
type Hz = Annotated[float, Field(ge=0)]
type Ratio = Annotated[float, Field(ge=0, le=1)]
type Bar = Annotated[float, Field(ge=0)]
