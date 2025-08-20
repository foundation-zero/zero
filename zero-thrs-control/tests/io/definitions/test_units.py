from datetime import datetime

import pytest
from pydantic import ValidationError

from input_output.base import Stamped, StampedDf, ThrsModel
from input_output.definitions.units import (
    LMin,
    PcsMode,
    unit_for_annotation,
    Ratio,
    zero_for_unit,
)

def test_lmin():
    with pytest.raises(ValidationError):
        Stamped[LMin](value=-2, timestamp=datetime.now())


def test_unit_for_annotation_stamped():
    class Data(ThrsModel):
        a: Stamped[Ratio]

    assert unit_for_annotation(Data.model_fields["a"].annotation) == Ratio


def test_unit_for_annotation_stamped_df():
    class Data(ThrsModel):
        a: StampedDf[Ratio]

    assert unit_for_annotation(Data.model_fields["a"].annotation) == Ratio


def test_unit_for_annotation_union():
    class Data(ThrsModel):
        a: Stamped[Ratio] | StampedDf[Ratio]

    assert unit_for_annotation(Data.model_fields["a"].annotation) == Ratio


type Stamp[T] = Stamped[T] | StampedDf[T]


def test_unit_for_annotation_union_alias():
    class Data(ThrsModel):
        a: Stamp[Ratio]

    assert unit_for_annotation(Data.model_fields["a"].annotation) == Ratio


def test_zero_for_unit_float():
    assert zero_for_unit(float) == 0.0


def test_zero_for_unit_float_alias():
    assert zero_for_unit(Ratio) == 0.0


def test_zero_for_unit_literal():
    assert zero_for_unit(PcsMode) == "off"
