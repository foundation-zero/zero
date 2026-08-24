from typing import Annotated

from pydantic import Field

from .base import LoadsModel
from .units import Load, VariableMeta


class FiberOptic(LoadsModel):
    TOPIC = "fiber-optics/values"
    main_v1_sb: Annotated[
        Load,
        VariableMeta(display_name="V1 SB", scale_min=0, scale_max=85, unit="tonne"),
        Field(validation_alias="mm-rigging-load-v1-stbd"),
    ]
    main_v1_ps: Annotated[
        Load,
        VariableMeta(display_name="V1 PT", scale_min=0, scale_max=85, unit="tonne"),
        Field(validation_alias="mm-rigging-load-v1-port"),
    ]
    main_d1_sb: Annotated[
        Load,
        VariableMeta(display_name="D1 SB", scale_min=0, scale_max=43, unit="tonne"),
        Field(validation_alias="mm-rigging-load-d1-stbd"),
    ]
    main_d1_ps: Annotated[
        Load,
        VariableMeta(display_name="D1 PT", scale_min=0, scale_max=43, unit="tonne"),
        Field(validation_alias="mm-rigging-load-d1-port"),
    ]
    mizzen_v1_sb: Annotated[
        Load,
        VariableMeta(display_name="V1 SB", scale_min=0, scale_max=47, unit="tonne"),
        Field(validation_alias="mz-rigging-load-v1-stbd"),
    ]
    mizzen_v1_ps: Annotated[
        Load,
        VariableMeta(display_name="V1 PT", scale_min=0, scale_max=47, unit="tonne"),
        Field(validation_alias="mz-rigging-load-v1-port"),
    ]
    mizzen_d1_sb: Annotated[
        Load,
        VariableMeta(display_name="D1 SB", scale_min=0, scale_max=25, unit="tonne"),
        Field(validation_alias="mz-rigging-load-d1-stbd"),
    ]
    mizzen_d1_ps: Annotated[
        Load,
        VariableMeta(display_name="D1 PT", scale_min=0, scale_max=25, unit="tonne"),
        Field(validation_alias="mz-rigging-load-d1-port"),
    ]
    mizzen_forestay: Annotated[
        Load,
        VariableMeta(display_name="Forestay", scale_min=0, scale_max=31, unit="tonne"),
    ] = 0
    main_mast_bending_moment_fore_aft_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s1"),
    ]
    main_mast_bending_moment_fore_aft_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s2"),
    ]
    main_mast_bending_moment_fore_aft_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s3"),
    ]
    main_mast_bending_moment_fore_aft_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s4"),
    ]
    main_mast_bending_moment_fore_aft_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s5"),
    ]
    main_mast_bending_moment_fore_aft_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s6"),
    ]
    main_mast_bending_moment_fore_aft_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s7"),
    ]
    main_mast_bending_moment_fore_aft_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s8"),
    ]
    main_mast_bending_moment_fore_aft_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-fore-aft-s9"),
    ]
    main_mast_bending_moment_side_way_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s1"),
    ]
    main_mast_bending_moment_side_way_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s2"),
    ]
    main_mast_bending_moment_side_way_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s3"),
    ]
    main_mast_bending_moment_side_way_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s4"),
    ]
    main_mast_bending_moment_side_way_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s5"),
    ]
    main_mast_bending_moment_side_way_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s6"),
    ]
    main_mast_bending_moment_side_way_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s7"),
    ]
    main_mast_bending_moment_side_way_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s8"),
    ]
    main_mast_bending_moment_side_way_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-bending-moment-side-way-s9"),
    ]
    main_mast_bending_strain_fore_aft_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s1"),
    ]
    main_mast_bending_strain_fore_aft_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s2"),
    ]
    main_mast_bending_strain_fore_aft_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s3"),
    ]
    main_mast_bending_strain_fore_aft_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s4"),
    ]
    main_mast_bending_strain_fore_aft_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s5"),
    ]
    main_mast_bending_strain_fore_aft_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s6"),
    ]
    main_mast_bending_strain_fore_aft_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s7"),
    ]
    main_mast_bending_strain_fore_aft_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s8"),
    ]
    main_mast_bending_strain_fore_aft_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-fore-aft-s9"),
    ]
    main_mast_bending_strain_side_way_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s1"),
    ]
    main_mast_bending_strain_side_way_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s2"),
    ]
    main_mast_bending_strain_side_way_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s3"),
    ]
    main_mast_bending_strain_side_way_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s4"),
    ]
    main_mast_bending_strain_side_way_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s5"),
    ]
    main_mast_bending_strain_side_way_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s6"),
    ]
    main_mast_bending_strain_side_way_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s7"),
    ]
    main_mast_bending_strain_side_way_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s8"),
    ]
    main_mast_bending_strain_side_way_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-bending-strain-side-way-s9"),
    ]
    main_mast_fa_deflection_spr1: Annotated[
        float,
        VariableMeta(display_name="Spr1", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection-spr1"),
    ]
    main_mast_fa_deflection_spr2: Annotated[
        float,
        VariableMeta(display_name="Spr2", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection-spr2"),
    ]
    main_mast_fa_deflection_spr3: Annotated[
        float,
        VariableMeta(display_name="Spr3", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection-spr3"),
    ]
    main_mast_fa_deflection_spr4: Annotated[
        float,
        VariableMeta(display_name="Spr4", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection-spr4"),
    ]
    main_mast_fa_deflection_spr5: Annotated[
        float,
        VariableMeta(display_name="Spr5", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection-spr5"),
    ]
    main_mast_fa_deflection000: Annotated[
        float,
        VariableMeta(display_name="000", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection000"),
    ]
    main_mast_fa_deflection010: Annotated[
        float,
        VariableMeta(display_name="010", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection010"),
    ]
    main_mast_fa_deflection020: Annotated[
        float,
        VariableMeta(display_name="020", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection020"),
    ]
    main_mast_fa_deflection030: Annotated[
        float,
        VariableMeta(display_name="030", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection030"),
    ]
    main_mast_fa_deflection040: Annotated[
        float,
        VariableMeta(display_name="040", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection040"),
    ]
    main_mast_fa_deflection050: Annotated[
        float,
        VariableMeta(display_name="050", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection050"),
    ]
    main_mast_fa_deflection060: Annotated[
        float,
        VariableMeta(display_name="060", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection060"),
    ]
    main_mast_fa_deflection070: Annotated[
        float,
        VariableMeta(display_name="070", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection070"),
    ]
    main_mast_fa_deflection080: Annotated[
        float,
        VariableMeta(display_name="080", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection080"),
    ]
    main_mast_fa_deflection090: Annotated[
        float,
        VariableMeta(display_name="090", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection090"),
    ]
    main_mast_fa_deflection100: Annotated[
        float,
        VariableMeta(display_name="100", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-fa-deflection100"),
    ]
    main_mast_longitudinal_load_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s1"),
    ]
    main_mast_longitudinal_load_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s2"),
    ]
    main_mast_longitudinal_load_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s3"),
    ]
    main_mast_longitudinal_load_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s4"),
    ]
    main_mast_longitudinal_load_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s5"),
    ]
    main_mast_longitudinal_load_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s6"),
    ]
    main_mast_longitudinal_load_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s7"),
    ]
    main_mast_longitudinal_load_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s8"),
    ]
    main_mast_longitudinal_load_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="T.m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-load-s9"),
    ]
    main_mast_longitudinal_strain_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s1"),
    ]
    main_mast_longitudinal_strain_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s2"),
    ]
    main_mast_longitudinal_strain_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s3"),
    ]
    main_mast_longitudinal_strain_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s4"),
    ]
    main_mast_longitudinal_strain_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s5"),
    ]
    main_mast_longitudinal_strain_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s6"),
    ]
    main_mast_longitudinal_strain_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s7"),
    ]
    main_mast_longitudinal_strain_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s8"),
    ]
    main_mast_longitudinal_strain_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-longitudinal-strain-s9"),
    ]
    main_mast_strain_s1_aft_port: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s1-aft-port"),
    ]
    main_mast_strain_s1_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s1-aft-stbd"),
    ]
    main_mast_strain_s1_fore: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s1-fore"),
    ]
    main_mast_strain_s1_side_port: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s1-side-port"),
    ]
    main_mast_strain_s1_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s1-side-stbd"),
    ]
    main_mast_strain_s2_aft_port: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s2-aft-port"),
    ]
    main_mast_strain_s2_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s2-aft-stbd"),
    ]
    main_mast_strain_s2_fore: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s2-fore"),
    ]
    main_mast_strain_s2_side_port: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s2-side-port"),
    ]
    main_mast_strain_s2_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s2-side-stbd"),
    ]
    main_mast_strain_s3_aft_port: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s3-aft-port"),
    ]
    main_mast_strain_s3_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s3-aft-stbd"),
    ]
    main_mast_strain_s3_fore: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s3-fore"),
    ]
    main_mast_strain_s3_side_port: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s3-side-port"),
    ]
    main_mast_strain_s3_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s3-side-stbd"),
    ]
    main_mast_strain_s4_aft_port: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s4-aft-port"),
    ]
    main_mast_strain_s4_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s4-aft-stbd"),
    ]
    main_mast_strain_s4_fore: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s4-fore"),
    ]
    main_mast_strain_s4_side_port: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s4-side-port"),
    ]
    main_mast_strain_s4_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s4-side-stbd"),
    ]
    main_mast_strain_s5_aft_port: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s5-aft-port"),
    ]
    main_mast_strain_s5_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s5-aft-stbd"),
    ]
    main_mast_strain_s5_fore: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s5-fore"),
    ]
    main_mast_strain_s5_side_port: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s5-side-port"),
    ]
    main_mast_strain_s5_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s5-side-stbd"),
    ]
    main_mast_strain_s6_aft_port: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s6-aft-port"),
    ]
    main_mast_strain_s6_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s6-aft-stbd"),
    ]
    main_mast_strain_s6_fore: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s6-fore"),
    ]
    main_mast_strain_s6_side_port: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s6-side-port"),
    ]
    main_mast_strain_s6_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s6-side-stbd"),
    ]
    main_mast_strain_s7_aft_port: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s7-aft-port"),
    ]
    main_mast_strain_s7_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s7-aft-stbd"),
    ]
    main_mast_strain_s7_fore: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s7-fore"),
    ]
    main_mast_strain_s7_side_port: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s7-side-port"),
    ]
    main_mast_strain_s7_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s7-side-stbd"),
    ]
    main_mast_strain_s8_aft_port: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s8-aft-port"),
    ]
    main_mast_strain_s8_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s8-aft-stbd"),
    ]
    main_mast_strain_s8_fore: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s8-fore"),
    ]
    main_mast_strain_s8_side_port: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s8-side-port"),
    ]
    main_mast_strain_s8_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s8-side-stbd"),
    ]
    main_mast_strain_s9_aft_port: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s9-aft-port"),
    ]
    main_mast_strain_s9_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s9-aft-stbd"),
    ]
    main_mast_strain_s9_fore: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s9-fore"),
    ]
    main_mast_strain_s9_side_port: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s9-side-port"),
    ]
    main_mast_strain_s9_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mm-mast-strain-s9-side-stbd"),
    ]
    main_mast_sw_deflection_spr1: Annotated[
        float,
        VariableMeta(display_name="Spr1", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection-spr1"),
    ]
    main_mast_sw_deflection_spr2: Annotated[
        float,
        VariableMeta(display_name="Spr2", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection-spr2"),
    ]
    main_mast_sw_deflection_spr3: Annotated[
        float,
        VariableMeta(display_name="Spr3", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection-spr3"),
    ]
    main_mast_sw_deflection_spr4: Annotated[
        float,
        VariableMeta(display_name="Spr4", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection-spr4"),
    ]
    main_mast_sw_deflection_spr5: Annotated[
        float,
        VariableMeta(display_name="Spr5", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection-spr5"),
    ]
    main_mast_sw_deflection000: Annotated[
        float,
        VariableMeta(display_name="000", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection000"),
    ]
    main_mast_sw_deflection010: Annotated[
        float,
        VariableMeta(display_name="010", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection010"),
    ]
    main_mast_sw_deflection020: Annotated[
        float,
        VariableMeta(display_name="020", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection020"),
    ]
    main_mast_sw_deflection030: Annotated[
        float,
        VariableMeta(display_name="030", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection030"),
    ]
    main_mast_sw_deflection040: Annotated[
        float,
        VariableMeta(display_name="040", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection040"),
    ]
    main_mast_sw_deflection050: Annotated[
        float,
        VariableMeta(display_name="050", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection050"),
    ]
    main_mast_sw_deflection060: Annotated[
        float,
        VariableMeta(display_name="060", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection060"),
    ]
    main_mast_sw_deflection070: Annotated[
        float,
        VariableMeta(display_name="070", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection070"),
    ]
    main_mast_sw_deflection080: Annotated[
        float,
        VariableMeta(display_name="080", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection080"),
    ]
    main_mast_sw_deflection090: Annotated[
        float,
        VariableMeta(display_name="090", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection090"),
    ]
    main_mast_sw_deflection100: Annotated[
        float,
        VariableMeta(display_name="100", unit="mm", type="actual"),
        Field(validation_alias="mm-mast-sw-deflection100"),
    ]
    main_mast_temperature_spr0_port: Annotated[
        float,
        VariableMeta(display_name="Spr0 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr0-port"),
    ]
    main_mast_temperature_spr1_fore: Annotated[
        float,
        VariableMeta(display_name="Spr1 Fore", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr1-fore"),
    ]
    main_mast_temperature_spr1_port: Annotated[
        float,
        VariableMeta(display_name="Spr1 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr1-port"),
    ]
    main_mast_temperature_spr1_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr1 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr1-stbd"),
    ]
    main_mast_temperature_spr2_fore: Annotated[
        float,
        VariableMeta(display_name="Spr2 Fore", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr2-fore"),
    ]
    main_mast_temperature_spr2_port: Annotated[
        float,
        VariableMeta(display_name="Spr2 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr2-port"),
    ]
    main_mast_temperature_spr2_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr2 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr2-stbd"),
    ]
    main_mast_temperature_spr3_port: Annotated[
        float,
        VariableMeta(display_name="Spr3 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr3-port"),
    ]
    main_mast_temperature_spr3_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr3 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr3-stbd"),
    ]
    main_mast_temperature_spr4_aft_port: Annotated[
        float,
        VariableMeta(display_name="Spr4 Aft PT", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr4-aft-port"),
    ]
    main_mast_temperature_spr4_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr4 Aft SB", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr4-aft-stbd"),
    ]
    main_mast_temperature_spr4_fore: Annotated[
        float,
        VariableMeta(display_name="Spr4 Fore", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr4-fore"),
    ]
    main_mast_temperature_spr5_fore: Annotated[
        float,
        VariableMeta(display_name="Spr5 Fore", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr5-fore"),
    ]
    main_mast_temperature_spr5_side_port: Annotated[
        float,
        VariableMeta(display_name="Spr5 Side PT", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr5-side-port"),
    ]
    main_mast_temperature_spr5_side_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr5 Side SB", unit="degC", type="actual"),
        Field(validation_alias="mm-mast-temperature-spr5-side-stbd"),
    ]
    main_rigging_load_d2_port: Annotated[
        float,
        VariableMeta(display_name="D2 PT", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-load-d2-port"),
    ]
    main_rigging_load_d2_stbd: Annotated[
        float,
        VariableMeta(display_name="D2 SB", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-load-d2-stbd"),
    ]
    main_rigging_load_d3_port: Annotated[
        float,
        VariableMeta(display_name="D3 PT", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-load-d3-port"),
    ]
    main_rigging_load_d3_stbd: Annotated[
        float,
        VariableMeta(display_name="D3 SB", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-load-d3-stbd"),
    ]
    main_rigging_load_d4_port: Annotated[
        float,
        VariableMeta(display_name="D4 PT", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-load-d4-port"),
    ]
    main_rigging_load_d4_stbd: Annotated[
        float,
        VariableMeta(display_name="D4 SB", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-load-d4-stbd"),
    ]
    main_rigging_load_d5_port: Annotated[
        float,
        VariableMeta(display_name="D5 PT", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-load-d5-port"),
    ]
    main_rigging_load_d5_stbd: Annotated[
        float,
        VariableMeta(display_name="D5 SB", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-load-d5-stbd"),
    ]
    main_rigging_strain_d1_port: Annotated[
        float,
        VariableMeta(display_name="D1 PT", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d1-port"),
    ]
    main_rigging_strain_d1_stbd: Annotated[
        float,
        VariableMeta(display_name="D1 SB", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d1-stbd"),
    ]
    main_rigging_strain_d2_port: Annotated[
        float,
        VariableMeta(display_name="D2 PT", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d2-port"),
    ]
    main_rigging_strain_d2_stbd: Annotated[
        float,
        VariableMeta(display_name="D2 SB", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d2-stbd"),
    ]
    main_rigging_strain_d3_port: Annotated[
        float,
        VariableMeta(display_name="D3 PT", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d3-port"),
    ]
    main_rigging_strain_d3_stbd: Annotated[
        float,
        VariableMeta(display_name="D3 SB", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d3-stbd"),
    ]
    main_rigging_strain_d4_port: Annotated[
        float,
        VariableMeta(display_name="D4 PT", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d4-port"),
    ]
    main_rigging_strain_d4_stbd: Annotated[
        float,
        VariableMeta(display_name="D4 SB", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d4-stbd"),
    ]
    main_rigging_strain_d5_port: Annotated[
        float,
        VariableMeta(display_name="D5 PT", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d5-port"),
    ]
    main_rigging_strain_d5_stbd: Annotated[
        float,
        VariableMeta(display_name="D5 SB", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-d5-stbd"),
    ]
    main_rigging_strain_v1_port: Annotated[
        float,
        VariableMeta(display_name="V1 PT", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-v1-port"),
    ]
    main_rigging_strain_v1_stbd: Annotated[
        float,
        VariableMeta(display_name="V1 SB", unit="um/m", type="actual"),
        Field(validation_alias="mm-rigging-strain-v1-stbd"),
    ]
    main_rigging_sum_load_v1_port: Annotated[
        float,
        VariableMeta(display_name="V1 PT", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-sum-load-v1-port"),
    ]
    main_rigging_sum_load_v1_stbd: Annotated[
        float,
        VariableMeta(display_name="V1 SB", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-sum-load-v1-stbd"),
    ]
    main_rigging_sum_load_v2_port: Annotated[
        float,
        VariableMeta(display_name="V2 PT", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-sum-load-v2-port"),
    ]
    main_rigging_sum_load_v2_stbd: Annotated[
        float,
        VariableMeta(display_name="V2 SB", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-sum-load-v2-stbd"),
    ]
    main_rigging_sum_load_v3_port: Annotated[
        float,
        VariableMeta(display_name="V3 PT", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-sum-load-v3-port"),
    ]
    main_rigging_sum_load_v3_stbd: Annotated[
        float,
        VariableMeta(display_name="V3 SB", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-sum-load-v3-stbd"),
    ]
    main_rigging_sum_load_v4_port: Annotated[
        float,
        VariableMeta(display_name="V4 PT", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-sum-load-v4-port"),
    ]
    main_rigging_sum_load_v4_stbd: Annotated[
        float,
        VariableMeta(display_name="V4 SB", unit="tonne", type="actual"),
        Field(validation_alias="mm-rigging-sum-load-v4-stbd"),
    ]
    main_rigging_temperature_d1_port: Annotated[
        float,
        VariableMeta(display_name="D1 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d1-port"),
    ]
    main_rigging_temperature_d1_stbd: Annotated[
        float,
        VariableMeta(display_name="D1 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d1-stbd"),
    ]
    main_rigging_temperature_d2_port: Annotated[
        float,
        VariableMeta(display_name="D2 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d2-port"),
    ]
    main_rigging_temperature_d2_stbd: Annotated[
        float,
        VariableMeta(display_name="D2 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d2-stbd"),
    ]
    main_rigging_temperature_d3_port: Annotated[
        float,
        VariableMeta(display_name="D3 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d3-port"),
    ]
    main_rigging_temperature_d3_stbd: Annotated[
        float,
        VariableMeta(display_name="D3 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d3-stbd"),
    ]
    main_rigging_temperature_d4_port: Annotated[
        float,
        VariableMeta(display_name="D4 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d4-port"),
    ]
    main_rigging_temperature_d4_stbd: Annotated[
        float,
        VariableMeta(display_name="D4 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d4-stbd"),
    ]
    main_rigging_temperature_d5_port: Annotated[
        float,
        VariableMeta(display_name="D5 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d5-port"),
    ]
    main_rigging_temperature_d5_stbd: Annotated[
        float,
        VariableMeta(display_name="D5 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-d5-stbd"),
    ]
    main_rigging_temperature_v1_port: Annotated[
        float,
        VariableMeta(display_name="V1 PT", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-v1-port"),
    ]
    main_rigging_temperature_v1_stbd: Annotated[
        float,
        VariableMeta(display_name="V1 SB", unit="degC", type="actual"),
        Field(validation_alias="mm-rigging-temperature-v1-stbd"),
    ]
    mizzen_mast_bending_moment_fore_aft_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s1"),
    ]
    mizzen_mast_bending_moment_fore_aft_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s2"),
    ]
    mizzen_mast_bending_moment_fore_aft_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s3"),
    ]
    mizzen_mast_bending_moment_fore_aft_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s4"),
    ]
    mizzen_mast_bending_moment_fore_aft_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s5"),
    ]
    mizzen_mast_bending_moment_fore_aft_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s6"),
    ]
    mizzen_mast_bending_moment_fore_aft_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s7"),
    ]
    mizzen_mast_bending_moment_fore_aft_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s8"),
    ]
    mizzen_mast_bending_moment_fore_aft_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-fore-aft-s9"),
    ]
    mizzen_mast_bending_moment_side_way_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s1"),
    ]
    mizzen_mast_bending_moment_side_way_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s2"),
    ]
    mizzen_mast_bending_moment_side_way_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s3"),
    ]
    mizzen_mast_bending_moment_side_way_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s4"),
    ]
    mizzen_mast_bending_moment_side_way_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s5"),
    ]
    mizzen_mast_bending_moment_side_way_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s6"),
    ]
    mizzen_mast_bending_moment_side_way_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s7"),
    ]
    mizzen_mast_bending_moment_side_way_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s8"),
    ]
    mizzen_mast_bending_moment_side_way_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-bending-moment-side-way-s9"),
    ]
    mizzen_mast_bending_strain_fore_aft_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s1"),
    ]
    mizzen_mast_bending_strain_fore_aft_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s2"),
    ]
    mizzen_mast_bending_strain_fore_aft_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s3"),
    ]
    mizzen_mast_bending_strain_fore_aft_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s4"),
    ]
    mizzen_mast_bending_strain_fore_aft_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s5"),
    ]
    mizzen_mast_bending_strain_fore_aft_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s6"),
    ]
    mizzen_mast_bending_strain_fore_aft_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s7"),
    ]
    mizzen_mast_bending_strain_fore_aft_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s8"),
    ]
    mizzen_mast_bending_strain_fore_aft_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-fore-aft-s9"),
    ]
    mizzen_mast_bending_strain_side_way_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s1"),
    ]
    mizzen_mast_bending_strain_side_way_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s2"),
    ]
    mizzen_mast_bending_strain_side_way_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s3"),
    ]
    mizzen_mast_bending_strain_side_way_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s4"),
    ]
    mizzen_mast_bending_strain_side_way_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s5"),
    ]
    mizzen_mast_bending_strain_side_way_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s6"),
    ]
    mizzen_mast_bending_strain_side_way_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s7"),
    ]
    mizzen_mast_bending_strain_side_way_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s8"),
    ]
    mizzen_mast_bending_strain_side_way_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-bending-strain-side-way-s9"),
    ]
    mizzen_mast_fa_deflection_spr1: Annotated[
        float,
        VariableMeta(display_name="Spr1", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection-spr1"),
    ]
    mizzen_mast_fa_deflection_spr2: Annotated[
        float,
        VariableMeta(display_name="Spr2", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection-spr2"),
    ]
    mizzen_mast_fa_deflection_spr3: Annotated[
        float,
        VariableMeta(display_name="Spr3", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection-spr3"),
    ]
    mizzen_mast_fa_deflection_spr4: Annotated[
        float,
        VariableMeta(display_name="Spr4", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection-spr4"),
    ]
    mizzen_mast_fa_deflection_spr5: Annotated[
        float,
        VariableMeta(display_name="Spr5", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection-spr5"),
    ]
    mizzen_mast_fa_deflection000: Annotated[
        float,
        VariableMeta(display_name="000", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection000"),
    ]
    mizzen_mast_fa_deflection010: Annotated[
        float,
        VariableMeta(display_name="010", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection010"),
    ]
    mizzen_mast_fa_deflection020: Annotated[
        float,
        VariableMeta(display_name="020", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection020"),
    ]
    mizzen_mast_fa_deflection030: Annotated[
        float,
        VariableMeta(display_name="030", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection030"),
    ]
    mizzen_mast_fa_deflection040: Annotated[
        float,
        VariableMeta(display_name="040", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection040"),
    ]
    mizzen_mast_fa_deflection050: Annotated[
        float,
        VariableMeta(display_name="050", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection050"),
    ]
    mizzen_mast_fa_deflection060: Annotated[
        float,
        VariableMeta(display_name="060", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection060"),
    ]
    mizzen_mast_fa_deflection070: Annotated[
        float,
        VariableMeta(display_name="070", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection070"),
    ]
    mizzen_mast_fa_deflection080: Annotated[
        float,
        VariableMeta(display_name="080", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection080"),
    ]
    mizzen_mast_fa_deflection090: Annotated[
        float,
        VariableMeta(display_name="090", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection090"),
    ]
    mizzen_mast_fa_deflection100: Annotated[
        float,
        VariableMeta(display_name="100", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-fa-deflection100"),
    ]
    mizzen_mast_longitudinal_load_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s1"),
    ]
    mizzen_mast_longitudinal_load_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s2"),
    ]
    mizzen_mast_longitudinal_load_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s3"),
    ]
    mizzen_mast_longitudinal_load_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s4"),
    ]
    mizzen_mast_longitudinal_load_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s5"),
    ]
    mizzen_mast_longitudinal_load_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s6"),
    ]
    mizzen_mast_longitudinal_load_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s7"),
    ]
    mizzen_mast_longitudinal_load_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s8"),
    ]
    mizzen_mast_longitudinal_load_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="T.m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-load-s9"),
    ]
    mizzen_mast_longitudinal_strain_s1: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s1"),
    ]
    mizzen_mast_longitudinal_strain_s2: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s2"),
    ]
    mizzen_mast_longitudinal_strain_s3: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s3"),
    ]
    mizzen_mast_longitudinal_strain_s4: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s4"),
    ]
    mizzen_mast_longitudinal_strain_s5: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s5"),
    ]
    mizzen_mast_longitudinal_strain_s6: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s6"),
    ]
    mizzen_mast_longitudinal_strain_s7: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s7"),
    ]
    mizzen_mast_longitudinal_strain_s8: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s8"),
    ]
    mizzen_mast_longitudinal_strain_s9: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-longitudinal-strain-s9"),
    ]
    mizzen_mast_strain_s1_aft_port: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s1-aft-port"),
    ]
    mizzen_mast_strain_s1_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s1-aft-stbd"),
    ]
    mizzen_mast_strain_s1_side_port: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s1-side-port"),
    ]
    mizzen_mast_strain_s1_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S1", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s1-side-stbd"),
    ]
    mizzen_mast_strain_s2_aft_port: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s2-aft-port"),
    ]
    mizzen_mast_strain_s2_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s2-aft-stbd"),
    ]
    mizzen_mast_strain_s2_fore: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s2-fore"),
    ]
    mizzen_mast_strain_s2_side_port: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s2-side-port"),
    ]
    mizzen_mast_strain_s2_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S2", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s2-side-stbd"),
    ]
    mizzen_mast_strain_s3_aft_port: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s3-aft-port"),
    ]
    mizzen_mast_strain_s3_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s3-aft-stbd"),
    ]
    mizzen_mast_strain_s3_fore: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s3-fore"),
    ]
    mizzen_mast_strain_s3_side_port: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s3-side-port"),
    ]
    mizzen_mast_strain_s3_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S3", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s3-side-stbd"),
    ]
    mizzen_mast_strain_s4_aft_port: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s4-aft-port"),
    ]
    mizzen_mast_strain_s4_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s4-aft-stbd"),
    ]
    mizzen_mast_strain_s4_fore: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s4-fore"),
    ]
    mizzen_mast_strain_s4_side_port: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s4-side-port"),
    ]
    mizzen_mast_strain_s4_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S4", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s4-side-stbd"),
    ]
    mizzen_mast_strain_s5_aft_port: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s5-aft-port"),
    ]
    mizzen_mast_strain_s5_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s5-aft-stbd"),
    ]
    mizzen_mast_strain_s5_fore: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s5-fore"),
    ]
    mizzen_mast_strain_s5_side_port: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s5-side-port"),
    ]
    mizzen_mast_strain_s5_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S5", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s5-side-stbd"),
    ]
    mizzen_mast_strain_s6_aft_port: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s6-aft-port"),
    ]
    mizzen_mast_strain_s6_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s6-aft-stbd"),
    ]
    mizzen_mast_strain_s6_fore: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s6-fore"),
    ]
    mizzen_mast_strain_s6_side_port: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s6-side-port"),
    ]
    mizzen_mast_strain_s6_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S6", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s6-side-stbd"),
    ]
    mizzen_mast_strain_s7_aft_port: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s7-aft-port"),
    ]
    mizzen_mast_strain_s7_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s7-aft-stbd"),
    ]
    mizzen_mast_strain_s7_fore: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s7-fore"),
    ]
    mizzen_mast_strain_s7_side_port: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s7-side-port"),
    ]
    mizzen_mast_strain_s7_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S7", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s7-side-stbd"),
    ]
    mizzen_mast_strain_s8_aft_port: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s8-aft-port"),
    ]
    mizzen_mast_strain_s8_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s8-aft-stbd"),
    ]
    mizzen_mast_strain_s8_fore: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s8-fore"),
    ]
    mizzen_mast_strain_s8_side_port: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s8-side-port"),
    ]
    mizzen_mast_strain_s8_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S8", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s8-side-stbd"),
    ]
    mizzen_mast_strain_s9_aft_port: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s9-aft-port"),
    ]
    mizzen_mast_strain_s9_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s9-aft-stbd"),
    ]
    mizzen_mast_strain_s9_fore: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s9-fore"),
    ]
    mizzen_mast_strain_s9_side_port: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s9-side-port"),
    ]
    mizzen_mast_strain_s9_side_stbd: Annotated[
        float,
        VariableMeta(display_name="S9", unit="um/m", type="actual"),
        Field(validation_alias="mz-mast-strain-s9-side-stbd"),
    ]
    mizzen_mast_sw_deflection_spr1: Annotated[
        float,
        VariableMeta(display_name="Spr1", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection-spr1"),
    ]
    mizzen_mast_sw_deflection_spr2: Annotated[
        float,
        VariableMeta(display_name="Spr2", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection-spr2"),
    ]
    mizzen_mast_sw_deflection_spr3: Annotated[
        float,
        VariableMeta(display_name="Spr3", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection-spr3"),
    ]
    mizzen_mast_sw_deflection_spr4: Annotated[
        float,
        VariableMeta(display_name="Spr4", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection-spr4"),
    ]
    mizzen_mast_sw_deflection_spr5: Annotated[
        float,
        VariableMeta(display_name="Spr5", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection-spr5"),
    ]
    mizzen_mast_sw_deflection000: Annotated[
        float,
        VariableMeta(display_name="000", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection000"),
    ]
    mizzen_mast_sw_deflection010: Annotated[
        float,
        VariableMeta(display_name="010", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection010"),
    ]
    mizzen_mast_sw_deflection020: Annotated[
        float,
        VariableMeta(display_name="020", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection020"),
    ]
    mizzen_mast_sw_deflection030: Annotated[
        float,
        VariableMeta(display_name="030", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection030"),
    ]
    mizzen_mast_sw_deflection040: Annotated[
        float,
        VariableMeta(display_name="040", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection040"),
    ]
    mizzen_mast_sw_deflection050: Annotated[
        float,
        VariableMeta(display_name="050", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection050"),
    ]
    mizzen_mast_sw_deflection060: Annotated[
        float,
        VariableMeta(display_name="060", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection060"),
    ]
    mizzen_mast_sw_deflection070: Annotated[
        float,
        VariableMeta(display_name="070", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection070"),
    ]
    mizzen_mast_sw_deflection080: Annotated[
        float,
        VariableMeta(display_name="080", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection080"),
    ]
    mizzen_mast_sw_deflection090: Annotated[
        float,
        VariableMeta(display_name="090", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection090"),
    ]
    mizzen_mast_sw_deflection100: Annotated[
        float,
        VariableMeta(display_name="100", unit="mm", type="actual"),
        Field(validation_alias="mz-mast-sw-deflection100"),
    ]
    mizzen_mast_temperature_spr0_port: Annotated[
        float,
        VariableMeta(display_name="Spr0 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr0-port"),
    ]
    mizzen_mast_temperature_spr1_fore: Annotated[
        float,
        VariableMeta(display_name="Spr1 Fore", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr1-fore"),
    ]
    mizzen_mast_temperature_spr1_port: Annotated[
        float,
        VariableMeta(display_name="Spr1 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr1-port"),
    ]
    mizzen_mast_temperature_spr1_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr1 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr1-stbd"),
    ]
    mizzen_mast_temperature_spr2_fore: Annotated[
        float,
        VariableMeta(display_name="Spr2 Fore", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr2-fore"),
    ]
    mizzen_mast_temperature_spr2_port: Annotated[
        float,
        VariableMeta(display_name="Spr2 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr2-port"),
    ]
    mizzen_mast_temperature_spr2_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr2 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr2-stbd"),
    ]
    mizzen_mast_temperature_spr3_port: Annotated[
        float,
        VariableMeta(display_name="Spr3 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr3-port"),
    ]
    mizzen_mast_temperature_spr3_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr3 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr3-stbd"),
    ]
    mizzen_mast_temperature_spr4_aft_port: Annotated[
        float,
        VariableMeta(display_name="Spr4 Aft PT", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr4-aft-port"),
    ]
    mizzen_mast_temperature_spr4_aft_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr4 Aft SB", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr4-aft-stbd"),
    ]
    mizzen_mast_temperature_spr4_fore: Annotated[
        float,
        VariableMeta(display_name="Spr4 Fore", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr4-fore"),
    ]
    mizzen_mast_temperature_spr5_fore: Annotated[
        float,
        VariableMeta(display_name="Spr5 Fore", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr5-fore"),
    ]
    mizzen_mast_temperature_spr5_side_port: Annotated[
        float,
        VariableMeta(display_name="Spr5 Side PT", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr5-side-port"),
    ]
    mizzen_mast_temperature_spr5_side_stbd: Annotated[
        float,
        VariableMeta(display_name="Spr5 Side SB", unit="degC", type="actual"),
        Field(validation_alias="mz-mast-temperature-spr5-side-stbd"),
    ]
    mizzen_rigging_load_d2_port: Annotated[
        float,
        VariableMeta(display_name="D2 PT", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-load-d2-port"),
    ]
    mizzen_rigging_load_d2_stbd: Annotated[
        float,
        VariableMeta(display_name="D2 SB", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-load-d2-stbd"),
    ]
    mizzen_rigging_load_d3_port: Annotated[
        float,
        VariableMeta(display_name="D3 PT", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-load-d3-port"),
    ]
    mizzen_rigging_load_d3_stbd: Annotated[
        float,
        VariableMeta(display_name="D3 SB", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-load-d3-stbd"),
    ]
    mizzen_rigging_load_d4_port: Annotated[
        float,
        VariableMeta(display_name="D4 PT", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-load-d4-port"),
    ]
    mizzen_rigging_load_d4_stbd: Annotated[
        float,
        VariableMeta(display_name="D4 SB", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-load-d4-stbd"),
    ]
    mizzen_rigging_load_d5_port: Annotated[
        float,
        VariableMeta(display_name="D5 PT", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-load-d5-port"),
    ]
    mizzen_rigging_load_d5_stbd: Annotated[
        float,
        VariableMeta(display_name="D5 SB", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-load-d5-stbd"),
    ]
    mizzen_rigging_strain_d1_port: Annotated[
        float,
        VariableMeta(display_name="D1 PT", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d1-port"),
    ]
    mizzen_rigging_strain_d1_stbd: Annotated[
        float,
        VariableMeta(display_name="D1 SB", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d1-stbd"),
    ]
    mizzen_rigging_strain_d2_port: Annotated[
        float,
        VariableMeta(display_name="D2 PT", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d2-port"),
    ]
    mizzen_rigging_strain_d2_stbd: Annotated[
        float,
        VariableMeta(display_name="D2 SB", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d2-stbd"),
    ]
    mizzen_rigging_strain_d3_port: Annotated[
        float,
        VariableMeta(display_name="D3 PT", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d3-port"),
    ]
    mizzen_rigging_strain_d3_stbd: Annotated[
        float,
        VariableMeta(display_name="D3 SB", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d3-stbd"),
    ]
    mizzen_rigging_strain_d4_port: Annotated[
        float,
        VariableMeta(display_name="D4 PT", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d4-port"),
    ]
    mizzen_rigging_strain_d4_stbd: Annotated[
        float,
        VariableMeta(display_name="D4 SB", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d4-stbd"),
    ]
    mizzen_rigging_strain_d5_port: Annotated[
        float,
        VariableMeta(display_name="D5 PT", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d5-port"),
    ]
    mizzen_rigging_strain_d5_stbd: Annotated[
        float,
        VariableMeta(display_name="D5 SB", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-d5-stbd"),
    ]
    mizzen_rigging_strain_v1_port: Annotated[
        float,
        VariableMeta(display_name="V1 PT", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-v1-port"),
    ]
    mizzen_rigging_strain_v1_stbd: Annotated[
        float,
        VariableMeta(display_name="V1 SB", unit="um/m", type="actual"),
        Field(validation_alias="mz-rigging-strain-v1-stbd"),
    ]
    mizzen_rigging_sum_load_v1_port: Annotated[
        float,
        VariableMeta(display_name="V1 PT", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-sum-load-v1-port"),
    ]
    mizzen_rigging_sum_load_v1_stbd: Annotated[
        float,
        VariableMeta(display_name="V1 SB", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-sum-load-v1-stbd"),
    ]
    mizzen_rigging_sum_load_v2_port: Annotated[
        float,
        VariableMeta(display_name="V2 PT", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-sum-load-v2-port"),
    ]
    mizzen_rigging_sum_load_v2_stbd: Annotated[
        float,
        VariableMeta(display_name="V2 SB", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-sum-load-v2-stbd"),
    ]
    mizzen_rigging_sum_load_v3_port: Annotated[
        float,
        VariableMeta(display_name="V3 PT", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-sum-load-v3-port"),
    ]
    mizzen_rigging_sum_load_v3_stbd: Annotated[
        float,
        VariableMeta(display_name="V3 SB", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-sum-load-v3-stbd"),
    ]
    mizzen_rigging_sum_load_v4_port: Annotated[
        float,
        VariableMeta(display_name="V4 PT", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-sum-load-v4-port"),
    ]
    mizzen_rigging_sum_load_v4_stbd: Annotated[
        float,
        VariableMeta(display_name="V4 SB", unit="tonne", type="actual"),
        Field(validation_alias="mz-rigging-sum-load-v4-stbd"),
    ]
    mizzen_rigging_temperature_d1_port: Annotated[
        float,
        VariableMeta(display_name="D1 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d1-port"),
    ]
    mizzen_rigging_temperature_d1_stbd: Annotated[
        float,
        VariableMeta(display_name="D1 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d1-stbd"),
    ]
    mizzen_rigging_temperature_d2_port: Annotated[
        float,
        VariableMeta(display_name="D2 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d2-port"),
    ]
    mizzen_rigging_temperature_d2_stbd: Annotated[
        float,
        VariableMeta(display_name="D2 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d2-stbd"),
    ]
    mizzen_rigging_temperature_d3_port: Annotated[
        float,
        VariableMeta(display_name="D3 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d3-port"),
    ]
    mizzen_rigging_temperature_d3_stbd: Annotated[
        float,
        VariableMeta(display_name="D3 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d3-stbd"),
    ]
    mizzen_rigging_temperature_d4_port: Annotated[
        float,
        VariableMeta(display_name="D4 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d4-port"),
    ]
    mizzen_rigging_temperature_d4_stbd: Annotated[
        float,
        VariableMeta(display_name="D4 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d4-stbd"),
    ]
    mizzen_rigging_temperature_d5_port: Annotated[
        float,
        VariableMeta(display_name="D5 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d5-port"),
    ]
    mizzen_rigging_temperature_d5_stbd: Annotated[
        float,
        VariableMeta(display_name="D5 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-d5-stbd"),
    ]
    mizzen_rigging_temperature_v1_port: Annotated[
        float,
        VariableMeta(display_name="V1 PT", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-v1-port"),
    ]
    mizzen_rigging_temperature_v1_stbd: Annotated[
        float,
        VariableMeta(display_name="V1 SB", unit="degC", type="actual"),
        Field(validation_alias="mz-rigging-temperature-v1-stbd"),
    ]
