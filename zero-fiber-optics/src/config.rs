use serde::Deserialize;

#[derive(Debug, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
pub struct UdpChannels {
    #[serde(rename = "@ip")]
    pub ip: String,
    #[serde(rename = "port", default)]
    pub ports: Vec<Port>,
}

#[derive(Debug, Deserialize, Clone)]
#[allow(dead_code)]
pub struct Port {
    #[serde(rename = "@numport")]
    pub numport: u16,
    #[serde(rename = "@channel")]
    pub channel: String,
    #[serde(rename = "@frequency")]
    pub frequency: Option<f32>,
    #[serde(rename = "@mode")]
    pub mode: Option<String>,
    #[serde(rename = "Var", default)]
    pub variables: Vec<Var>,
}

#[derive(Debug, Deserialize, Clone)]
#[allow(dead_code)]
pub struct Var {
    #[serde(rename = "@num")]
    pub num: Option<u32>,
    #[serde(rename = "@type")]
    pub var_type: String,
    #[serde(rename = "@units")]
    pub units: Option<String>,
    #[serde(rename = "@factor")]
    pub factor: Option<f64>,
    #[serde(rename = "@offset")]
    pub offset: Option<f64>,
    #[serde(rename = "@decimals")]
    pub decimals: Option<u8>,
    #[serde(rename = "@class")]
    pub class: Option<String>,
    #[serde(rename = "@tags")]
    pub tags: Option<String>,
    #[serde(rename = "@description")]
    pub description: Option<String>,
    #[serde(rename = "@name")]
    pub name: String,
    #[serde(rename = "bit", default)]
    pub bits: Vec<Bit>,
}

#[derive(Debug, Deserialize, Clone)]
#[allow(dead_code)]
pub struct Bit {
    #[serde(rename = "@num")]
    pub num: u8,
    #[serde(rename = "$value")]
    pub name: String,
}

pub fn load_config(xml_content: &str) -> Result<UdpChannels, quick_xml::DeError> {
    quick_xml::de::from_str(xml_content)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn load_config_parses_ports_vars_and_bits() {
        let xml = r#"
<udpChannels ip="127.0.0.1">
    <port numport="50000" channel="FiberA" frequency="10" mode="active">
        <Var num="1" type="UnSignedInt16" units="W" factor="10" offset="1" name="Power" />
        <Var num="2" type="8BitBoolRegister" name="Flags">
            <bit num="0">Alarm</bit>
            <bit num="3">LinkUp</bit>
        </Var>
    </port>
</udpChannels>
"#;

        let cfg = load_config(xml).expect("valid xml should parse");
        assert_eq!(cfg.ip, "127.0.0.1");
        assert_eq!(cfg.ports.len(), 1);

        let port = &cfg.ports[0];
        assert_eq!(port.numport, 50000);
        assert_eq!(port.channel, "FiberA");
        assert_eq!(port.frequency, Some(10.0));
        assert_eq!(port.mode.as_deref(), Some("active"));
        assert_eq!(port.variables.len(), 2);

        let power = &port.variables[0];
        assert_eq!(power.name, "Power");
        assert_eq!(power.var_type, "UnSignedInt16");
        assert_eq!(power.units.as_deref(), Some("W"));
        assert_eq!(power.factor, Some(10.0));
        assert_eq!(power.offset, Some(1.0));

        let flags = &port.variables[1];
        assert_eq!(flags.name, "Flags");
        assert_eq!(flags.bits.len(), 2);
        assert_eq!(flags.bits[0].num, 0);
        assert_eq!(flags.bits[0].name, "Alarm");
        assert_eq!(flags.bits[1].num, 3);
        assert_eq!(flags.bits[1].name, "LinkUp");
    }

    #[test]
    fn load_config_returns_error_on_invalid_xml() {
        let xml = "<udpChannels ip=\"127.0.0.1\"><port></udpChannels>";
        assert!(load_config(xml).is_err());
    }
}
