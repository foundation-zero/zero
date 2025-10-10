SELECT
    sea_state,
    awa,
    aws,
    (pcs_mode).aft as pcs_mode_aft,
    (pcs_mode).fwd as pcs_mode_fwd,
    sails,
    time
FROM
    {{ ref('load_case')}}
