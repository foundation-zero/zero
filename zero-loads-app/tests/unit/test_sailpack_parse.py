from sailpack.parse import parse_sailpack


def test_parse_sailpack_skips_tables_without_rows(tmp_path):
    file_path = tmp_path / "load_case.htm"
    file_path.write_text(
        """
        <html><body>
          <b>Calculation ID</b><i>test-calculation</i>
          <b>EMPTY TABLE</b>
          <table><tr><th>F (N)</th></tr></table>
          <b>CARS DATA</b>
          <table>
            <tr><th>F (N)</th></tr>
            <tr><td>123</td></tr>
          </table>
        </body></html>
        """,
        encoding="latin-1",
    )

    result = parse_sailpack(file_path)

    assert "EMPTY TABLE" not in result["table_description"].to_list()
    cars_data = result.filter(result["table_description"] == "CARS DATA")
    assert cars_data["F (N)"].to_list() == ["123"]
