/*
 * Normally this metadata should be loaded into a seed table.
 * However, it is currently not possible to create tables the normal way, because GreptimeDB demands that each table has a time index constraint.
 * Therefore we cannot use seeds or create tables in silver/gold layer the usual way; dbt uses regular "CREATE TABLE" statements that lack the time index constraint.
 * 
 * The only (simple) solution at the moment is to create a table using a macro.
*/

-- TODO: Create dbt plugin for greptime which seeds with an epoch time index

{% macro load_24vdc_metadata() %}

    {% set target_table = 'dc_24v_metadata' %}

    {% set query %}
        DROP TABLE IF EXISTS {{ target_table }};

        CREATE TABLE {{ target_table }} (
            ts TIMESTAMP,
            "description" STRING,
            "name" STRING,
            topic STRING,
            converter STRING,
            converter_subnr INT,
            main_group STRING,
            sub_group STRING,
            TIME INDEX (ts),
            PRIMARY KEY (topic)
        );

        INSERT INTO {{ target_table }} (ts, description, name, topic, converter, converter_subnr, main_group, sub_group)
        VALUES
            ('1970-01-01 00:00:00', 'Converter W14E1_01V01', 'W14E1_01V01', 'marpower/450000-24vdc-system/conv/w14e1-01v01', 'W14E1_01', 1, NULL, NULL),
            ('1970-01-01 00:00:00', 'Converter W14E1_01V02', 'W14E1_01V02', 'marpower/450000-24vdc-system/conv/w14e1-01v02', 'W14E1_01', 2, NULL, NULL),
            ('1970-01-01 00:00:00', 'Converter W14E1_02V01', 'W14E1_02V01', 'marpower/450000-24vdc-system/conv/w14e1-02v01', 'W14E1_02', 1, NULL, NULL),
            ('1970-01-01 00:00:00', 'Converter W14E1_02V02', 'W14E1_02V02', 'marpower/450000-24vdc-system/conv/w14e1-02v02', 'W14E1_02', 2, NULL, NULL),
            ('1970-01-01 00:00:00', 'Converter W14E2_01V01', 'W14E2_01V01', 'marpower/450000-24vdc-system/conv/w14e2-01v01', 'W14E2_01', 1, NULL, NULL),
            ('1970-01-01 00:00:00', 'Converter W14E2_01V02', 'W14E2_01V02', 'marpower/450000-24vdc-system/conv/w14e2-01v02', 'W14E2_01', 2, NULL, NULL),
            ('1970-01-01 00:00:00', 'Converter W14E2_01V03', 'W14E2_01V03', 'marpower/450000-24vdc-system/conv/w14e2-01v03', 'W14E2_01', 3, NULL, NULL),
            ('1970-01-01 00:00:00', 'Converter W14E2_02V01', 'W14E2_02V01', 'marpower/450000-24vdc-system/conv/w14e2-02v01', 'W14E2_02', 1, NULL, NULL),
            ('1970-01-01 00:00:00', 'Converter W14E2_02V02', 'W14E2_02V02', 'marpower/450000-24vdc-system/conv/w14e2-02v02', 'W14E2_02', 2, NULL, NULL),
            ('1970-01-01 00:00:00', 'Sea Cooling Actuator 38001153-1 & -2', '14E1_10F01', 'marpower/450000-24vdc-system/14e1-10f01', 'W14E1_01', NULL, 'Technical', 'THRS'),
            ('1970-01-01 00:00:00', 'Sea Cooling Actuator 38001153-3 & -4', '14E1_11F01', 'marpower/450000-24vdc-system/14e1-11f01', 'W14E1_01', NULL, 'Technical', 'THRS'),
            ('1970-01-01 00:00:00', 'Fwd Thruster Control Cabinet Status', '14E1_12F01', 'marpower/450000-24vdc-system/14e1-12f01', 'W14E1_01', NULL, 'Propulsion', NULL),
            ('1970-01-01 00:00:00', 'Aft Thruster Control Cabinet Status', '14E1_13F01', 'marpower/450000-24vdc-system/14e1-13f01', 'W14E1_01', NULL, 'Propulsion', NULL),
            ('1970-01-01 00:00:00', 'Stripping Pump 21001004', '14E1_20F01', 'marpower/450000-24vdc-system/14e1-20f01', 'W14E1_02', NULL, 'Technical', 'Bilge/FiFi'),
            ('1970-01-01 00:00:00', 'Chain Locker Pump', '14E1_21F01', 'marpower/450000-24vdc-system/14e1-21f01', 'W14E1_02', NULL, 'Technical', 'Bilge/FiFi'),
            ('1970-01-01 00:00:00', '10P0 Section 1 Panel Light', '14E1_22F01', 'marpower/450000-24vdc-system/14e1-22f01', 'W14E1_02', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', '10P0 Section 3 Panel Light', '14E1_23F01', 'marpower/450000-24vdc-system/14e1-23f01', 'W14E1_02', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'Passerelle', '14E1_24F01', 'marpower/450000-24vdc-system/14e1-24f01', 'W14E1_02', NULL, 'Technical', 'Other'),
            ('1970-01-01 00:00:00', 'Boarding Ladder', '14E1_25F01', 'marpower/450000-24vdc-system/14e1-25f01', 'W14E1_02', NULL, 'Technical', 'Other'),
            ('1970-01-01 00:00:00', 'SOS Panel Main Power Supply 1', '14E1_26F01', 'marpower/450000-24vdc-system/14e1-26f01', 'W14E1_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'SOS Panel Main Power Supply 2', '14E1_27F01', 'marpower/450000-24vdc-system/14e1-27f01', 'W14E1_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Navigation Lights - Main Supply', '14E1_28F01', 'marpower/450000-24vdc-system/14e1-28f01', 'W14E1_02', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'Cabinet Sliding Window Owner Private Salon', '14E1_29F01', 'marpower/450000-24vdc-system/14e1-29f01', 'W14E1_02', NULL, 'Domestic', 'Guest area'),
            ('1970-01-01 00:00:00', 'Spare - Main Supply', '14E1_30F01', 'marpower/450000-24vdc-system/14e1-30f01', 'W14E1_02', NULL, 'Technical', 'Technical'),
            ('1970-01-01 00:00:00', 'Bed Gimball', '14E1_31F01', 'marpower/450000-24vdc-system/14e1-31f01', 'W14E1_02', NULL, 'Domestic', 'Guest area'),
            ('1970-01-01 00:00:00', 'WT DOOR CREW MESS ENTRY', '14E1_32F01', 'marpower/450000-24vdc-system/14e1-32f01', 'W14E1_02', NULL, 'Domestic', 'Crew'),
            ('1970-01-01 00:00:00', 'A&T ATP2 Iinstruments (Navcom)', '14E1_33F01', 'marpower/450000-24vdc-system/14e1-33f01', 'W14E1_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Lights Technical Area - 901JB102', '14E1_80F01', 'marpower/450000-24vdc-system/14e1-80f01', 'W14E1_02', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'Lights Technical Area - 901JB103', '14E1_81F01', 'marpower/450000-24vdc-system/14e1-81f01', 'W14E1_02', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'SOS PANEL MAIN POWER SUPPLY 3', '14E1_82F01', 'marpower/450000-24vdc-system/14e1-82f01', 'W14E1_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Hatches Nr33/34/44', '14E1_83F01', 'marpower/450000-24vdc-system/14e1-83f01', 'W14E1_02', NULL, 'Technical', 'Other'),
            ('1970-01-01 00:00:00', 'Gyrocompass', '14E1_84F01', 'marpower/450000-24vdc-system/14e1-84f01', 'W14E1_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Technical Water Salinity Sensor', '14E1_85F01', 'marpower/450000-24vdc-system/14e1-85f01', 'W14E1_02', NULL, 'Technical', 'Technical water'),
            ('1970-01-01 00:00:00', 'Foldable Windows Main Cockpit', '14E1_86F01', 'marpower/450000-24vdc-system/14e1-86f01', 'W14E1_02', NULL, 'Technical', 'Other'),
            ('1970-01-01 00:00:00', 'Foldable Windows Private Salon', '14E1_87F01', 'marpower/450000-24vdc-system/14e1-87f01', 'W14E1_02', NULL, 'Technical', 'Other'),
            ('1970-01-01 00:00:00', 'Sunbed PS', '14E1_88F01', 'marpower/450000-24vdc-system/14e1-88f01', 'W14E1_02', NULL, 'Domestic', 'Guest area'),
            ('1970-01-01 00:00:00', 'Sunbed SB', '14E1_89F01', 'marpower/450000-24vdc-system/14e1-89f01', 'W14E1_02', NULL, 'Domestic', 'Guest area'),
            ('1970-01-01 00:00:00', 'Fire Door Galley', '14E2_11F01', 'marpower/450000-24vdc-system/14e2-11f01', 'W14E2_02', NULL, 'Technical', 'Bilge/FiFi'),
            ('1970-01-01 00:00:00', 'Fire Detection Panel', '14E2_12F01', 'marpower/450000-24vdc-system/14e2-12f01', 'W14E2_02', NULL, 'Technical', 'Bilge/FiFi'),
            ('1970-01-01 00:00:00', 'Fire Dampers PS & SB', '14E2_14F01', 'marpower/450000-24vdc-system/14e2-14f01', 'W14E2_02', NULL, 'Technical', 'Bilge/FiFi'),
            ('1970-01-01 00:00:00', 'Bilge LVL Petrol Locker', '14E2_16F01', 'marpower/450000-24vdc-system/14e2-16f01', 'W14E2_02', NULL, 'Technical', 'Bilge/FiFi'),
            ('1970-01-01 00:00:00', 'SOS Panel Back-up PSU 3 Hull Valves', '14E2_18F01', 'marpower/450000-24vdc-system/14e2-18f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Signal Panel System', '14E2_21F01', 'marpower/450000-24vdc-system/14e2-21f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Talk Back System', '14E2_22F01', 'marpower/450000-24vdc-system/14e2-22f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'WT Door Crew Corridor', '14E2_24F01', 'marpower/450000-24vdc-system/14e2-24f01', 'W14E2_02', NULL, 'Technical', 'Other'),
            ('1970-01-01 00:00:00', 'SOS Panel Back-UP Power Supply 1', '14E2_25F01', 'marpower/450000-24vdc-system/14e2-25f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'SOS Panel Back-UP Power Supply 2', '14E2_25F02', 'marpower/450000-24vdc-system/14e2-25f02', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Navigation Lights - EM Supply', '14E2_26F01', 'marpower/450000-24vdc-system/14e2-26f01', 'W14E2_01', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'GALLEY FIRE DAMPER', '14E2_33F01', 'marpower/450000-24vdc-system/14e2-33f01', 'W14E2_02', NULL, 'HVAC', 'Other'),
            ('1970-01-01 00:00:00', 'OXYCELL FIRE DAMPER', '14E2_34F01', 'marpower/450000-24vdc-system/14e2-34f01', 'W14E2_02', NULL, 'HVAC', 'Other'),
            ('1970-01-01 00:00:00', 'Helm Console SB', '14E2_42F23', 'marpower/450000-24vdc-system/14e2-42f23', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Helm Console SB', '14E2_24F24', 'marpower/450000-24vdc-system/14e2-24f24', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Navtex', '14E2_68F01', 'marpower/450000-24vdc-system/14e2-68f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'RAI', '14E2_69F01', 'marpower/450000-24vdc-system/14e2-69f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Deck Crane (MOB)', '14E2_70F01', 'marpower/450000-24vdc-system/14e2-70f01', 'W14E2_02', NULL, 'Technical', 'Other'),
            ('1970-01-01 00:00:00', 'Valve For Battery Comp. Fan PS/SB Aft/Fwd', '14E2_71F01', 'marpower/450000-24vdc-system/14e2-71f01', 'W14E2_02', NULL, 'Technical', 'Technical'),
            ('1970-01-01 00:00:00', 'Electric Horn (Air Whistle)', '14E2_73F01', 'marpower/450000-24vdc-system/14e2-73f01', 'W14E2_02', NULL, 'Technical', 'Technical'),
            ('1970-01-01 00:00:00', 'Iridium', '14E2_74F01', 'marpower/450000-24vdc-system/14e2-74f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Bnwas', '14E2_75F01', 'marpower/450000-24vdc-system/14e2-75f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'VHF 2', '14E2_76F01', 'marpower/450000-24vdc-system/14e2-76f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Fleetbroad Band', '14E2_77F01', 'marpower/450000-24vdc-system/14e2-77f01', 'W14E2_02', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Butterfly Control', '14E2_78F01', 'marpower/450000-24vdc-system/14e2-78f01', 'W14E2_02', NULL, 'HVAC', 'Ventilation'),
            ('1970-01-01 00:00:00', 'Butterfly Control', '14E2_79F01', 'marpower/450000-24vdc-system/14e2-79f01', 'W14E2_02', NULL, 'HVAC', 'Ventilation'),
            ('1970-01-01 00:00:00', 'VHF 1', '14E3_10F01', 'marpower/450000-24vdc-system/14e3-10f01', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'MF/HF SSB', '14E3_12F01', 'marpower/450000-24vdc-system/14e3-12f01', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Dgps', '14E3_13F01', 'marpower/450000-24vdc-system/14e3-13f01', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Iridium', '14E3_14F01', 'marpower/450000-24vdc-system/14e3-14f01', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Chart Red Light', '14E3_15F01', 'marpower/450000-24vdc-system/14e3-15f01', 'W14E2_01', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'EM LIGHTS TECHNICAL AREA - 903JB103', '14E2_41F01', 'marpower/450000-24vdc-system/14e2-41f01', 'W14E2_01', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'EM LIGHTS TECHNICAL AREA 903JB102', '14E2_42F01', 'marpower/450000-24vdc-system/14e2-42f01', 'W14E2_01', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'EM LIGHTS AFT SHIP', '14E2_45F01', 'marpower/450000-24vdc-system/14e2-45f01', 'W14E2_01', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'EM LIGHTS FWD SHIP', '14E2_46F01', 'marpower/450000-24vdc-system/14e2-46f01', 'W14E2_01', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'EM LIGHTS OUTSIDE AFT/FWD', '14E2_47F01', 'marpower/450000-24vdc-system/14e2-47f01', 'W14E2_01', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'STEERING SYSTEM CONTROL - EM SUPPLY', '14E2_27F01', 'marpower/450000-24vdc-system/14e2-27f01', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'AIS', '14E2_60F01', 'marpower/450000-24vdc-system/14e2-60f01', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'AutoPilot', '14E2_61F01', 'marpower/450000-24vdc-system/14e2-61f01', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'Gyro Compass', '14E2_63F01', 'marpower/450000-24vdc-system/14e2-63f01', 'W14E2_01', NULL, 'Technical', 'NavComm'),
            ('1970-01-01 00:00:00', 'PCS 1 AFT', '14E2_80F01', 'marpower/450000-24vdc-system/14e2-80f01', 'W14E2_02', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'PCS 1 AFT', '14E2_81F01', 'marpower/450000-24vdc-system/14e2-81f01', 'W14E2_02', NULL, 'Technical', 'Lighting'),
            ('1970-01-01 00:00:00', 'Solar 1', '14E2_82F01', 'marpower/450000-24vdc-system/14e2-82f01', 'W14E2_02', NULL, 'Technical', 'Technical'),
            ('1970-01-01 00:00:00', 'Solar 2', '14E2_83F01', 'marpower/450000-24vdc-system/14e2-83f01', 'W14E2_02', NULL, 'Technical', 'Technical'),
            ('1970-01-01 00:00:00', 'HELM CONSOLE PS', '14E2_42F24', 'marpower/450000-24vdc-system/14e2-42f24', 'W14E2_01', NULL, 'Technical', 'NavComm');
    {% endset %}

    {% do log("Create 24V DC metadata table and insert data...", info=True) %}
    {% do run_query(query) %}
    {% do log("Success! Data has been loaded.", info=True) %}

{% endmacro %}
