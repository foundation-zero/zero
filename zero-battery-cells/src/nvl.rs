use crate::cells::{PAYLOAD_BYTES, TEMPERATURES_PER_PACK, VOLTAGES_PER_PACK};
use anyhow::{bail, Context, Result};
use nom::branch::alt;
use nom::bytes::complete::{tag, tag_no_case, take_until, take_while, take_while1};
use nom::character::complete::{char, digit1, multispace0, multispace1};
use nom::combinator::{map, map_res};
use nom::error::{ErrorKind, FromExternalError, ParseError};
use nom::multi::{many0, separated_list1};
use nom::sequence::{delimited, pair, preceded, terminated, tuple};
use nom::{Err, IResult};

/// Prefixes that single out the two value families of a cell declaration.
const VOLTAGE_MARKER: &str = "CellVoltage_";
const TEMPERATURE_MARKER: &str = "CellTemperature_";

/// One pack's CODESYS NetVar declaration, as exported by the PLC.
#[derive(Debug, Clone)]
pub struct PackSpec {
    /// Pack name derived from the variable prefix, e.g. `41-1`.
    pub pack: &'static str,
    /// NetVar `ListIdentifier` the sender attaches, e.g. `411`.
    pub list_id: u16,
    /// Variable name prefix without the trailing underscore, e.g. `FOX_05_41_1`.
    pub prefix: String,
    /// Declared variables in transmission order.
    pub declarations: Vec<VarDecl>,
    /// Number of declared cell voltages.
    pub voltage_count: usize,
    /// Number of declared cell temperatures.
    pub temperature_count: usize,
    /// Summed byte size of all declared variables as CODESYS packs them.
    pub declared_bytes: u32,
}

/// One variable declaration from the `VAR_GLOBAL ... END_VAR` block.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct VarDecl {
    pub name: String,
    /// Element type; the whole variable for scalars.
    pub base: IecBase,
    /// Element count: `1` for scalars, `end - start + 1` for arrays.
    pub elements: u32,
    /// Bytes this variable occupies in a packed datagram payload.
    pub bytes: u32,
}

impl PackSpec {
    /// The same layout declared for another pack, e.g. `41-1` -> `42-3`.
    ///
    /// Only the pack segment of the variable names changes (`FOX_05_41_1_...`
    /// becomes `FOX_05_42_3_...`); all packs share one layout.
    pub fn for_list_id(&self, list_id: u16) -> Result<PackSpec> {
        let pack = crate::mapping::pack_name(list_id)
            .with_context(|| format!("list {} is not a known list id", list_id))?;
        let old_tail = self.pack.replace('-', "_");
        let stem = self.prefix.strip_suffix(&old_tail).with_context(|| {
            format!(
                "prefix '{}' does not end in pack {}",
                self.prefix, self.pack
            )
        })?;
        let prefix = format!("{stem}{}", pack.replace('-', "_"));
        let declarations = self
            .declarations
            .iter()
            .map(|declaration| VarDecl {
                name: declaration.name.replacen(&self.prefix, &prefix, 1),
                ..declaration.clone()
            })
            .collect();
        Ok(PackSpec {
            pack,
            list_id,
            prefix,
            declarations,
            ..self.clone()
        })
    }

    /// Refuse declarations this decoder cannot map onto the pack layout.
    ///
    /// A pack may declare fewer values than a fully wired one; the undeclared
    /// tail is zero-padded at decode time. Rejected are over-large declarations
    /// and any layout `decode_pack` would mislabel: every variable must be a
    /// scalar `INT`, and the names must run `{prefix}_CellVoltage_0..` then
    /// `{prefix}_CellTemperature_0..`, contiguous and in that order.
    pub fn validate(&self, source: &str) -> Result<()> {
        if self.voltage_count > VOLTAGES_PER_PACK {
            bail!(
                "{}: pack {} declares {} cell voltages, more than the {} of a full pack",
                source,
                self.pack,
                self.voltage_count,
                VOLTAGES_PER_PACK
            );
        }
        if self.temperature_count > TEMPERATURES_PER_PACK {
            bail!(
                "{}: pack {} declares {} cell temperatures, more than the {} of a full pack",
                source,
                self.pack,
                self.temperature_count,
                TEMPERATURES_PER_PACK
            );
        }
        if self.declared_bytes as usize > PAYLOAD_BYTES {
            bail!(
                "{}: pack {} declares {} byte(s), more than the {} of a full pack",
                source,
                self.pack,
                self.declared_bytes,
                PAYLOAD_BYTES
            );
        }
        if self.voltage_count + self.temperature_count != self.declarations.len() {
            bail!(
                "{}: pack {} declares {} variable(s), but only {} are cell voltages or temperatures",
                source,
                self.pack,
                self.declarations.len(),
                self.voltage_count + self.temperature_count
            );
        }
        self.validate_layout(source)
    }

    /// Check each declaration against the position `decode_pack` reads it from.
    fn validate_layout(&self, source: &str) -> Result<()> {
        let voltages = (0..self.voltage_count).map(|index| (VOLTAGE_MARKER, index));
        let temperatures = (0..self.temperature_count).map(|index| (TEMPERATURE_MARKER, index));
        for (declaration, (marker, index)) in
            self.declarations.iter().zip(voltages.chain(temperatures))
        {
            if declaration.base != IecBase::Int || declaration.elements != 1 {
                bail!(
                    "{}: '{}' is {} x {:?}; cell values must be scalar INTs",
                    source,
                    declaration.name,
                    declaration.elements,
                    declaration.base
                );
            }
            if cell_index(&declaration.name, &self.prefix, marker) != Some(index) {
                bail!(
                    "{}: found '{}' where {}_{}{:03} belongs; cell values must be declared voltages first, then temperatures, each numbered from 000 without gaps",
                    source,
                    declaration.name,
                    self.prefix,
                    marker,
                    index
                );
            }
        }
        Ok(())
    }
}

/// Numeric suffix of `{prefix}_{marker}{digits}`, e.g. `7` for `FOX_05_41_1_CellVoltage_007`.
fn cell_index(name: &str, prefix: &str, marker: &str) -> Option<usize> {
    let digits = name
        .strip_prefix(prefix)?
        .strip_prefix('_')?
        .strip_prefix(marker)?;
    if digits.is_empty() || !digits.bytes().all(|byte| byte.is_ascii_digit()) {
        return None;
    }
    digits.parse().ok()
}

/// Load and parse one pack declaration file from disk.
pub fn load_declaration(path: &str) -> Result<PackSpec> {
    let content =
        std::fs::read_to_string(path).with_context(|| format!("Failed to read {}", path))?;
    parse_declaration(&content).with_context(|| format!("Failed to parse {}", path))
}

/// Parse a `VAR_GLOBAL ... END_VAR` declaration into a [`PackSpec`].
pub fn parse_declaration(declarations: &str) -> Result<PackSpec> {
    let variables = parse_var_declarations(declarations).map_err(anyhow::Error::msg)?;
    let (pack, list_id, prefix) = pack_identity(&variables)?;
    let voltage_count = count_marker(&variables, VOLTAGE_MARKER);
    let temperature_count = count_marker(&variables, TEMPERATURE_MARKER);
    let declared_bytes: u32 = variables.iter().map(|variable| variable.bytes).sum();
    Ok(PackSpec {
        pack,
        list_id,
        prefix,
        declarations: variables,
        voltage_count,
        temperature_count,
        declared_bytes,
    })
}

/// Derive the pack name and list id from the variable prefix, e.g.
/// `FOX_05_41_1_CellVoltage_000` -> (`41-1`, 411, `FOX_05_41_1`).
///
/// The pack must be one of [`crate::mapping::KNOWN_PACKS`].
fn pack_identity(variables: &[VarDecl]) -> Result<(&'static str, u16, String)> {
    let sample = variables
        .iter()
        .find(|variable| variable.name.contains(VOLTAGE_MARKER))
        .map(|variable| variable.name.as_str())
        .context("declaration has no CellVoltage_ variable")?;
    let prefix = sample.split(VOLTAGE_MARKER).next().unwrap_or(sample);

    let mut segments = prefix.rsplit('_').filter(|segment| !segment.is_empty());
    let (Some(index), Some(number)) = (segments.next(), segments.next()) else {
        bail!(
            "cannot derive a pack name from variable prefix '{}'",
            prefix
        );
    };
    let derived = format!("{number}-{index}");
    let list_id = crate::mapping::list_id(&derived)?;
    let pack = crate::mapping::pack_name(list_id)
        .filter(|known| *known == derived)
        .with_context(|| format!("pack {} is not a known pack", derived))?;
    Ok((pack, list_id, prefix.trim_end_matches('_').to_string()))
}

/// Number of declarations whose name carries the given marker.
fn count_marker(variables: &[VarDecl], marker: &str) -> usize {
    variables
        .iter()
        .filter(|variable| variable.name.contains(marker))
        .count()
}

/// IEC 61131-3 data types this decoder can map to a wire width.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum IecBase {
    Bool,
    Byte,
    Word,
    DWord,
    LWord,
    Int,
    DInt,
    LInt,
    UInt,
    UDInt,
    ULInt,
    Real,
    LReal,
}

impl IecBase {
    /// Bytes one element occupies in a packed datagram payload.
    pub fn bytes(self) -> u32 {
        match self {
            IecBase::Bool | IecBase::Byte => 1,
            IecBase::Word | IecBase::Int | IecBase::UInt => 2,
            IecBase::DWord | IecBase::DInt | IecBase::UDInt | IecBase::Real => 4,
            IecBase::LWord | IecBase::LInt | IecBase::ULInt | IecBase::LReal => 8,
        }
    }

    fn from_keyword(keyword: &str) -> Option<Self> {
        match keyword {
            "BOOL" => Some(IecBase::Bool),
            "BYTE" => Some(IecBase::Byte),
            "WORD" => Some(IecBase::Word),
            "DWORD" => Some(IecBase::DWord),
            "LWORD" => Some(IecBase::LWord),
            "INT" => Some(IecBase::Int),
            "DINT" => Some(IecBase::DInt),
            "LINT" => Some(IecBase::LInt),
            "UINT" => Some(IecBase::UInt),
            "UDINT" => Some(IecBase::UDInt),
            "ULINT" => Some(IecBase::ULInt),
            "REAL" => Some(IecBase::Real),
            "LREAL" => Some(IecBase::LReal),
            _ => None,
        }
    }
}

/// How one declared variable is laid out: a fixed-width base type or an array of one.
#[derive(Debug, Clone, PartialEq, Eq)]
enum DeclType {
    Base(IecBase),
    Array(IecBase, u32),
}

impl DeclType {
    fn elements(&self) -> u32 {
        match self {
            DeclType::Base(_) => 1,
            DeclType::Array(_, elements) => *elements,
        }
    }

    fn base(&self) -> IecBase {
        match self {
            DeclType::Base(base) | DeclType::Array(base, _) => *base,
        }
    }
}

/// Error type for the declaration parser, carrying a human-readable message.
#[derive(Debug, Clone)]
pub struct DeclError {
    message: String,
}

impl ParseError<&[u8]> for DeclError {
    fn from_error_kind(_input: &[u8], kind: ErrorKind) -> Self {
        DeclError {
            message: format!("unexpected declaration syntax ({kind:?})"),
        }
    }

    fn append(_input: &[u8], _kind: ErrorKind, other: Self) -> Self {
        other
    }

    fn or(self, _other: Self) -> Self {
        self
    }
}

/// nom result over declaration text, carrying readable [`DeclError`] messages.
type DeclResult<'a, T> = IResult<&'a [u8], T, DeclError>;

impl FromExternalError<&[u8], std::num::ParseIntError> for DeclError {
    fn from_external_error(
        _input: &[u8],
        _kind: ErrorKind,
        error: std::num::ParseIntError,
    ) -> Self {
        DeclError {
            message: format!("invalid unsigned number: {error}"),
        }
    }
}

/// Parse the `VAR_GLOBAL ... END_VAR` declarations of one pack.
///
/// CODESYS packs the declared variables into the UDP payload in declaration
/// order with no padding, so transmission order is declaration order.
pub fn parse_var_declarations(declarations: &str) -> std::result::Result<Vec<VarDecl>, String> {
    let input = declarations.as_bytes();
    let (rest, parsed) = preceded(
        preceded(
            multispace0,
            terminated(tag_no_case("VAR_GLOBAL"), multispace0),
        ),
        terminated(
            many0(item),
            preceded(multispace0, terminated(tag_no_case("END_VAR"), multispace0)),
        ),
    )(input)
    .map_err(|error| match error {
        Err::Error(parsing) | Err::Failure(parsing) => parsing.message.clone(),
        Err::Incomplete(_) => "incomplete declaration data".to_string(),
    })?;

    if !rest.iter().all(|byte| byte.is_ascii_whitespace()) {
        return Err(format!(
            "unexpected trailing text '{}' after END_VAR",
            preview(rest)
        ));
    }

    let mut variables = Vec::new();
    for (names, data_type) in parsed.into_iter().flatten() {
        for name in names {
            variables.push(VarDecl {
                name,
                base: data_type.base(),
                elements: data_type.elements(),
                bytes: data_type.base().bytes() * data_type.elements(),
            });
        }
    }
    Ok(variables)
}

/// IEC type keywords this receiver cannot map to a wire width; named in the
/// failure message instead of surfacing a generic nom error.
const UNSUPPORTED_TYPES: &[&str] = &[
    "STRING",
    "WSTRING",
    "TIME",
    "TIME_OF_DAY",
    "TOD",
    "DATE",
    "DATE_AND_TIME",
    "DT",
];

/// One declaration or one comment between declarations.
fn item(input: &[u8]) -> DeclResult<'_, Option<(Vec<String>, DeclType)>> {
    let (input, _) = multispace0(input)?;
    alt((
        map(line_comment, |_| None),
        map(block_comment, |_| None),
        map(declaration, Some),
    ))(input)
}

/// `name [, name ...] : TYPE;`
fn declaration(input: &[u8]) -> DeclResult<'_, (Vec<String>, DeclType)> {
    map(
        tuple((
            separated_list1(delimited(multispace0, char(','), multispace0), identifier),
            preceded(multispace0, char(':')),
            preceded(multispace0, decl_type),
            terminated(multispace0, char(';')),
        )),
        |(names, _, data_type, _)| (names, data_type),
    )(input)
}

/// `REAL`, `ARRAY[0..4] OF REAL`, ...
fn decl_type(input: &[u8]) -> DeclResult<'_, DeclType> {
    let (input, name) = identifier(input)?;
    let upper_name = name.to_ascii_uppercase();
    if upper_name == "ARRAY" {
        let (input, _) = multispace0(input)?;
        let (input, elements) = array_dimensions(input)?;
        let (input, _) = multispace0(input)?;
        let (input, _) = tag_no_case("OF")(input)?;
        let (input, _) = multispace1(input)?;
        let (input, base) = base_type(input)?;
        Ok((input, DeclType::Array(base, elements)))
    } else if let Some(base) = IecBase::from_keyword(&upper_name) {
        Ok((input, DeclType::Base(base)))
    } else if UNSUPPORTED_TYPES.contains(&upper_name.as_str()) {
        Err(Err::Failure(DeclError {
            message: format!("unsupported declaration type {upper_name}"),
        }))
    } else {
        Err(Err::Failure(DeclError {
            message: format!("unknown declaration type {upper_name}"),
        }))
    }
}

/// `[start..end]`, producing the element count `end - start + 1`.
fn array_dimensions(input: &[u8]) -> DeclResult<'_, u32> {
    let (input, (start, end)) = delimited(
        pair(char('['), multispace0),
        pair(terminated(unsigned, tag_no_case("..")), unsigned),
        pair(multispace0, char(']')),
    )(input)?;
    match end.checked_sub(start).and_then(|span| span.checked_add(1)) {
        Some(elements) => Ok((input, elements)),
        None => Err(Err::Failure(DeclError {
            message: format!("empty array dimensions {start}..{end}"),
        })),
    }
}

/// A base type keyword after `ARRAY ... OF` or for a plain declaration.
fn base_type(input: &[u8]) -> DeclResult<'_, IecBase> {
    let (input, name) = identifier(input)?;
    let upper_name = name.to_ascii_uppercase();
    match IecBase::from_keyword(&upper_name) {
        Some(base) => Ok((input, base)),
        None => Err(Err::Failure(DeclError {
            message: format!("unsupported element type {upper_name} in array"),
        })),
    }
}

/// CODESYS variable or type identifier: letters, digits, underscores and `$`.
fn identifier(input: &[u8]) -> DeclResult<'_, String> {
    map(
        take_while1(|byte: u8| byte.is_ascii_alphanumeric() || byte == b'_' || byte == b'$'),
        |name| String::from_utf8_lossy(name).into_owned(),
    )(input)
}

/// `// ...` comment, up to (not including) the end of the line.
fn line_comment(input: &[u8]) -> DeclResult<'_, ()> {
    let (input, _) = tag("//")(input)?;
    let (input, _) = take_while(|byte: u8| byte != b'\n')(input)?;
    Ok((input, ()))
}

/// `(* ... *)` comment, spanning any content up to (not including) the `*)`.
fn block_comment(input: &[u8]) -> DeclResult<'_, ()> {
    let (input, _) = tag("(*")(input)?;
    let (input, _) = take_until("*)")(input)?;
    let (input, _) = tag("*)")(input)?;
    Ok((input, ()))
}

/// An unsigned decimal number used in array bounds.
fn unsigned(input: &[u8]) -> DeclResult<'_, u32> {
    map_res(digit1, |digits| {
        std::str::from_utf8(digits).unwrap_or("0").parse::<u32>()
    })(input)
}

/// Last few bytes of undeclared input.
fn preview(rest: &[u8]) -> String {
    if rest.len() > 40 {
        String::from_utf8_lossy(&rest[..40]).into_owned() + "..."
    } else {
        String::from_utf8_lossy(rest).into_owned()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn var(name: &str, base: IecBase, elements: u32) -> VarDecl {
        VarDecl {
            name: name.to_string(),
            base,
            elements,
            bytes: base.bytes() * elements,
        }
    }

    #[test]
    fn declarations_parse_names_types_and_sizes() {
        let declarations =
            parse_var_declarations("VAR_GLOBAL sinus, cosine : REAL; some_word : WORD; END_VAR")
                .unwrap();
        assert_eq!(
            declarations,
            vec![
                var("sinus", IecBase::Real, 1),
                var("cosine", IecBase::Real, 1),
                var("some_word", IecBase::Word, 1),
            ]
        );
    }

    #[test]
    fn array_declaration_counts_elements() {
        let declarations =
            parse_var_declarations("VAR_GLOBAL my_array: ARRAY[0..4] OF INT; END_VAR").unwrap();
        assert_eq!(declarations, vec![var("my_array", IecBase::Int, 5)]);
    }

    #[test]
    fn comments_between_declarations_are_skipped() {
        let declarations = parse_var_declarations(
            "VAR_GLOBAL (* a comment *) value : REAL; // line comment\n meds : DINT; END_VAR",
        )
        .unwrap();
        assert_eq!(
            declarations,
            vec![
                var("value", IecBase::Real, 1),
                var("meds", IecBase::DInt, 1)
            ]
        );
    }

    #[test]
    fn unsupported_types_fail_with_the_type_named() {
        let error = parse_var_declarations("VAR_GLOBAL s : STRING(20); END_VAR")
            .expect_err("STRING should be rejected");
        assert!(
            error.contains("unsupported declaration type STRING"),
            "{error}"
        );
    }

    #[test]
    fn string_parse_rejects_garbage_after_end_var() {
        let error = parse_var_declarations("VAR_GLOBAL a : REAL; END_VAR etc")
            .expect_err("trailing text should be rejected");
        assert!(error.contains("unexpected trailing text"), "{error}");
    }

    #[test]
    fn declaration_derives_pack_identity_and_counts() {
        let text = "VAR_GLOBAL
// FOX_05_41_1
FOX_05_41_1_CellVoltage_000 : INT;
FOX_05_41_1_CellVoltage_001 : INT;
FOX_05_41_1_CellTemperature_000 : INT;
END_VAR";
        let spec = parse_declaration(text).unwrap();
        assert_eq!(spec.pack, "41-1");
        assert_eq!(spec.list_id, 411);
        assert_eq!(spec.voltage_count, 2);
        assert_eq!(spec.temperature_count, 1);
        assert_eq!(spec.declared_bytes, 6);
        assert!(spec.validate("sample").is_ok());
    }

    #[test]
    fn for_list_id_renames_the_pack_segment_only() {
        let template = parse_declaration(
            "VAR_GLOBAL
FOX_05_41_1_CellVoltage_000 : INT;
FOX_05_41_1_CellTemperature_000 : INT;
END_VAR",
        )
        .unwrap();
        let spec = template.for_list_id(463).unwrap();
        assert_eq!(spec.pack, "46-3");
        assert_eq!(spec.list_id, 463);
        assert_eq!(spec.prefix, "FOX_05_46_3");
        assert_eq!(spec.declarations[0].name, "FOX_05_46_3_CellVoltage_000");
        assert_eq!(spec.declarations[1].name, "FOX_05_46_3_CellTemperature_000");
        assert_eq!(spec.declared_bytes, template.declared_bytes);
        assert!(spec.validate("sample").is_ok());
    }

    #[test]
    fn validate_rejects_more_than_a_full_pack() {
        let variables = (0..=VOLTAGES_PER_PACK)
            .map(|index| {
                var(
                    &format!("FOX_05_41_1_CellVoltage_{index:03}"),
                    IecBase::Int,
                    1,
                )
            })
            .collect();
        let spec = PackSpec {
            pack: "41-1",
            list_id: 411,
            prefix: "FOX_05_41_1".to_string(),
            declarations: variables,
            voltage_count: VOLTAGES_PER_PACK + 1,
            temperature_count: 0,
            declared_bytes: (VOLTAGES_PER_PACK as u32 + 1) * 2,
        };
        let error = spec.validate("sample").unwrap_err();
        assert!(error.to_string().contains("more than"), "{error}");
    }

    #[test]
    fn validate_rejects_unexpected_variables() {
        let spec = PackSpec {
            pack: "41-1",
            list_id: 411,
            prefix: "FOX_05_41_1".to_string(),
            declarations: vec![
                var("FOX_05_41_1_CellVoltage_000", IecBase::Int, 1),
                var("other", IecBase::Int, 1),
            ],
            voltage_count: 1,
            temperature_count: 0,
            declared_bytes: 4,
        };
        let error = spec.validate("sample").unwrap_err();
        assert!(error.to_string().contains("only 1"), "{error}");
    }

    fn cell_template(names: &[&str], cell_type: &str) -> String {
        let body: String = names
            .iter()
            .map(|name| format!("FOX_05_41_1_{name} : {cell_type};\n"))
            .collect();
        format!("VAR_GLOBAL\n{body}END_VAR")
    }

    #[test]
    fn validate_rejects_interleaved_voltages_and_temperatures() {
        let text = cell_template(
            &["CellVoltage_000", "CellTemperature_000", "CellVoltage_001"],
            "INT",
        );
        let error = parse_declaration(&text)
            .unwrap()
            .validate("sample")
            .unwrap_err();
        assert!(error.to_string().contains("CellTemperature_000"), "{error}");
    }

    #[test]
    fn validate_rejects_gaps_and_reordered_indices() {
        for names in [
            ["CellVoltage_000", "CellVoltage_002", "CellTemperature_000"],
            ["CellVoltage_001", "CellVoltage_000", "CellTemperature_000"],
            ["CellVoltage_000", "CellVoltage_001", "CellTemperature_001"],
        ] {
            let spec = parse_declaration(&cell_template(&names, "INT")).unwrap();
            assert!(
                spec.validate("sample").is_err(),
                "{names:?} should be rejected"
            );
        }
    }

    #[test]
    fn validate_rejects_cells_that_are_not_scalar_ints() {
        for cell_type in ["UINT", "WORD", "REAL", "ARRAY[0..1] OF INT"] {
            let text = cell_template(&["CellVoltage_000", "CellTemperature_000"], cell_type);
            let error = parse_declaration(&text)
                .unwrap()
                .validate("sample")
                .unwrap_err();
            assert!(
                error.to_string().contains("scalar INTs"),
                "{cell_type}: {error}"
            );
        }
    }

    #[test]
    fn validate_accepts_the_shipped_declaration() {
        let path = "spec/KEB6_FOX_05_41_1_NVL_Declaration.txt";
        load_declaration(path).unwrap().validate(path).unwrap();
    }
}
