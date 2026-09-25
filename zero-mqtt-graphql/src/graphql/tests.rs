use super::*;
use crate::asyncapi::FieldDef;
use crate::http::router;
use crate::model::views::{MemberDef, ObjectSection, SwitchSection};
use axum::http::StatusCode;
use serde_json::json;
use tower::ServiceExt;

// Per-module fixture shapes, converted into the view/member/section
// model by `schema_views`.
#[derive(Default, Clone)]
struct ModuleView {
    module: String,
    modules_type_name: String,
    type_name: String,
    sensor_values_type_name: String,
    sensor_values: Vec<StampedFieldDef>,
    control_values: Option<ObjectSectionDef>,
    parameters: Option<ObjectSectionDef>,
    controller_state: Option<ObjectSectionDef>,
    control_mode: Option<ControlModeDef>,
}

#[derive(Default, Clone)]
struct ControlModeDef {
    topic: String,
    operation: Option<crate::extension::OperationRef>,
    type_name: String,
    key: String,
    automatic_mode: PlainObjectDef,
}

fn member_of(v: &ModuleView) -> MemberDef {
    let mut sections = vec![SectionDef::StampedFields(StampedFieldsSection {
        gql: "sensorValues".into(),
        type_name: v.sensor_values_type_name.clone(),
        fields: v.sensor_values.clone(),
    })];
    for (name, section) in [
        ("controlValues", &v.control_values),
        ("parameters", &v.parameters),
        ("controllerState", &v.controller_state),
    ] {
        if let Some(section) = section {
            sections.push(SectionDef::Object(ObjectSection {
                gql: name.into(),
                section: section.clone(),
            }));
        }
    }
    if let Some(cm) = &v.control_mode {
        sections.push(SectionDef::Switch(SwitchSection {
            gql: "controlMode".into(),
            section: SwitchSectionDef {
                operation: cm.operation.clone(),
                topic: cm.topic.clone(),
                type_name: cm.type_name.clone(),
                key: cm.key.clone(),
                flag_field: "automatic".into(),
                object_field: "automaticMode".into(),
                object: cm.automatic_mode.clone(),
            },
        }));
    }
    MemberDef {
        gql: v.module.clone(),
        type_name: v.type_name.clone(),
        sections,
        mutations: Vec::new(),
    }
}

/// The `modules` view of the fixtures: each mutation group joins the
/// member of its module (created from the group's objects when no view
/// fixture declares it) and returns the section matching its kind.
fn schema_views(views: &[ModuleView], groups: &[ModuleMutations]) -> Vec<ViewDef> {
    let mut members: Vec<MemberDef> = views.iter().map(member_of).collect();
    let type_name = views
        .first()
        .map(|v| v.modules_type_name.clone())
        .unwrap_or_else(|| "ControlModules".into());
    for g in groups {
        let position = members.iter().position(|m| m.gql == g.module);
        let member = match position {
            Some(i) => &mut members[i],
            None => {
                members.push(MemberDef {
                    gql: g.module.clone(),
                    type_name: format!("{}ControlModule", g.module),
                    sections: Vec::new(),
                    mutations: Vec::new(),
                });
                members.last_mut().unwrap()
            }
        };
        for (name, section) in [
            ("parameters", &g.parameters_object),
            ("controlValues", &g.control_values_object),
        ] {
            if member.object_section(name).is_none() {
                member.sections.push(SectionDef::Object(ObjectSection {
                    gql: name.into(),
                    section: section.clone(),
                }));
            }
        }
        member
            .mutations
            .extend(g.mutations.iter().map(|m| MutationDef {
                returns: match m.kind {
                    MutationKind::SetField => Some("parameters".into()),
                    MutationKind::SetComponent => Some("controlValues".into()),
                    MutationKind::SetFlag => None,
                },
                ..m.clone()
            }));
    }
    if members.is_empty() {
        return Vec::new();
    }
    vec![ViewDef {
        gql: "modules".into(),
        type_name,
        members,
    }]
}

#[derive(Default, Clone)]
struct ModuleMutations {
    module: String,
    mutations: Vec<MutationDef>,
    parameters_object: ObjectSectionDef,
    control_values_object: ObjectSectionDef,
}

#[test]
fn test_build_schema_for_one_topic() {
    let topics = vec![TopicDef {
        topic: "test/channel".to_string(),
        fields: vec![
            FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            },
            FieldDef {
                name: "ok".to_string(),
                graphql_type: "Boolean".to_string(),
            },
        ],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let cache = Arc::new(TopicCache::new());
    let _schema = build_schema(
        cache,
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();
    // Schema builds without panicking
}

#[test]
fn test_colliding_sanitized_topics_error() {
    // "a/b" and "a-b" both sanitize to "a_b" — should error rather than suffix
    let topics = vec![
        TopicDef {
            topic: "a/b".to_string(),
            fields: vec![FieldDef {
                name: "x".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        },
        TopicDef {
            topic: "a-b".to_string(),
            fields: vec![FieldDef {
                name: "y".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        },
    ];

    let err = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap_err();
    assert!(
        err.to_string().contains("duplicate sanitized topic name"),
        "{err}"
    );
}

#[test]
fn test_reserved_topic_name_errors() {
    let topics = vec![TopicDef {
        topic: "Query".to_string(),
        fields: vec![FieldDef {
            name: "x".to_string(),
            graphql_type: "Float".to_string(),
        }],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let err = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap_err();
    assert!(err.to_string().contains("reserved"), "{err}");
}

#[test]
fn test_digit_prefixed_topic_is_valid() {
    let topics = vec![TopicDef {
        topic: "123/topic".to_string(),
        fields: vec![FieldDef {
            name: "x".to_string(),
            graphql_type: "Float".to_string(),
        }],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();
    let sdl = schema.sdl();
    assert!(sdl.contains("_123Topic"), "{sdl}");
}

#[test]
fn test_empty_topic_is_listed_but_not_queryable() {
    // A topic without scalar fields must not crash schema building;
    // it stays visible via `topics` but has no query type.
    let topics = vec![TopicDef {
        topic: "empty/topic".to_string(),
        fields: vec![],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();
    let sdl = schema.sdl();
    assert!(!sdl.contains("emptyTopic"), "{sdl}");
}

#[test]
fn test_field_types_in_schema() {
    let topics = vec![TopicDef {
        topic: "t".to_string(),
        fields: vec![
            FieldDef {
                name: "f_float".to_string(),
                graphql_type: "Float".to_string(),
            },
            FieldDef {
                name: "f_int".to_string(),
                graphql_type: "Int".to_string(),
            },
            FieldDef {
                name: "f_bool".to_string(),
                graphql_type: "Boolean".to_string(),
            },
            FieldDef {
                name: "f_str".to_string(),
                graphql_type: "String".to_string(),
            },
            FieldDef {
                name: "f_unknown".to_string(),
                graphql_type: "DateTime".to_string(),
            },
        ],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();
    let sdl = schema.sdl();
    assert!(sdl.contains("fFloat: Float"), "{sdl}");
    assert!(sdl.contains("fInt: Int"), "{sdl}");
    assert!(sdl.contains("fBool: Boolean"), "{sdl}");
    assert!(sdl.contains("fStr: String"), "{sdl}");
    // Unknown types fall back to String
    assert!(sdl.contains("fUnknown: String"), "{sdl}");
}

#[tokio::test]
async fn test_query_returns_cached_values() {
    let topics = vec![TopicDef {
        topic: "test/channel".to_string(),
        fields: vec![
            FieldDef {
                name: "value".to_string(),
                graphql_type: "Float".to_string(),
            },
            FieldDef {
                name: "ok".to_string(),
                graphql_type: "Boolean".to_string(),
            },
            FieldDef {
                name: "label".to_string(),
                graphql_type: "String".to_string(),
            },
        ],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "test/channel",
        json!({"value": 23.5, "ok": true, "label": "hello"}),
    );
    let schema = build_schema(
        cache,
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema.execute("{ testChannel { value ok label } }").await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["testChannel"]["value"], json!(23.5));
    assert_eq!(data["testChannel"]["ok"], json!(true));
    assert_eq!(data["testChannel"]["label"], json!("hello"));
}

fn thrusters_module_view() -> Vec<ModuleView> {
    vec![ModuleView {
        module: "thrusters".to_string(),
        modules_type_name: "ControlModules".into(),
        type_name: "ThrustersControlModule".into(),
        sensor_values_type_name: "ThrustersSensorValuesType".into(),
        control_mode: None,
        control_values: None,
        parameters: None,
        controller_state: None,
        sensor_values: vec![StampedFieldDef {
            gql: "thrustersFlowcontrolAft".to_string(),
            type_name: "thrustersFlowcontrolAftType".into(),
            topic: "simulation/500000-thrs/thrusters/thrusters-flowcontrol-aft".to_string(),
            operation: None,
            leaves: vec![
                LeafDef {
                    gql: "positionRel".to_string(),
                    key: "PositionRel".to_string(),
                    r#type: "Float".to_string(),
                    enum_values: None,
                    enum_type: None,
                    optional: false,
                    actuated_key: None,
                    default: None,
                },
                LeafDef {
                    gql: "positionAbs".to_string(),
                    key: "PositionAbs".to_string(),
                    r#type: "Float".to_string(),
                    enum_values: None,
                    enum_type: None,
                    optional: false,
                    actuated_key: None,
                    default: None,
                },
            ],
            computed: false,
        }],
    }]
}

#[tokio::test]
async fn test_nested_module_view_returns_camelcase_leaves() {
    // Leaf names must be thrs-api's camelCase (positionRel), not the flat
    // schema's lowercased positionrel, and value/timestamp come from the
    // cached PascalCase payload.
    let topic = "simulation/500000-thrs/thrusters/thrusters-flowcontrol-aft";
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        topic,
        json!({
            "PositionRel": {"Value": 0.75, "TimeStamp": "2024-01-01T00:00:00Z"},
            "PositionAbs": {"Value": 270.0, "TimeStamp": "2024-01-01T00:00:00Z"}
        }),
    );
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&thrusters_module_view(), &[]),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute(
            "{ modules { thrusters { sensorValues { thrustersFlowcontrolAft { \
             positionRel { value timestamp } positionAbs { value } } } } } }",
        )
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    let field = &data["modules"]["thrusters"]["sensorValues"]["thrustersFlowcontrolAft"];
    assert_eq!(field["positionRel"]["value"], json!(0.75));
    // The wire timestamp is served as-is (RFC 3339, no re-rendering).
    assert_eq!(
        field["positionRel"]["timestamp"],
        json!("2024-01-01T00:00:00Z")
    );
    assert_eq!(field["positionAbs"]["value"], json!(270.0));
}

#[tokio::test]
async fn test_nested_module_view_null_when_uncached() {
    // A field with no cached payload resolves to null (not an error).
    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            views: &schema_views(&thrusters_module_view(), &[]),
            ..Default::default()
        },
    )
    .unwrap();
    let response = schema
        .execute(
            "{ modules { thrusters { sensorValues { thrustersFlowcontrolAft { \
             positionRel { value } } } } } }",
        )
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(
        data["modules"]["thrusters"]["sensorValues"]["thrustersFlowcontrolAft"],
        json!(null)
    );
}

#[tokio::test]
async fn test_nested_module_view_dedupes_colliding_gql_field() {
    // Two distinct snake_case model fields can collapse to the same
    // camelCase name (pvt_flow_main_string1_2 / pvt_flow_main_string12 ->
    // pvtFlowMainString12). The schema must still build (async-graphql
    // panics on a duplicate field) by keeping the first and skipping the
    // rest, so one ambiguous field never crashes the service.
    let first_topic = "simulation/500000-thrs/pvt/pvt-flow-main-string1-2";
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        first_topic,
        json!({"Flow": {"Value": 1.5, "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    let leaf = || {
        vec![LeafDef {
            gql: "flow".to_string(),
            key: "Flow".to_string(),
            r#type: "Float".to_string(),
            enum_values: None,
            enum_type: None,
            optional: false,
            actuated_key: None,
            default: None,
        }]
    };
    let views = vec![ModuleView {
        module: "pvt".to_string(),
        modules_type_name: "ControlModules".into(),
        type_name: "PvtControlModule".into(),
        sensor_values_type_name: "PvtSensorValuesType".into(),
        control_mode: None,
        control_values: None,
        parameters: None,
        controller_state: None,
        sensor_values: vec![
            StampedFieldDef {
                gql: "pvtFlowMainString12".to_string(),
                type_name: "pvtFlowMainString12Type".into(),
                topic: first_topic.to_string(),
                operation: None,
                leaves: leaf(),
                computed: false,
            },
            StampedFieldDef {
                gql: "pvtFlowMainString12".to_string(),
                type_name: "pvtFlowMainString12Type".into(),
                topic: "simulation/500000-thrs/pvt/pvt-flow-main-string12".to_string(),
                operation: None,
                leaves: leaf(),
                computed: false,
            },
        ],
    }];
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&views, &[]),
            ..Default::default()
        },
    )
    .unwrap();
    let response = schema
        .execute("{ modules { pvt { sensorValues { pvtFlowMainString12 { flow { value } } } } } }")
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    // The kept (first) field resolves from its own topic's cached payload.
    assert_eq!(
        data["modules"]["pvt"]["sensorValues"]["pvtFlowMainString12"]["flow"]["value"],
        json!(1.5)
    );
}

#[tokio::test]
async fn test_object_section_parameters_flat_and_empty_controller_state() {
    // parameters is one whole-object topic: flat scalar + list fields are
    // pulled out of the cached object by their PascalCase keys. An empty
    // controllerState (no fields) must still form a valid, null-resolving
    // section (thrs-api's `_empty` placeholder).
    let params_topic = "thrs/controller/thrusters/parameters";
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        params_topic,
        json!({"CoolingFlow": 25.0, "PumpTuning": [0.01, 0.001, 0.0]}),
    );
    let views = vec![ModuleView {
        module: "thrusters".to_string(),
        modules_type_name: "ControlModules".into(),
        type_name: "ThrustersControlModule".into(),
        sensor_values_type_name: "ThrustersSensorValuesType".into(),
        control_mode: None,
        parameters: Some(ObjectSectionDef {
            topic: params_topic.to_string(),
            operation: None,
            type_name: "ThrustersParametersType".into(),
            fields: vec![
                ObjectFieldDef {
                    gql: "coolingFlow".to_string(),
                    key: "CoolingFlow".to_string(),
                    topic: None,
                    operation: None,
                    type_name: None,
                    optional: false,
                    r#type: Some("Float".to_string()),
                    leaves: vec![],
                },
                ObjectFieldDef {
                    gql: "pumpTuning".to_string(),
                    key: "PumpTuning".to_string(),
                    topic: None,
                    operation: None,
                    type_name: None,
                    optional: false,
                    r#type: Some("[Float!]".to_string()),
                    leaves: vec![],
                },
            ],
        }),
        controller_state: Some(ObjectSectionDef {
            topic: "thrs/controller/thrusters/controller-state".to_string(),
            operation: None,
            type_name: "ThrustersControllerStateType".into(),
            fields: vec![],
        }),
        // Every real module has sensor fields; one keeps the SensorValues
        // object non-empty (an empty GraphQL object is invalid).
        sensor_values: vec![StampedFieldDef {
            gql: "thrustersFlowAft".to_string(),
            type_name: "thrustersFlowAftType".into(),
            topic: "simulation/500000-thrs/thrusters/thrusters-flow-aft".to_string(),
            operation: None,
            leaves: vec![LeafDef {
                gql: "flow".to_string(),
                key: "Flow".to_string(),
                r#type: "Float".to_string(),
                enum_values: None,
                enum_type: None,
                optional: false,
                actuated_key: None,
                default: None,
            }],
            computed: false,
        }],
        ..Default::default()
    }];
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&views, &[]),
            ..Default::default()
        },
    )
    .unwrap();
    let response = schema
        .execute(
            "{ modules { thrusters { \
             parameters { coolingFlow pumpTuning } \
             controllerState { Empty } } } }",
        )
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    let params = &data["modules"]["thrusters"]["parameters"];
    assert_eq!(params["coolingFlow"], json!(25.0));
    assert_eq!(params["pumpTuning"], json!([0.01, 0.001, 0.0]));
    // No controller-state object cached -> the whole section resolves null,
    // exactly like thrs-api returning null for an unpublished section.
    assert_eq!(data["modules"]["thrusters"]["controllerState"], json!(null));
}

#[tokio::test]
async fn test_nested_module_view_maps_enum_leaf_to_member_name() {
    // An enum leaf (type String + enumValues) must resolve `value` to the
    // thrs-api member name, not the raw wire value: int 0 -> "LOCAL",
    // str "off" -> "OFF". Unmapped values pass through untouched.
    let mode_topic = "simulation/500000-thrs/thrusters/mode";
    let pcs_topic = "simulation/500000-thrs/thrusters/pcs-mode";
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        mode_topic,
        json!({"Mode": {"Value": 0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    cache.insert(
        pcs_topic,
        json!({"Mode": {"Value": "off", "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    let enum_leaf = |enum_type: &str, raw_to_name: &[(&str, &str)]| LeafDef {
        gql: "mode".to_string(),
        key: "Mode".to_string(),
        r#type: "String".to_string(),
        enum_values: Some(
            raw_to_name
                .iter()
                .map(|(k, v)| (k.to_string(), v.to_string()))
                .collect(),
        ),
        enum_type: Some(enum_type.to_string()),
        optional: false,
        actuated_key: None,
        default: None,
    };
    let views = vec![ModuleView {
        module: "thrusters".to_string(),
        modules_type_name: "ControlModules".into(),
        type_name: "ThrustersControlModule".into(),
        sensor_values_type_name: "ThrustersSensorValuesType".into(),
        control_mode: None,
        control_values: None,
        parameters: None,
        controller_state: None,
        sensor_values: vec![
            StampedFieldDef {
                gql: "mode".to_string(),
                type_name: "modeType".into(),
                topic: mode_topic.to_string(),
                operation: None,
                leaves: vec![enum_leaf("ControlMode", &[("0", "LOCAL"), ("1", "MANUAL")])],
                computed: false,
            },
            StampedFieldDef {
                gql: "thrustersPcs".to_string(),
                type_name: "thrustersPcsType".into(),
                topic: pcs_topic.to_string(),
                operation: None,
                leaves: vec![enum_leaf("PcsMode", &[("off", "OFF"), ("on", "ON")])],
                computed: false,
            },
        ],
    }];
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&views, &[]),
            ..Default::default()
        },
    )
    .unwrap();
    let response = schema
        .execute(
            "{ modules { thrusters { sensorValues { \
             mode { mode { value timestamp } } \
             thrustersPcs { mode { value } } } } } }",
        )
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    let sv = &data["modules"]["thrusters"]["sensorValues"];
    assert_eq!(sv["mode"]["mode"]["value"], json!("LOCAL"));
    assert_eq!(
        sv["mode"]["mode"]["timestamp"],
        json!("2024-01-01T00:00:00Z")
    );
    assert_eq!(sv["thrustersPcs"]["mode"]["value"], json!("OFF"));
}

struct CapturingPublisher {
    sent: Arc<std::sync::Mutex<Vec<(String, String)>>>,
}

impl TopicPublisher for CapturingPublisher {
    fn publish(&self, topic: String, payload: String) -> PublishFuture {
        let sent = self.sent.clone();
        Box::pin(async move {
            sent.lock().unwrap().push((topic, payload));
            Ok(())
        })
    }
}

fn cooling_flow_mutation() -> Vec<ModuleMutations> {
    vec![ModuleMutations {
        module: "thrusters".to_string(),
        mutations: vec![MutationDef {
            derived: Vec::new(),
            gql: "thrustersParameterSetCoolingFlow".to_string(),
            kind: MutationKind::SetField,
            arg_type: "Float".to_string(),
            arg_name: "value".to_string(),
            key: "CoolingFlow".to_string(),
            state_topic: "thrs/controller/thrusters/parameters".to_string(),
            set_topic: "thrs/controller/thrusters/parameters/set".to_string(),
            state: None,
            target: None,
            returns: None,
            true_value: None,
            false_value: None,
            input_fields: Vec::new(),
            input_type_name: None,
            missing_error: Some("No parameters available to update".to_string()),
            confirm: None,
            model: None,
        }],
        parameters_object: Default::default(),
        control_values_object: Default::default(),
    }]
}

fn automation_mode_mutation() -> Vec<ModuleMutations> {
    let mut groups = cooling_flow_mutation();
    let def = &mut groups[0].mutations[0];
    def.gql = "thrustersSetAutomationMode".to_string();
    def.kind = MutationKind::SetFlag;
    def.arg_type = "Boolean".to_string();
    def.arg_name = "automatic".to_string();
    def.key = "Mode".to_string();
    def.state_topic = String::new();
    def.set_topic = "thrs/controller/thrusters/automation-mode/set".to_string();
    def.true_value = Some("automatic".to_string());
    def.false_value = Some("manual".to_string());
    def.missing_error = None;
    groups
}

#[tokio::test]
async fn test_mutation_reads_cache_modifies_and_publishes() {
    // A parameter mutation overwrites one field of the cached object and
    // publishes the whole object to the set topic; other fields untouched.
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "thrs/controller/thrusters/parameters",
        json!({"CoolingFlow": 25.0, "WarmupTemperature": 60.0}),
    );
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(CapturingPublisher { sent: sent.clone() });

    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&[], &cooling_flow_mutation()),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute("mutation { thrustersParameterSetCoolingFlow(value: 12.34) }")
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["thrustersParameterSetCoolingFlow"], json!(true));

    let sent = sent.lock().unwrap();
    assert_eq!(sent.len(), 1, "expected exactly one publish");
    assert_eq!(sent[0].0, "thrs/controller/thrusters/parameters/set");
    let published: serde_json::Value = serde_json::from_str(&sent[0].1).unwrap();
    assert_eq!(published["CoolingFlow"], json!(12.34), "field set to arg");
    assert_eq!(
        published["WarmupTemperature"],
        json!(60.0),
        "other fields preserved"
    );
}

/// A publisher that echoes every publish back into the cache at the
/// state topic, as a control loop that accepts the object would.
struct EchoingPublisher {
    cache: Arc<TopicCache>,
    state_topic: String,
    sent: Arc<std::sync::Mutex<Vec<(String, String)>>>,
}

impl TopicPublisher for EchoingPublisher {
    fn publish(&self, topic: String, payload: String) -> PublishFuture {
        let cache = self.cache.clone();
        let state_topic = self.state_topic.clone();
        let sent = self.sent.clone();
        Box::pin(async move {
            sent.lock().unwrap().push((topic, payload.clone()));
            let echoed: serde_json::Value = serde_json::from_str(&payload).unwrap();
            tokio::spawn(async move {
                tokio::time::sleep(std::time::Duration::from_millis(60)).await;
                cache.insert(&state_topic, echoed);
            });
            Ok(())
        })
    }
}

fn confirmed(mut groups: Vec<ModuleMutations>, timeout_s: f64) -> Vec<ModuleMutations> {
    for def in groups.iter_mut().flat_map(|g| g.mutations.iter_mut()) {
        def.confirm = Some(ConfirmDef {
            operation: None,
            topic: def.state_topic.clone(),
            key: None,
            presence: false,
            timeout_s,
            timeout_error: "Timeout when setting parameters".to_string(),
        });
    }
    groups
}

#[tokio::test]
async fn test_confirmed_mutation_returns_once_the_state_echoes_the_change() {
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "thrs/controller/thrusters/parameters",
        json!({"CoolingFlow": 25.0, "WarmupTemperature": 60.0}),
    );
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(EchoingPublisher {
        cache: cache.clone(),
        state_topic: "thrs/controller/thrusters/parameters".to_string(),
        sent: sent.clone(),
    });
    let schema = build_schema(
        cache.clone(),
        SchemaInputs {
            views: &schema_views(&[], &confirmed(cooling_flow_mutation(), 2.0)),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute("mutation { thrustersParameterSetCoolingFlow(value: 12) }")
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    // The echo carries the same value as the publish (`12` vs `12.0` is one
    // wire value), and the cache holds it by the time the mutation returns.
    assert_eq!(
        cache.get_field("thrs/controller/thrusters/parameters", "CoolingFlow"),
        Some(json!(12.0))
    );
    assert_eq!(sent.lock().unwrap().len(), 1);
}

#[tokio::test]
async fn test_confirmed_mutation_times_out_without_an_echo() {
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "thrs/controller/thrusters/parameters",
        json!({"CoolingFlow": 25.0}),
    );
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(CapturingPublisher { sent: sent.clone() });
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&[], &confirmed(cooling_flow_mutation(), 0.15)),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute("mutation { thrustersParameterSetCoolingFlow(value: 12.34) }")
        .await;
    assert_eq!(response.errors.len(), 1, "{:?}", response.errors);
    assert_eq!(
        response.errors[0].message,
        "Timeout when setting parameters"
    );
    assert_eq!(sent.lock().unwrap().len(), 1, "published, then timed out");
}

#[tokio::test]
async fn test_flag_mutation_is_confirmed_by_the_presence_of_the_switched_object() {
    let cache = Arc::new(TopicCache::new());
    let control_mode = "thrs/controller/thrusters/control-mode";
    cache.insert(control_mode, json!({"AutomaticMode": null}));
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(EchoingPublisher {
        cache: cache.clone(),
        state_topic: "thrs/controller/thrusters/automation-mode".to_string(),
        sent: sent.clone(),
    });
    let mut groups = automation_mode_mutation();
    groups[0].mutations[0].confirm = Some(ConfirmDef {
        operation: None,
        topic: control_mode.to_string(),
        key: Some("AutomaticMode".to_string()),
        presence: true,
        timeout_s: 0.15,
        timeout_error: "Timeout when setting automation mode".to_string(),
    });
    let schema = build_schema(
        cache.clone(),
        SchemaInputs {
            views: &schema_views(&[], &groups),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();

    // Off: the switched object is already null, confirmed at once.
    let response = schema
        .execute("mutation { thrustersSetAutomationMode(automatic: false) }")
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    // On: nothing turns the mode on, so the switch never confirms.
    let response = schema
        .execute("mutation { thrustersSetAutomationMode(automatic: true) }")
        .await;
    assert_eq!(response.errors.len(), 1, "{:?}", response.errors);
    assert_eq!(
        response.errors[0].message,
        "Timeout when setting automation mode"
    );
    assert_eq!(sent.lock().unwrap().len(), 2);
}

#[tokio::test]
async fn test_invariant_violation_errors_and_publishes_nothing() {
    use crate::model_validation::ModelSchema;
    use crate::schema::Components;
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "thrs/controller/thrusters/parameters",
        json!({"CoolingFlow": 25.0, "WarmupTemperature": 60.0, "CoolingTemperature": 40.0}),
    );
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(CapturingPublisher { sent: sent.clone() });
    let mut groups = cooling_flow_mutation();
    let def = &mut groups[0].mutations[0];
    def.key = "WarmupTemperature".to_string();
    // Warmup must stay above cooling; setting it to 30 breaks that.
    let components = json!({"schemas": {"Parameters": {
        "title": "ThrustersParameters", "type": "object",
        "properties": {
            "CoolingFlow": {"type": "number", "x-python-name": "cooling_flow"},
            "WarmupTemperature": {"type": "number", "x-python-name": "warmup_temperature"},
            "CoolingTemperature": {"type": "number", "x-python-name": "cooling_temperature"}},
        "x-invariants": [{"lhs": "WarmupTemperature", "op": "ge", "rhs": "CoolingTemperature",
            "error": "Warmup temperature must be greater than cooling temperature"}]}}});
    def.model = Some(
        ModelSchema::read(
            &json!({"$ref": "#/components/schemas/Parameters"}),
            Components::new(Some(&components)),
        )
        .unwrap()
        .with_error_url("https://errors.pydantic.dev/2.13/v/"),
    );
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&[], &groups),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute("mutation { thrustersParameterSetCoolingFlow(value: 30) }")
        .await;
    assert_eq!(response.errors.len(), 1, "{:?}", response.errors);
    assert!(
        response.errors[0].message.contains(
            "Value error, Warmup temperature must be greater than cooling temperature [type=value_error"
        ),
        "{}",
        response.errors[0].message
    );
    assert!(
        sent.lock().unwrap().is_empty(),
        "nothing should be published"
    );

    let response = schema
        .execute("mutation { thrustersParameterSetCoolingFlow(value: 45) }")
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    assert_eq!(sent.lock().unwrap().len(), 1);
}

#[tokio::test]
async fn test_mutation_errors_and_publishes_nothing_when_state_uncached() {
    // With no cached parameters object, the mutation errors (like thrs-api's
    // "No parameters available to update") and publishes nothing.
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(CapturingPublisher { sent: sent.clone() });
    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            views: &schema_views(&[], &cooling_flow_mutation()),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute("mutation { thrustersParameterSetCoolingFlow(value: 12.34) }")
        .await;
    assert!(!response.errors.is_empty(), "expected an error");
    assert!(
        sent.lock().unwrap().is_empty(),
        "nothing should be published"
    );
}

#[tokio::test]
async fn test_control_mutation_restamps_component_and_publishes() {
    use crate::model::mutations::InputFieldDef;
    let cache = Arc::new(TopicCache::new());
    // Seed a manual-values object with two components; only one is set.
    cache.insert(
        "thrs/controller/thrusters/manual-values",
        json!({
            "thrusters_pump_1": {"Dutypoint": {"Value": 0.5, "TimeStamp": "old"}},
            "thrusters_flowcontrol_aft": {"Setpoint": {"Value": 0.0, "TimeStamp": "old"}}
        }),
    );
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(CapturingPublisher { sent: sent.clone() });
    let mut enum_values = std::collections::BTreeMap::new();
    enum_values.insert("1".to_string(), "CONSTANT_SPEED".to_string());
    let mutations = vec![ModuleMutations {
        module: "thrusters".to_string(),
        mutations: vec![MutationDef {
            derived: Vec::new(),
            gql: "thrustersControlSetThrustersPump1".to_string(),
            kind: MutationKind::SetComponent,
            arg_type: "Float".to_string(),
            arg_name: "value".to_string(),
            key: "thrusters_pump_1".to_string(),
            state_topic: "thrs/controller/thrusters/manual-values".to_string(),
            set_topic: "thrs/controller/thrusters/manual-values/set".to_string(),
            state: None,
            target: None,
            returns: None,
            true_value: None,
            false_value: None,
            input_type_name: Some("PumpInputType".to_string()),
            missing_error: None,
            confirm: None,
            model: None,
            input_fields: vec![
                InputFieldDef {
                    gql: "dutypoint".to_string(),
                    key: "Dutypoint".to_string(),
                    r#type: "Float".to_string(),
                    enum_values: None,
                    enum_type: None,
                    required: true,
                },
                InputFieldDef {
                    gql: "on".to_string(),
                    key: "On".to_string(),
                    r#type: "Boolean".to_string(),
                    enum_values: None,
                    enum_type: None,
                    required: true,
                },
                InputFieldDef {
                    gql: "controlMode".to_string(),
                    key: "ControlMode".to_string(),
                    r#type: "String".to_string(),
                    enum_values: Some(enum_values),
                    enum_type: Some("PumpControlMode".to_string()),
                    required: true,
                },
            ],
        }],
        parameters_object: Default::default(),
        control_values_object: Default::default(),
    }];
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&[], &mutations),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();

    let resp = schema
        .execute(
            "mutation { thrustersControlSetThrustersPump1(value: \
             { dutypoint: 0.8, on: true, controlMode: CONSTANT_SPEED }) }",
        )
        .await;
    assert!(resp.errors.is_empty(), "{:?}", resp.errors);

    let sent = sent.lock().unwrap();
    assert_eq!(sent.len(), 1);
    assert_eq!(sent[0].0, "thrs/controller/thrusters/manual-values/set");
    let published: serde_json::Value = serde_json::from_str(&sent[0].1).unwrap();
    let comp = &published["thrusters_pump_1"];
    assert_eq!(comp["Dutypoint"]["Value"], json!(0.8));
    assert_eq!(comp["On"]["Value"], json!(true));
    // Enum member mapped back to its wire value (1), stored as a number.
    assert_eq!(comp["ControlMode"]["Value"], json!(1));
    // Each leaf got a fresh (non-"old") timestamp.
    assert_ne!(comp["Dutypoint"]["TimeStamp"], json!("old"));
    // The other component is preserved untouched.
    assert_eq!(
        published["thrusters_flowcontrol_aft"]["Setpoint"]["Value"],
        json!(0.0)
    );
    // The republished object has exactly the seeded components as
    // top-level keys: the cache's flattened field view (which also holds
    // the leaf keys `Dutypoint`/`Setpoint` at the top level) must not
    // leak into what the controller receives.
    let mut keys: Vec<&String> = published.as_object().unwrap().keys().collect();
    keys.sort();
    assert_eq!(
        keys,
        vec!["thrusters_flowcontrol_aft", "thrusters_pump_1"],
        "republished object carries flattened keys: {published}"
    );
}

#[tokio::test]
async fn test_parameter_mutation_returns_modified_object_and_automation_mode() {
    use crate::model::views::ObjectFieldDef;
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "thrs/controller/thrusters/parameters",
        json!({"CoolingFlow": 25.0, "WarmupTemperature": 60.0}),
    );
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(CapturingPublisher { sent: sent.clone() });
    let mutations = vec![ModuleMutations {
        module: "thrusters".to_string(),
        mutations: vec![
            MutationDef {
                derived: Vec::new(),
                gql: "thrustersParameterSetCoolingFlow".to_string(),
                kind: MutationKind::SetField,
                arg_type: "Float".to_string(),
                arg_name: "value".to_string(),
                key: "CoolingFlow".to_string(),
                state_topic: "thrs/controller/thrusters/parameters".to_string(),
                set_topic: "thrs/controller/thrusters/parameters/set".to_string(),
                state: None,
                target: None,
                returns: None,
                true_value: None,
                false_value: None,
                input_fields: Vec::new(),
                input_type_name: None,
                missing_error: None,
                confirm: None,
                model: None,
            },
            MutationDef {
                derived: Vec::new(),
                gql: "thrustersSetAutomationMode".to_string(),
                kind: MutationKind::SetFlag,
                arg_type: "Boolean".to_string(),
                arg_name: "automatic".to_string(),
                key: "Mode".to_string(),
                state_topic: "thrs/controller/thrusters/automation-mode".to_string(),
                set_topic: "thrs/controller/thrusters/automation-mode/set".to_string(),
                state: None,
                target: None,
                returns: None,
                true_value: Some("automatic".to_string()),
                false_value: Some("manual".to_string()),
                input_fields: Vec::new(),
                input_type_name: None,
                missing_error: None,
                confirm: None,
                model: None,
            },
        ],
        parameters_object: ObjectSectionDef {
            topic: String::new(),
            operation: None,
            type_name: "ThrustersParametersType".into(),
            fields: vec![
                ObjectFieldDef {
                    gql: "coolingFlow".to_string(),
                    key: "CoolingFlow".to_string(),
                    topic: None,
                    operation: None,
                    r#type: Some("Float".to_string()),
                    type_name: None,
                    optional: false,
                    leaves: Vec::new(),
                },
                ObjectFieldDef {
                    gql: "warmupTemperature".to_string(),
                    key: "WarmupTemperature".to_string(),
                    topic: None,
                    operation: None,
                    r#type: Some("Float".to_string()),
                    type_name: None,
                    optional: false,
                    leaves: Vec::new(),
                },
            ],
        },
        control_values_object: Default::default(),
    }];
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&[], &mutations),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();

    // Parameter mutation returns the modified parameters object.
    let resp = schema
        .execute(
            "mutation { thrustersParameterSetCoolingFlow(value: 12.34) \
             { coolingFlow warmupTemperature } }",
        )
        .await;
    assert!(resp.errors.is_empty(), "{:?}", resp.errors);
    let data: serde_json::Value = resp.data.into_json().unwrap();
    let obj = &data["thrustersParameterSetCoolingFlow"];
    assert_eq!(obj["coolingFlow"], json!(12.34), "modified field returned");
    assert_eq!(
        obj["warmupTemperature"],
        json!(60.0),
        "other field returned"
    );

    // Automation-mode returns Boolean and publishes a fresh {"Mode": ...}.
    let resp = schema
        .execute("mutation { thrustersSetAutomationMode(automatic: false) }")
        .await;
    assert!(resp.errors.is_empty(), "{:?}", resp.errors);
    let data: serde_json::Value = resp.data.into_json().unwrap();
    // thrs-api's set_automation_mode returns the `automatic` it was given.
    assert_eq!(data["thrustersSetAutomationMode"], json!(false));
    let sent = sent.lock().unwrap();
    let am = sent
        .iter()
        .find(|(t, _)| t == "thrs/controller/thrusters/automation-mode/set")
        .expect("automation-mode publish");
    assert_eq!(
        serde_json::from_str::<serde_json::Value>(&am.1).unwrap(),
        json!({"Mode": "manual"})
    );
}

#[tokio::test]
async fn test_simulation_mutation_rederives_mirror_fields_from_the_new_component() {
    use crate::model::mutations::{DerivedFieldDef, DerivedLeaf, InputFieldDef};
    // dhw's inputs: `DrivesFlowRecovery` mirrors `DhwDrivesSupply`'s flow
    // and temperature (a pydantic computed_field thrs-api re-serializes).
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "thrs/simulator/simulation-inputs",
        json!({
            "DhwDrivesSupply": {
                "Flow": {"Value": 1.0, "TimeStamp": "old"},
                "Temperature": {"Value": 2.0, "TimeStamp": "old"}
            },
            "DrivesFlowRecovery": {
                "Flow": {"Value": 1.0, "TimeStamp": "old"},
                "Temperature": {"Value": 2.0, "TimeStamp": "old"}
            },
            "Mode": {"Value": 0, "TimeStamp": "old"}
        }),
    );
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(CapturingPublisher { sent: sent.clone() });
    let leaf = |arg: &str, wire: &str| InputFieldDef {
        gql: arg.to_string(),
        key: wire.to_string(),
        r#type: "Float".to_string(),
        enum_values: None,
        enum_type: None,
        required: true,
    };
    let mut leaves = BTreeMap::new();
    for (k, v) in [("Flow", "Flow"), ("Temperature", "Temperature")] {
        leaves.insert(
            k.to_string(),
            DerivedLeaf::Source {
                component: "DhwDrivesSupply".to_string(),
                leaf: v.to_string(),
            },
        );
    }
    let mutations = vec![ModuleMutations {
        module: "dhw".to_string(),
        mutations: vec![MutationDef {
            gql: "dhwSimulationSetDhwDrivesSupply".to_string(),
            kind: MutationKind::SetComponent,
            arg_type: String::new(),
            arg_name: "value".to_string(),
            key: "DhwDrivesSupply".to_string(),
            state_topic: "thrs/simulator/simulation-inputs".to_string(),
            set_topic: "thrs/simulator/simulation-inputs/set".to_string(),
            state: None,
            target: None,
            returns: None,
            true_value: None,
            false_value: None,
            input_type_name: Some("BoundaryInputType".to_string()),
            missing_error: None,
            confirm: None,
            model: None,
            input_fields: vec![leaf("flow", "Flow"), leaf("temperature", "Temperature")],
            derived: vec![DerivedFieldDef {
                key: "DrivesFlowRecovery".to_string(),
                leaves,
            }],
        }],
        parameters_object: Default::default(),
        control_values_object: Default::default(),
    }];
    let schema = build_schema(
        cache,
        SchemaInputs {
            views: &schema_views(&[], &mutations),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();
    let resp = schema
        .execute(
            "mutation { dhwSimulationSetDhwDrivesSupply(value: { flow: 0.5, temperature: 0.25 }) }",
        )
        .await;
    assert!(resp.errors.is_empty(), "{:?}", resp.errors);
    let sent = sent.lock().unwrap();
    let published: serde_json::Value = serde_json::from_str(&sent[0].1).unwrap();
    // The mirror carries the new component's leaves verbatim (value and
    // the fresh timestamp), exactly like thrs-api's re-serialized model.
    assert_eq!(
        published["DrivesFlowRecovery"],
        published["DhwDrivesSupply"]
    );
    assert_eq!(published["DrivesFlowRecovery"]["Flow"]["Value"], json!(0.5));
    assert_ne!(
        published["DrivesFlowRecovery"]["Flow"]["TimeStamp"],
        json!("old")
    );
    assert_eq!(published["Mode"]["Value"], json!(0));
}

#[test]
fn test_duplicate_input_type_keeps_first_definition() {
    // Two mutations naming their input `AdsorptionChillerInputType` with
    // different fields (control vs. simulation component): the schema
    // serves the first one, like thrs-api's Strawberry.
    let control = InputObject::new("AdsorptionChillerInputType")
        .field(InputValue::new(
            "enable",
            TypeRef::named_nn(TypeRef::BOOLEAN),
        ))
        .field(InputValue::new(
            "coolingSetpoint",
            TypeRef::named_nn(TypeRef::FLOAT),
        ));
    let simulation = InputObject::new("AdsorptionChillerInputType").field(InputValue::new(
        "freeCooling",
        TypeRef::named_nn(TypeRef::BOOLEAN),
    ));
    let mutation = Object::new("Mutation").field(
        Field::new("set", TypeRef::named_nn(TypeRef::BOOLEAN), |_| {
            FieldFuture::new(async { Ok(Some(FieldValue::value(true))) })
        })
        .argument(InputValue::new(
            "value",
            TypeRef::named_nn("AdsorptionChillerInputType"),
        )),
    );
    let query = Object::new("Query").field(Field::new(
        "ok",
        TypeRef::named_nn(TypeRef::BOOLEAN),
        |_| FieldFuture::new(async { Ok(Some(FieldValue::value(true))) }),
    ));
    let schema = finish_schema(
        query,
        Some(mutation),
        vec![control.into(), simulation.into()],
    )
    .unwrap();
    let sdl = schema.sdl();
    let def = sdl
        .split("input AdsorptionChillerInputType")
        .nth(1)
        .expect("input type in SDL");
    let def = &def[..def.find('}').unwrap()];
    assert!(
        def.contains("enable") && def.contains("coolingSetpoint"),
        "{def}"
    );
    assert!(!def.contains("freeCooling"), "{def}");
}

#[test]
fn test_no_mutation_type_without_publisher() {
    // Mutations declared but no publisher (read-only deploy): no Mutation
    // type in the schema.
    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            views: &schema_views(&[], &cooling_flow_mutation()),
            ..Default::default()
        },
    )
    .unwrap();
    assert!(!schema.sdl().contains("type Mutation"), "{}", schema.sdl());
}

#[test]
fn test_no_modules_query_without_module_views() {
    // Without any module-view specs the flat schema is unchanged: no
    // `modules` query field, no `Modules` type.
    let topics = vec![TopicDef {
        topic: "test/channel".to_string(),
        fields: vec![FieldDef {
            name: "value".to_string(),
            graphql_type: "Float".to_string(),
        }],
        payload_schema: None,
        ttl_secs: 300,
    }];
    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();
    let sdl = schema.sdl();
    assert!(!sdl.contains("type Modules"), "{sdl}");
}

#[tokio::test]
async fn test_query_returns_null_for_missing_topic() {
    let topics = vec![TopicDef {
        topic: "test/channel".to_string(),
        fields: vec![FieldDef {
            name: "value".to_string(),
            graphql_type: "Float".to_string(),
        }],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema.execute("{ testChannel { value } }").await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["testChannel"], json!(null));
}

#[tokio::test]
async fn test_query_returns_null_for_missing_field() {
    let topics = vec![TopicDef {
        topic: "test/channel".to_string(),
        fields: vec![FieldDef {
            name: "value".to_string(),
            graphql_type: "Float".to_string(),
        }],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let cache = Arc::new(TopicCache::new());
    cache.insert("test/channel", json!({"other": 1.0}));
    let schema = build_schema(
        cache,
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema.execute("{ testChannel { value } }").await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["testChannel"]["value"], json!(null));
}

#[tokio::test]
async fn test_query_unknown_field_errors() {
    let topics = vec![TopicDef {
        topic: "test/channel".to_string(),
        fields: vec![FieldDef {
            name: "value".to_string(),
            graphql_type: "Float".to_string(),
        }],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema.execute("{ testChannel { nope } }").await;
    assert!(!response.errors.is_empty());
}

#[tokio::test]
async fn test_topics_field_lists_all_topics() {
    let topics = vec![
        TopicDef {
            topic: "a/b".to_string(),
            fields: vec![],
            payload_schema: None,
            ttl_secs: 300,
        },
        TopicDef {
            topic: "c/d".to_string(),
            fields: vec![],
            payload_schema: None,
            ttl_secs: 300,
        },
    ];

    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema.execute("{ topics }").await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["topics"], json!(["a/b", "c/d"]));
}

#[tokio::test]
async fn test_query_multiple_topics() {
    let topics = vec![
        TopicDef {
            topic: "a/b".to_string(),
            fields: vec![FieldDef {
                name: "x".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        },
        TopicDef {
            topic: "c/d".to_string(),
            fields: vec![FieldDef {
                name: "y".to_string(),
                graphql_type: "Float".to_string(),
            }],
            payload_schema: None,
            ttl_secs: 300,
        },
    ];

    let cache = Arc::new(TopicCache::new());
    cache.insert("a/b", json!({"x": 1.5}));
    cache.insert("c/d", json!({"y": 2.5}));
    let schema = build_schema(
        cache,
        SchemaInputs {
            topics: &topics,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema.execute("{ aB { x } cD { y } }").await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["aB"]["x"], json!(1.5));
    assert_eq!(data["cD"]["y"], json!(2.5));
}

fn power_tag_group() -> Vec<TopicGroupDef> {
    vec![TopicGroupDef {
        group: "power-tags".to_string(),
        pattern: "power-tags/+/+".to_string(),
        params: vec!["panel".to_string(), "slug".to_string()],
        fields: vec![
            FieldDef {
                name: "active_power_total".to_string(),
                graphql_type: "Float".to_string(),
            },
            FieldDef {
                name: "current_a".to_string(),
                graphql_type: "Float".to_string(),
            },
        ],
        payload_schema: None,
        field_schemas: BTreeMap::new(),
        value_extensions: BTreeMap::from([
            (
                "active_power_total".to_string(),
                BTreeMap::from([("unit".to_string(), "W".to_string())]),
            ),
            (
                "current_a".to_string(),
                BTreeMap::from([("unit".to_string(), "A".to_string())]),
            ),
        ]),
        ttl_secs: 300,
    }]
}

fn power_tag_metadata() -> Vec<MetadataFile> {
    serde_json::from_value(json!([
        {
            "group": "power-tags",
            "topics": [
                {
                    "topic": "power-tags/10P1/test-consumer",
                    "metadata": {
                        "panel": "10P1",
                        "slug": "test-consumer",
                        "component": "150F01",
                        "consumer": "TEST CONSUMER"
                    }
                },
                {
                    "topic": "power-tags/10P2/no-data",
                    "metadata": {"component": "151F01", "slug": "no-data"}
                }
            ]
        }
    ]))
    .unwrap()
}

#[tokio::test]
async fn test_group_list_returns_metadata_and_values() {
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "power-tags/10P1/test-consumer",
        json!({"active_power_total": 42.0}),
    );
    let schema = build_schema(
        cache,
        SchemaInputs {
            groups: &power_tag_group(),
            metadata: &power_tag_metadata(),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute(
            "{ powerTags { topic \
             metadata { panel component consumer values { name unit } } \
             values { activePowerTotal } } }",
        )
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    let rows = data["powerTags"].as_array().unwrap();
    assert_eq!(rows.len(), 2);

    assert_eq!(rows[0]["topic"], json!("power-tags/10P1/test-consumer"));
    assert_eq!(rows[0]["metadata"]["panel"], json!("10P1"));
    assert_eq!(rows[0]["metadata"]["component"], json!("150F01"));
    assert_eq!(rows[0]["metadata"]["consumer"], json!("TEST CONSUMER"));
    assert_eq!(
        rows[0]["metadata"]["values"],
        json!([
            {"name": "activePowerTotal", "unit": "W"},
            {"name": "currentA", "unit": "A"}
        ])
    );
    assert_eq!(rows[0]["values"]["activePowerTotal"], json!(42.0));

    // Second row has no cached MQTT data: static fields present, live null
    assert_eq!(rows[1]["topic"], json!("power-tags/10P2/no-data"));
    assert_eq!(rows[1]["metadata"]["panel"], json!(null));
    assert_eq!(rows[1]["metadata"]["component"], json!("151F01"));
    assert_eq!(rows[1]["values"]["activePowerTotal"], json!(null));
}

#[tokio::test]
async fn test_group_without_mqtt_data_serves_static() {
    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            groups: &power_tag_group(),
            metadata: &power_tag_metadata(),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute("{ powerTags { metadata { component slug } } }")
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    let rows = data["powerTags"].as_array().unwrap();
    assert_eq!(rows.len(), 2);
    assert_eq!(rows[0]["metadata"]["component"], json!("150F01"));
    assert_eq!(rows[0]["metadata"]["slug"], json!("test-consumer"));
}

#[tokio::test]
async fn test_group_without_metadata_omits_query_field() {
    // Without metadata there is no enumeration source, so no list field
    // (empty object types would be invalid GraphQL).
    let schema = build_schema(
        Arc::new(TopicCache::new()),
        SchemaInputs {
            groups: &power_tag_group(),
            ..Default::default()
        },
    )
    .unwrap();
    let sdl = schema.sdl();
    assert!(!sdl.contains("powerTags"), "{sdl}");
}

#[tokio::test]
async fn test_group_live_values_expire_to_null() {
    let per_topic =
        std::collections::HashMap::from([("power-tags/10P1/test-consumer".to_string(), 0u64)]);
    let cache = Arc::new(TopicCache::with_ttl(60, per_topic));
    cache.insert("power-tags/10P1/test-consumer", json!({"current_a": 1.0}));
    let schema = build_schema(
        cache.clone(),
        SchemaInputs {
            groups: &power_tag_group(),
            metadata: &power_tag_metadata(),
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute("{ powerTags { values { currentA } } }")
        .await;
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["powerTags"][0]["values"]["currentA"], json!(null));

    // A topic without a zero-TTL override keeps serving its cached value
    cache.insert("power-tags/10P2/no-data", json!({"current_a": 2.5}));
    let response = schema
        .execute("{ powerTags { values { currentA } } }")
        .await;
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["powerTags"][1]["values"]["currentA"], json!(2.5));
}

#[tokio::test]
async fn test_power_tag_bucket_grouping() {
    // `group_by: "panel"` on the group's metadata file enables bucket queries.
    let mut metadata = power_tag_metadata();
    metadata[0].group_by = Some("panel".to_string());
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        "power-tags/10P1/test-consumer",
        json!({"active_power_total": 42.0}),
    );
    let schema = build_schema(
        cache,
        SchemaInputs {
            groups: &power_tag_group(),
            metadata: &metadata,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute(
            "{ powerTagBuckets { id powerTags { topic values { activePowerTotal } } } \
             powerTagBucket(id: \"10P1\") { id powerTags { topic } } }",
        )
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();

    // Entries without the `group_by` attribute land in the "unknown" bucket.
    let buckets = data["powerTagBuckets"].as_array().unwrap();
    assert_eq!(buckets.len(), 2);
    assert_eq!(buckets[0]["id"], json!("10P1"));
    assert_eq!(
        buckets[0]["powerTags"][0]["topic"],
        json!("power-tags/10P1/test-consumer")
    );
    assert_eq!(
        buckets[0]["powerTags"][0]["values"]["activePowerTotal"],
        json!(42.0)
    );
    assert_eq!(buckets[1]["id"], json!("unknown"));
    assert_eq!(
        buckets[1]["powerTags"][0]["topic"],
        json!("power-tags/10P2/no-data")
    );

    assert_eq!(
        data["powerTagBucket"]["powerTags"][0]["topic"],
        json!("power-tags/10P1/test-consumer")
    );

    // Unknown bucket ids resolve to null.
    let response = schema
        .execute("{ powerTagBucket(id: \"nope\") { id } }")
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["powerTagBucket"], json!(null));
}

#[tokio::test]
async fn test_grouped_by_queries_are_generic() {
    // Any group whose metadata file declares `group_by` gains grouped
    // queries — the names derive from group + attribute, not from a
    // hardcoded domain.
    let mut group = power_tag_group()[0].clone();
    group.group = "fuel-tags".to_string();
    group.pattern = "fuel-tags/+/+".to_string();
    let mut metadata = power_tag_metadata();
    metadata[0].group = "fuel-tags".to_string();
    metadata[0].group_by = Some("tank".to_string());
    metadata[0].topics[0]
        .metadata
        .insert("tank".to_string(), json!("T01"));

    let cache = Arc::new(TopicCache::new());
    let schema = build_schema(
        cache,
        SchemaInputs {
            groups: &[group],
            metadata: &metadata,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute(
            "{ fuelTagBuckets { id fuelTags { topic } } \
             fuelTagBucket(id: \"T01\") { id } }",
        )
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();

    // Entries without a `tank` attribute land in the "unknown" bucket.
    let buckets = data["fuelTagBuckets"].as_array().unwrap();
    assert_eq!(buckets.len(), 2);
    assert_eq!(buckets[0]["id"], json!("T01"));
    assert_eq!(
        buckets[0]["fuelTags"][0]["topic"],
        json!("power-tags/10P1/test-consumer")
    );
    assert_eq!(buckets[1]["id"], json!("unknown"));
    assert_eq!(data["fuelTagBucket"]["id"], json!("T01"));
}

#[tokio::test]
async fn test_concrete_topic_gains_metadata_field() {
    let topics = vec![TopicDef {
        topic: "sensor/temp".to_string(),
        fields: vec![FieldDef {
            name: "celsius".to_string(),
            graphql_type: "Float".to_string(),
        }],
        payload_schema: None,
        ttl_secs: 300,
    }];
    let metadata: Vec<MetadataFile> = serde_json::from_value(json!([
        {
            "group": "sensors",
            "topics": [
                {"topic": "sensor/temp", "metadata": {"room": "galley"}}
            ]
        }
    ]))
    .unwrap();

    let cache = Arc::new(TopicCache::new());
    cache.insert("sensor/temp", json!({"celsius": 21.5}));
    let schema = build_schema(
        cache,
        SchemaInputs {
            topics: &topics,
            metadata: &metadata,
            ..Default::default()
        },
    )
    .unwrap();

    let response = schema
        .execute("{ sensorTemp { celsius metadata { room } } }")
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["sensorTemp"]["celsius"], json!(21.5));
    assert_eq!(data["sensorTemp"]["metadata"]["room"], json!("galley"));
}

#[tokio::test]
async fn test_health_endpoint() {
    let app = router(build_schema(Arc::new(TopicCache::new()), SchemaInputs::default()).unwrap());

    let response = app
        .oneshot(
            axum::http::Request::builder()
                .uri("/health")
                .body(axum::body::Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
}

#[tokio::test]
async fn test_graphql_endpoint_returns_cached_values() {
    let topics = vec![TopicDef {
        topic: "test/channel".to_string(),
        fields: vec![FieldDef {
            name: "value".to_string(),
            graphql_type: "Float".to_string(),
        }],
        payload_schema: None,
        ttl_secs: 300,
    }];

    let cache = Arc::new(TopicCache::new());
    cache.insert("test/channel", json!({"value": 42.0}));
    let app = router(
        build_schema(
            cache,
            SchemaInputs {
                topics: &topics,
                ..Default::default()
            },
        )
        .unwrap(),
    );

    let request = axum::http::Request::builder()
        .method("POST")
        .uri("/graphql")
        .header("content-type", "application/json")
        .body(axum::body::Body::from(
            r#"{"query": "{ testChannel { value } }"}"#,
        ))
        .unwrap();

    let response = app.oneshot(request).await.unwrap();
    assert_eq!(response.status(), StatusCode::OK);

    let body = axum::body::to_bytes(response.into_body(), 1024 * 1024)
        .await
        .unwrap();
    let data: serde_json::Value = serde_json::from_slice(&body).unwrap();
    assert_eq!(data["data"]["testChannel"]["value"], json!(42.0));
}

fn leaf(gql: &str, raw: &str, ty: &str) -> LeafDef {
    LeafDef {
        gql: gql.to_string(),
        key: raw.to_string(),
        r#type: ty.to_string(),
        enum_values: None,
        enum_type: None,
        optional: false,
        actuated_key: None,
        default: None,
    }
}

fn sensor_field(gql: &str, topic: &str) -> StampedFieldDef {
    StampedFieldDef {
        gql: gql.to_string(),
        type_name: format!("{gql}Type"),
        topic: topic.to_string(),
        operation: None,
        leaves: vec![leaf("flow", "Flow", "Float")],
        computed: false,
    }
}

#[tokio::test]
async fn test_actuated_control_values_assembled_from_device_topics_and_rekeyed() {
    // thrs-api's controlValues is the actuated control values: one device
    // topic per component read through the `CC_*` keys. The section is
    // null until every component is cached with its required keys, then
    // the shared component type reads the plain aliases.
    let pump_topic = "simulation/500000-thrs/thrusters/thrusters-pump1";
    let valve_topic = "simulation/500000-thrs/thrusters/thrusters-flowcontrol-aft";
    let cache = Arc::new(TopicCache::new());
    cache.insert(
        pump_topic,
        json!({
            "Speed": {"Value": 3.0, "TimeStamp": "2024-01-01T00:00:00Z"},
            "CC_DutyPoint": {"Value": 0.42, "TimeStamp": "2024-01-01T00:00:00Z"},
            "CC_OnOff": {"Value": true, "TimeStamp": "2024-01-01T00:00:00Z"}
        }),
    );
    let mut dutypoint = leaf("dutypoint", "Dutypoint", "Float");
    dutypoint.actuated_key = Some("CC_DutyPoint".to_string());
    let mut on = leaf("on", "On", "Boolean");
    on.actuated_key = Some("CC_OnOff".to_string());
    let mut setpoint = leaf("setpoint", "Setpoint", "Float");
    setpoint.actuated_key = Some("CC_Setpoint".to_string());
    let views = vec![ModuleView {
        module: "thrusters".to_string(),
        modules_type_name: "ControlModules".into(),
        type_name: "ThrustersControlModule".into(),
        sensor_values_type_name: "ThrustersSensorValuesType".into(),
        control_values: Some(ObjectSectionDef {
            topic: String::new(),
            operation: None,
            type_name: "ThrustersControlValuesType".to_string(),
            fields: vec![
                ObjectFieldDef {
                    gql: "thrustersPump1".to_string(),
                    key: "thrusters_pump1".to_string(),
                    topic: Some(pump_topic.to_string()),
                    operation: None,
                    type_name: Some("ControlPumpType".to_string()),
                    optional: false,
                    r#type: None,
                    leaves: vec![dutypoint, on],
                },
                ObjectFieldDef {
                    gql: "thrustersFlowcontrolAft".to_string(),
                    key: "thrusters_flowcontrol_aft".to_string(),
                    topic: Some(valve_topic.to_string()),
                    operation: None,
                    type_name: Some("ControlValveType".to_string()),
                    optional: false,
                    r#type: None,
                    leaves: vec![setpoint],
                },
            ],
        }),
        sensor_values: vec![sensor_field("thrustersFlowAft", "simulation/x/flow-aft")],
        ..Default::default()
    }];
    let schema = build_schema(
        cache.clone(),
        SchemaInputs {
            views: &schema_views(&views, &[]),
            ..Default::default()
        },
    )
    .unwrap();
    let query = "{ modules { thrusters { controlValues { \
                 thrustersPump1 { dutypoint { value } on { value } } \
                 thrustersFlowcontrolAft { setpoint { value } } } } } }";
    // Valve topic missing -> the whole section is null, no errors.
    let response = schema.execute(query).await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["modules"]["thrusters"]["controlValues"], json!(null));
    // Valve payload with only the request setpoint (no CC_) is incomplete too.
    cache.insert(
        valve_topic,
        json!({"Setpoint": {"Value": 1.0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
    assert_eq!(data["modules"]["thrusters"]["controlValues"], json!(null));
    // Actuated key present -> complete; values come from the CC_ keys.
    cache.insert(
        valve_topic,
        json!({
            "Setpoint": {"Value": 1.0, "TimeStamp": "2024-01-01T00:00:00Z"},
            "CC_Setpoint": {"Value": 0.5, "TimeStamp": "2024-01-01T00:00:00Z"}
        }),
    );
    let response = schema.execute(query).await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    let cv = &data["modules"]["thrusters"]["controlValues"];
    assert_eq!(cv["thrustersPump1"]["dutypoint"]["value"], json!(0.42));
    assert_eq!(cv["thrustersPump1"]["on"]["value"], json!(true));
    assert_eq!(
        cv["thrustersFlowcontrolAft"]["setpoint"]["value"],
        json!(0.5)
    );
}

#[tokio::test]
async fn test_sensor_values_null_until_every_required_leaf_is_cached() {
    // thrs-api serves sensorValues only once its whole model validates.
    let cache = Arc::new(TopicCache::new());
    let a = "simulation/x/flow-aft";
    let b = "simulation/x/flow-fwd";
    cache.insert(
        a,
        json!({"Flow": {"Value": 1.0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    let views = vec![ModuleView {
        module: "thrusters".to_string(),
        modules_type_name: "ControlModules".into(),
        type_name: "ThrustersControlModule".into(),
        sensor_values_type_name: "ThrustersSensorValuesType".into(),
        sensor_values: vec![
            sensor_field("thrustersFlowAft", a),
            sensor_field("thrustersFlowFwd", b),
        ],
        ..Default::default()
    }];
    let schema = build_schema(
        cache.clone(),
        SchemaInputs {
            views: &schema_views(&views, &[]),
            ..Default::default()
        },
    )
    .unwrap();
    let query =
        "{ modules { thrusters { sensorValues { thrustersFlowAft { flow { value } } } } } }";
    let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
    assert_eq!(data["modules"]["thrusters"]["sensorValues"], json!(null));
    // Present but null value for a required leaf is still incomplete.
    cache.insert(
        b,
        json!({"Flow": {"Value": null, "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
    assert_eq!(data["modules"]["thrusters"]["sensorValues"], json!(null));
    cache.insert(
        b,
        json!({"Flow": {"Value": 2.0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    let response = schema.execute(query).await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(
        data["modules"]["thrusters"]["sensorValues"]["thrustersFlowAft"]["flow"]["value"],
        json!(1.0)
    );
}

#[tokio::test]
async fn test_enable_optional_sensor_values_serves_cached_fields_and_nulls_the_rest() {
    // ENABLE_OPTIONAL_SENSOR_VALUES: each sensor field answers on its own topic.
    let cache = Arc::new(TopicCache::new());
    let a = "simulation/x/flow-aft";
    let b = "simulation/x/flow-fwd";
    let views = vec![ModuleView {
        module: "thrusters".to_string(),
        modules_type_name: "ControlModules".into(),
        type_name: "ThrustersControlModule".into(),
        sensor_values_type_name: "ThrustersSensorValuesType".into(),
        sensor_values: vec![
            sensor_field("thrustersFlowAft", a),
            sensor_field("thrustersFlowFwd", b),
        ],
        ..Default::default()
    }];
    let schema = build_schema(
        cache.clone(),
        SchemaInputs {
            views: &schema_views(&views, &[]),
            enable_optional_sensor_values: true,
            ..Default::default()
        },
    )
    .unwrap();
    // The sensor fields are nullable in this mode (schema change).
    let sdl = schema.sdl();
    assert!(
        sdl.contains("thrustersFlowAft: thrustersFlowAftType\n"),
        "expected nullable sensor field in:\n{sdl}"
    );
    let query = "{ modules { thrusters { sensorValues { \
                 thrustersFlowAft { flow { value } } \
                 thrustersFlowFwd { flow { value } } } } } }";
    // Nothing cached yet: the container itself is null, like thrs-api.
    let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
    assert_eq!(data["modules"]["thrusters"]["sensorValues"], json!(null));
    // One topic cached: that field serves, the other is null, no errors.
    cache.insert(
        a,
        json!({"Flow": {"Value": 1.0, "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    let response = schema.execute(query).await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    let sv = &data["modules"]["thrusters"]["sensorValues"];
    assert_eq!(sv["thrustersFlowAft"]["flow"]["value"], json!(1.0));
    assert_eq!(sv["thrustersFlowFwd"], json!(null));
    // A cached payload missing a required leaf value nulls only its field.
    cache.insert(
        b,
        json!({"Flow": {"Value": null, "TimeStamp": "2024-01-01T00:00:00Z"}}),
    );
    let response = schema.execute(query).await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    let sv = &data["modules"]["thrusters"]["sensorValues"];
    assert_eq!(sv["thrustersFlowAft"]["flow"]["value"], json!(1.0));
    assert_eq!(sv["thrustersFlowFwd"], json!(null));
}

#[tokio::test]
async fn test_control_mode_section_and_empty_placeholder() {
    // `controlMode { automatic automaticMode { ... } }`: null when the
    // topic is absent, `automatic` derived from `AutomaticMode` being
    // non-null, nested groups typed by thrs-api's names, and a fieldless
    // model rendered with the `Empty: Void` placeholder.
    let topic = "thrs/controller/pvt/control-mode";
    let cache = Arc::new(TopicCache::new());
    let group = PlainObjectDef {
        type_name: "PvtGroupControlModeType".to_string(),
        fields: vec![PlainFieldDef {
            gql: "mode".to_string(),
            key: "Mode".to_string(),
            r#type: Some("String".to_string()),
            object: None,
            optional: false,
        }],
    };
    let views = vec![ModuleView {
        module: "pvt".to_string(),
        modules_type_name: "ControlModules".into(),
        type_name: "PvtControlModule".into(),
        sensor_values_type_name: "PvtSensorValuesType".into(),
        control_mode: Some(ControlModeDef {
            topic: topic.to_string(),
            operation: None,
            type_name: "PvtSwitchingControlModeType".into(),
            key: "AutomaticMode".to_string(),
            automatic_mode: PlainObjectDef {
                type_name: "PvtControlModeType".to_string(),
                fields: vec![
                    PlainFieldDef {
                        gql: "aft".to_string(),
                        key: "Aft".to_string(),
                        r#type: None,
                        object: Some(group.clone()),
                        optional: false,
                    },
                    PlainFieldDef {
                        gql: "empty".to_string(),
                        key: "Empty".to_string(),
                        r#type: None,
                        object: Some(PlainObjectDef {
                            type_name: "ConsumersControlModeType".to_string(),
                            fields: vec![],
                        }),
                        optional: true,
                    },
                ],
            },
        }),
        sensor_values: vec![sensor_field("pvtFlow", "simulation/x/pvt-flow")],
        ..Default::default()
    }];
    let schema = build_schema(
        cache.clone(),
        SchemaInputs {
            views: &schema_views(&views, &[]),
            ..Default::default()
        },
    )
    .unwrap();
    let query = "{ modules { pvt { controlMode { automatic \
                 automaticMode { aft { mode } empty { Empty } } } } } }";
    let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
    assert_eq!(data["modules"]["pvt"]["controlMode"], json!(null));
    cache.insert(topic, json!({"AutomaticMode": null}));
    let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
    assert_eq!(
        data["modules"]["pvt"]["controlMode"],
        json!({"automatic": false, "automaticMode": null})
    );
    cache.insert(
        topic,
        json!({"AutomaticMode": {"Aft": {"Mode": "idle"}, "Empty": {}}}),
    );
    let response = schema.execute(query).await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(
        data["modules"]["pvt"]["controlMode"],
        json!({"automatic": true,
               "automaticMode": {"aft": {"mode": "idle"}, "empty": {"Empty": null}}})
    );
}

/// The simulation lifecycle as the loader builds it from a document:
/// two simulations (thrusters, pcm) with their inputs/outputs types, the
/// status object and the play/pause/step directives.
fn simulation_view() -> LifecycleDef {
    use crate::asyncapi::OperationIndex;
    use crate::extension::fixtures::{op, DOCUMENT};
    use crate::extension::parse_extension;
    use roas_asyncapi::v3_0::operation::OperationAction;

    let reference = |name: &str| json!({"$ref": format!("#/components/schemas/{name}")});
    let components = json!({"schemas": {
        "PcsMode": {"title": "PcsMode", "type": "integer", "enum": [0, 1],
                    "x-enum-varnames": ["OFF", "PROPULSION"]},
        "StampedPcsMode": {"type": "object", "properties": {
            "Value": reference("PcsMode"), "TimeStamp": {"type": "string"}}},
        "StampedFloat": {"type": "object", "properties": {
            "Value": {"type": "number"}, "TimeStamp": {"type": "string"}}},
        "Pcs": {"title": "Pcs", "type": "object", "properties": {"Mode": reference("StampedPcsMode")}},
        "Boundary": {"title": "Boundary", "type": "object", "properties": {"Flow": reference("StampedFloat")}},
        "FlowBoundary": {"title": "FlowBoundary", "type": "object", "properties": {"Flow": reference("StampedFloat")}},
        "ThrustersInputs": {"type": "object", "properties": {"ThrustersPcs": reference("Pcs")}},
        "ThrustersOutputs": {"type": "object", "properties": {"ThrustersPcmSupply": reference("FlowBoundary")}},
        "PcmInputs": {"type": "object", "properties": {"PcmPvtSupply": reference("Boundary")}},
        "PcmOutputs": {"type": "object", "properties": {"PcmConsumersSupply": reference("FlowBoundary")}},
        "Status": {"type": "object", "properties": {
            "Status": {"type": "string"}, "SimulationTime": {"type": "string", "format": "date-time"}}},
        "Play": {"type": "object", "properties": {
            "PlaybackRate": {"type": "number", "default": 1.0, "minimum": 0.25, "maximum": 10}}},
        "Pause": {"type": "object", "properties": {}},
        "Step": {"type": "object", "properties": {"Seconds": {"type": "number"}}}
    }});
    let inputs = json!({"anyOf": [reference("ThrustersInputs"), reference("PcmInputs")]});
    let outputs = json!({"anyOf": [reference("ThrustersOutputs"), reference("PcmOutputs")]});
    let operations = OperationIndex::from([
        (
            "status.send".to_string(),
            op(
                OperationAction::Send,
                "thrs/simulator/status",
                "thrs/simulator/status",
                reference("Status"),
            ),
        ),
        (
            "inputs.send".to_string(),
            op(
                OperationAction::Send,
                "thrs/simulator/simulation-inputs",
                "thrs/simulator/simulation-inputs",
                inputs.clone(),
            ),
        ),
        (
            "inputs.set.receive".to_string(),
            op(
                OperationAction::Receive,
                "thrs/simulator/simulation-inputs/set",
                "thrs/simulator/simulation-inputs/set",
                inputs,
            ),
        ),
        (
            "outputs.send".to_string(),
            op(
                OperationAction::Send,
                "thrs/simulator/simulation-outputs",
                "thrs/simulator/simulation-outputs",
                outputs,
            ),
        ),
        (
            "play.receive".to_string(),
            op(
                OperationAction::Receive,
                "thrs/simulator/play",
                "thrs/simulator/play",
                reference("Play"),
            ),
        ),
        (
            "pause.receive".to_string(),
            op(
                OperationAction::Receive,
                "thrs/simulator/pause",
                "thrs/simulator/pause",
                reference("Pause"),
            ),
        ),
        (
            "step.receive".to_string(),
            op(
                OperationAction::Receive,
                "thrs/simulator/step",
                "thrs/simulator/step",
                reference("Step"),
            ),
        ),
    ]);
    let extension = json!({
        "version": crate::extension::EXTENSION_VERSION,
        "types": {
            "SimulationPcsType": {"schema": reference("Pcs")},
            "SimulationBoundaryType": {"schema": reference("Boundary")},
            "SimulationFlowBoundaryType": {"schema": reference("FlowBoundary")},
            "ThrustersSimulationInputsType": {"schema": reference("ThrustersInputs")},
            "ThrustersSimulationOutputsType": {"schema": reference("ThrustersOutputs")},
            "PcmSimulationInputsType": {"schema": reference("PcmInputs")},
            "PcmSimulationOutputsType": {"schema": reference("PcmOutputs")}
        },
        "lifecycles": [{
            "gql": "simulation",
            "stateTypeName": "SimulationState",
            "status": {"operation": {"operation": "status.send"}, "key": "Status",
                       "fields": [{"key": "Status"}, {"key": "SimulationTime", "gql": "time"}]},
            "objects": [
                {"gql": "inputs", "operation": {"operation": "inputs.send"},
                 "unionType": "SimulationInputsType", "memberSection": "inputs"},
                {"gql": "outputs", "operation": {"operation": "outputs.send"},
                 "unionType": "SimulationOutputsType", "memberSection": "outputs"}
            ],
            "waitTimeoutS": 0.2,
            "directives": [
                {"gql": "simulationPlay", "target": {"operation": "play.receive"}, "key": "PlaybackRate",
                 "allowedFrom": ["available", "running"], "expectStatus": "running",
                 "preconditionError": "Can only play an available or running simulation",
                 "missingError": "No simulation status available, cannot play"},
                {"gql": "simulationPause", "target": {"operation": "pause.receive"},
                 "allowedFrom": ["running"], "expectStatus": "available",
                 "preconditionError": "Can only pause a running simulation",
                 "missingError": "No simulation status available, cannot pause"},
                {"gql": "simulationStep", "target": {"operation": "step.receive"}, "key": "Seconds",
                 "allowedFrom": ["available"], "expectStatus": "stepping",
                 "preconditionError": "Can only step an available simulation",
                 "missingError": "No simulation status available, cannot step"}
            ],
            "members": [
                {"name": "thrusters",
                 "sections": [
                     {"kind": "object", "gql": "inputs", "typeName": "ThrustersSimulationInputsType"},
                     {"kind": "object", "gql": "outputs", "typeName": "ThrustersSimulationOutputsType"}],
                 "mutations": [{"gql": "thrustersSimulationSetThrustersPcs",
                     "kind": "setComponent", "argName": "value", "key": "ThrustersPcs",
                     "returns": "inputs", "inputTypeName": "PcsInputType",
                     "state": {"operation": "inputs.send"}, "target": {"operation": "inputs.set.receive"}}]},
                {"name": "pcm",
                 "sections": [
                     {"kind": "object", "gql": "inputs", "typeName": "PcmSimulationInputsType"},
                     {"kind": "object", "gql": "outputs", "typeName": "PcmSimulationOutputsType"}],
                 "mutations": []}
            ]
        }]
    });
    let root = BTreeMap::from([(crate::extension::EXTENSION_KEY.to_string(), extension)]);
    let mut ext = parse_extension(Some(&root), Some(&components), DOCUMENT)
        .unwrap()
        .unwrap();
    ext.resolve(&operations, &[]).unwrap();
    ext.lifecycles.remove(0)
}

#[tokio::test]
async fn test_simulation_query_status_union_and_directive_preconditions() {
    let cache = Arc::new(TopicCache::new());
    let sim = simulation_view();
    let sent = Arc::new(std::sync::Mutex::new(Vec::new()));
    let publisher: Arc<dyn TopicPublisher> = Arc::new(CapturingPublisher { sent: sent.clone() });
    let schema = build_schema(
        cache.clone(),
        SchemaInputs {
            lifecycles: std::slice::from_ref(&sim),
            publisher: Some(publisher),
            ..Default::default()
        },
    )
    .unwrap();
    let query = "{ simulation { status time inputs { __typename \
                 ... on ThrustersSimulationInputsType { thrustersPcs { mode { value } } } \
                 ... on PcmSimulationInputsType { pcmPvtSupply { flow { value } } } } \
                 outputs { __typename } } }";
    // No status retained -> `simulation` is null, like thrs-api.
    let data: serde_json::Value = schema.execute(query).await.data.into_json().unwrap();
    assert_eq!(data["simulation"], json!(null));
    cache.insert(
        "thrs/simulator/status",
        json!({"Mode": "thrusters", "Status": "available", "ControlModules": ["thrusters"],
               "SimulationTime": "2026-01-02T03:04:05.678901Z"}),
    );
    // Inputs typed by which simulation's keys the object carries.
    cache.insert(
        "thrs/simulator/simulation-inputs",
        json!({"ThrustersPcs": {"Mode": {"Value": 1, "TimeStamp": "2026-01-01T00:00:00Z"}}}),
    );
    let response = schema.execute(query).await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(data["simulation"]["status"], json!("available"));
    assert_eq!(
        data["simulation"]["time"],
        json!("2026-01-02T03:04:05.678901Z")
    );
    assert_eq!(
        data["simulation"]["inputs"]["__typename"],
        json!("ThrustersSimulationInputsType")
    );
    assert_eq!(
        data["simulation"]["inputs"]["thrustersPcs"]["mode"]["value"],
        json!("PROPULSION")
    );
    assert_eq!(data["simulation"]["outputs"], json!(null));

    // Pause while available: thrs-api's exact precondition error, nothing published.
    let response = schema.execute("mutation { simulationPause }").await;
    assert_eq!(
        response.errors[0].message,
        "Can only pause a running simulation"
    );
    assert!(sent.lock().unwrap().is_empty());
    // Play out of bounds: rejected before publishing.
    let response = schema
        .execute("mutation { simulationPlay(playbackRate: 100) }")
        .await;
    assert!(!response.errors.is_empty());
    assert!(sent.lock().unwrap().is_empty());
    // Play in range: publishes `{"PlaybackRate": 2}` then times out waiting
    // for `running` (nothing flips the status here) with thrs-api's
    // message-less timeout.
    let response = schema
        .execute("mutation { simulationPlay(playbackRate: 2) }")
        .await;
    assert_eq!(sent.lock().unwrap().len(), 1);
    let (topic, payload) = sent.lock().unwrap()[0].clone();
    assert_eq!(topic, "thrs/simulator/play");
    assert_eq!(
        serde_json::from_str::<serde_json::Value>(&payload).unwrap(),
        json!({"PlaybackRate": 2.0})
    );
    assert_eq!(response.errors[0].message, "An unknown error occurred.");

    // Input mutation: restamps the component into the cached inputs object
    // and republishes it; returns the simulation's inputs type.
    let response = schema
        .execute(
            "mutation { thrustersSimulationSetThrustersPcs(value: {mode: OFF}) \
             { thrustersPcs { mode { value } } } }",
        )
        .await;
    assert!(response.errors.is_empty(), "{:?}", response.errors);
    let data: serde_json::Value = response.data.into_json().unwrap();
    assert_eq!(
        data["thrustersSimulationSetThrustersPcs"]["thrustersPcs"]["mode"]["value"],
        json!("OFF")
    );
    let (topic, payload) = sent.lock().unwrap()[1].clone();
    assert_eq!(topic, "thrs/simulator/simulation-inputs/set");
    let published: serde_json::Value = serde_json::from_str(&payload).unwrap();
    assert_eq!(published["ThrustersPcs"]["Mode"]["Value"], json!(0));
}
