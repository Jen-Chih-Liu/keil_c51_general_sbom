# How-To: Run Automated Verification Tests for the SBOM Generator

This guide explains how to run the test suite to verify that the SBOM extraction engine correctly parses Keil project files, listings, linker maps, headers, and toolchain versions.

---

## When to Use

- After modifying `tools/generate_c51_sbom.py`.
- During CI/CD quality gates.
- When porting to new Keil toolchain versions or different 8051 MCU targets.

---

## Running the Tests

Execute Python's built-in `unittest` runner from the repository root:

```powershell
python -m unittest discover -s tests
```

### Expected Output

```text
........
----------------------------------------------------------------------
Ran 8 tests in 0.025s

OK
```

---

## Test Suite Inventory

Tests are located in [`tests/test_sbom_generator.py`](file:///C:/Users/tester/Desktop/c51%20sbom/tests/test_sbom_generator.py):

| Test Method | Verification Target |
| :--- | :--- |
| `test_01_keil_c51_detected` | Confirms Keil C51 root directory and binaries are properly discovered. |
| `test_02_parse_uvproj` | Verifies `.uvproj` parsing for device name (`W78E052D`), vendor (`Nuvoton`), and AfterMake hook. |
| `test_03_parse_m51_runtime_library` | Confirms that `C51S.LIB` is discovered in `.m51`, internal modules (`?C_INIT`, `?C?UIDIV`) are tracked, and user `STARTUP.OBJ` is segregated. |
| `test_04_header_recursive_resolution` | Tests recursive resolution of `#include` directives against `C51\INC` and checks SHA-256 validity. |
| `test_05_tools_ini_and_dual_versions` | Tests dual-level version extraction: suite version `V9.61` from `TOOLS.INI` and executable versions (`C51.exe` V9.60.7.0, `A51.exe` V8.2.7.0). |
| `test_06_cyclonedx_sbom_format` | Validates CycloneDX 1.5 JSON compliance, component types (`device`, `library`, `file`), and dependency graphs. |
| `test_07_spdx_sbom_format` | Validates SPDX 2.3 JSON compliance, packages, files, and relationships. |
| `test_08_markdown_report_content` | Verifies Markdown report structure and required tables. |
