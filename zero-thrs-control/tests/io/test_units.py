from datetime import datetime
from pydantic import ValidationError
import pytest

from input_output.base import Stamped
from input_output.units import LMin


def test_lmin():
    with pytest.raises(ValidationError) as exc_info:
        Stamped[LMin](value=-1, timestamp=datetime.now())
