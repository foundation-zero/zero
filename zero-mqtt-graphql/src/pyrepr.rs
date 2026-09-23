//! Python's `repr()` of the values a client can send, which the producer's
//! validation errors embed (pydantic's `input_value=...`, model reprs) - ported
//! so a rejection reads exactly as the producer's API words it.

/// Python's `repr(float)`: the shortest round-tripping digits, fixed notation
/// for decimal exponents in `-4..16` (always with a fractional part), else
/// scientific with a signed, at least two-digit exponent.
pub fn float_repr(x: f64) -> String {
    if x.is_nan() {
        return "nan".into();
    }
    if x.is_infinite() {
        return if x > 0.0 { "inf" } else { "-inf" }.into();
    }
    let sci = format!("{:e}", x.abs());
    let (mantissa, exponent) = sci.split_once('e').unwrap_or((&sci, "0"));
    let exponent: i32 = exponent.parse().unwrap_or(0);
    let digits: String = mantissa.chars().filter(char::is_ascii_digit).collect();
    let sign = if x.is_sign_negative() { "-" } else { "" };
    if (-4..16).contains(&exponent) {
        let body = if exponent >= 0 {
            let split = exponent as usize + 1;
            let padded = format!("{digits:0<split$}");
            let (int_part, frac_part) = padded.split_at(split);
            let frac_part = if frac_part.is_empty() { "0" } else { frac_part };
            format!("{int_part}.{frac_part}")
        } else {
            format!("0.{}{digits}", "0".repeat((-exponent - 1) as usize))
        };
        format!("{sign}{body}")
    } else {
        let (first, rest) = digits.split_at(1);
        let mantissa = if rest.is_empty() {
            first.to_string()
        } else {
            format!("{first}.{rest}")
        };
        let exponent_sign = if exponent < 0 { '-' } else { '+' };
        format!("{sign}{mantissa}e{exponent_sign}{:02}", exponent.abs())
    }
}

/// Whether Python's `str.isprintable()` holds for `c`: everything except the
/// control, format, separator (other than the space), private-use and
/// surrogate categories. Unassigned code points (also non-printable in
/// Python) are not tracked.
fn is_printable(c: char) -> bool {
    let code = c as u32;
    !matches!(code,
        0x00..=0x1F | 0x7F..=0xA0 | 0xAD | 0x034F | 0x061C | 0x115F..=0x1160
        | 0x1680 | 0x180E | 0x2000..=0x200F | 0x2028..=0x202F | 0x205F..=0x206F
        | 0x3000 | 0x3164 | 0xD800..=0xF8FF | 0xFE00..=0xFE0F | 0xFEFF | 0xFFA0
        | 0xFFF0..=0xFFFB | 0xE0000..=0xE0FFF | 0xF0000..=0x10FFFF)
}

/// Python's `repr(str)`: single-quoted unless the string holds a single quote
/// and no double quote, with Python's escapes.
pub fn str_repr(s: &str) -> String {
    let quote = if s.contains('\'') && !s.contains('"') {
        '"'
    } else {
        '\''
    };
    let mut out = String::with_capacity(s.len() + 2);
    out.push(quote);
    for c in s.chars() {
        match c {
            '\\' => out.push_str("\\\\"),
            '\t' => out.push_str("\\t"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            c if c == quote => {
                out.push('\\');
                out.push(c);
            }
            c if c == ' ' || (c.is_ascii() && !c.is_ascii_control()) => out.push(c),
            c if !c.is_ascii() && is_printable(c) => out.push(c),
            c if (c as u32) <= 0xFF => out.push_str(&format!("\\x{:02x}", c as u32)),
            c if (c as u32) <= 0xFFFF => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push_str(&format!("\\U{:08x}", c as u32)),
        }
    }
    out.push(quote);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_float_repr_matches_python() {
        let cases = [
            (25.0, "25.0"),
            (-300.0, "-300.0"),
            (0.001, "0.001"),
            (1e-5, "1e-05"),
            (1.5e-7, "1.5e-07"),
            (1e16, "1e+16"),
            (123456789.125, "123456789.125"),
            (0.1, "0.1"),
            (-0.0, "-0.0"),
            (1e15, "1000000000000000.0"),
            (2.5e20, "2.5e+20"),
            (f64::INFINITY, "inf"),
        ];
        for (x, expected) in cases {
            assert_eq!(float_repr(x), expected, "{x}");
        }
    }

    #[test]
    fn test_str_repr_quotes_and_escapes_like_python() {
        assert_eq!(str_repr("abc"), "'abc'");
        assert_eq!(str_repr("it's"), "\"it's\"");
        assert_eq!(str_repr("a'b\"c"), "'a\\'b\"c'");
        assert_eq!(str_repr("x\ny\t\\"), "'x\\ny\\t\\\\'");
        assert_eq!(str_repr("\u{1}é"), "'\\x01é'");
    }
}
