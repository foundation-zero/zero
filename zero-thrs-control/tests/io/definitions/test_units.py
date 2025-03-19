from datetime import datetime

import pytest
from pydantic import ValidationError

from input_output.base import Stamped, StampedDf, ThrsModel
from input_output.definitions.units import LMin, unit_for_annotation, Ratio


def test_lmin():
    with pytest.raises(ValidationError):
        Stamped[LMin](value=-1, timestamp=datetime.now())


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
