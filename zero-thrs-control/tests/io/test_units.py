from datetime import datetime

import pytest
from pydantic import ValidationError

from input_output.base import Stamped
from input_output.units import LMin


def test_lmin():
    with pytest.raises(ValidationError) as exc_info:
        Stamped[LMin](value=-1, timestamp=datetime.now())
