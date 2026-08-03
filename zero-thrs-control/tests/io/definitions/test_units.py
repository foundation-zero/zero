from datetime import datetime

import pytest
from pydantic import ValidationError

from thrs.input_output.base import Stamped, ThrsValues
from thrs.input_output.definitions.units import (
    LMin,
    PcsMode,
    Ratio,
    unit_for_annotation,
    zero_for_unit,
)


def test_lmin():
    with pytest.raises(ValidationError):
        Stamped[LMin](value=-2, timestamp=datetime.now())


def test_unit_for_annotation_stamped():
    class Data(ThrsValues):
        a: Stamped[Ratio]

    assert unit_for_annotation(Data.model_fields["a"].annotation) == Ratio


def test_unit_for_annotation_union_alias():
    class Data(ThrsValues):
        a: Stamped[Ratio]

    assert unit_for_annotation(Data.model_fields["a"].annotation) == Ratio


def test_zero_for_unit_float():
    assert zero_for_unit(float) == 0.0


def test_zero_for_unit_float_alias():
    assert zero_for_unit(Ratio) == 0.0


def test_zero_for_enum():
    assert zero_for_unit(PcsMode) == PcsMode.OFF


def test_zero_for_unnested():
    class Data(ThrsValues):
        a: float
        b: Ratio
        c: PcsMode

    zero = Data.zero()
    assert zero.a == 0.0
    assert zero.b == 0.0
    assert zero.c == PcsMode.OFF.value
