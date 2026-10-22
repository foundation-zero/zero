import subprocess
import sys

DEV_ONLY_MODULES = ["polars", "pyarrow", "pandas", "matplotlib", "seaborn", "bs4"]


def test_cli_imports_without_dev_dependencies():
    blocked = "; ".join(f"sys.modules['{name}'] = None" for name in DEV_ONLY_MODULES)
    result = subprocess.run(
        [sys.executable, "-c", f"import sys; {blocked}; import loads.cli"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
