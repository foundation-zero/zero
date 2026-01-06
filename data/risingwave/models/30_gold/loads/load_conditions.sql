SELECT
    time,
    sea_state,
    awa,
    aws,
    (pcs_mode).aft AS pcs_mode_aft,
    (pcs_mode).fwd AS pcs_mode_fwd,
    sails
FROM
    {{ ref('load_conditions_source')}}
