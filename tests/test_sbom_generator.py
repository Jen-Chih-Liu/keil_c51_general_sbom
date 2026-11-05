#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated unit tests for Keil C51 SBOM Generator
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add project root and tools to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

import generate_c51_sbom


class TestC51SbomGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_dir = PROJECT_ROOT / "project"
        cls.sbom_dir = PROJECT_ROOT / "sbom"
        cls.keil_c51 = generate_c51_sbom.find_keil_c51_root()

    def test_01_keil_c51_detected(self):
        self.assertIsNotNone(self.keil_c51, "Keil C51 installation directory must be found")
        self.assertTrue(self.keil_c51.is_dir(), f"{self.keil_c51} must be an existing directory")
        self.assertTrue((self.keil_c51 / "BIN" / "C51.exe").is_file(), "C51.exe must exist")

    def test_02_parse_uvproj(self):
        uvproj_path = self.project_dir / "w78_std_8051.uvproj"
        self.assertTrue(uvproj_path.is_file(), "w78_std_8051.uvproj must exist")
        info = generate_c51_sbom.parse_uvproj(uvproj_path)
        self.assertEqual(info["device"], "W78E052D", "Device must be W78E052D")
        self.assertEqual(info["vendor"], "Nuvoton", "Vendor must be Nuvoton")
        self.assertTrue(info["aftermake_enabled"], "AfterMake must be enabled")
        self.assertIn("generate_c51_sbom.py", info["aftermake_cmd"], "AfterMake must call generate_c51_sbom.py")

    def test_03_parse_m51_runtime_library(self):
        m51_path = self.project_dir / "Listings" / "w78_std_8051.m51"
        self.assertTrue(m51_path.is_file(), "w78_std_8051.m51 map file must exist")
        info = generate_c51_sbom.parse_m51(m51_path)
        self.assertEqual(info["memory_model"], "SMALL")
        self.assertIn("V6.22", info["bl51_version"])

        # Check libraries
        lib_names = [lib["name"] for lib in info["libraries"]]
        self.assertIn("C51S.LIB", lib_names, "Implicitly linked C51S.LIB must be detected in m51")

        c51s_lib = next(l for l in info["libraries"] if l["name"] == "C51S.LIB")
        self.assertIn("?C_INIT", c51s_lib["modules"], "Module ?C_INIT must be present in C51S.LIB")
        self.assertIn("?C?UIDIV", c51s_lib["modules"], "Module ?C?UIDIV must be present in C51S.LIB")

        # Check startup object is distinguished
        user_modules = [m["module"] for m in info["user_objects"]]
        self.assertIn("?C_STARTUP", user_modules, "Startup module must come from user STARTUP.OBJ")

    def test_04_header_recursive_resolution(self):
        main_c = self.project_dir / "src" / "main.c"
        self.assertTrue(main_c.is_file(), "main.c must exist")
        inc_dirs = [self.keil_c51 / "INC"]
        headers = generate_c51_sbom.find_headers_recursively(main_c, inc_dirs)
        header_names = [h["name"] for h in headers]
        self.assertIn("REG52.H", header_names, "Standard REG52.H must be resolved")
        self.assertIn("INTRINS.H", header_names, "Standard INTRINS.H must be resolved")

        for h in headers:
            self.assertIn("SHA-256", h["hashes"])
            self.assertEqual(len(h["hashes"]["SHA-256"]), 64)

    def test_05_tools_ini_and_dual_versions(self):
        tools_info = generate_c51_sbom.parse_tools_ini(self.keil_c51)
        self.assertEqual(tools_info.get("suite_version"), "V9.61", "TOOLS.INI suite version should be V9.61")

        lst_versions = generate_c51_sbom.parse_lst_tool_versions(self.project_dir / "Listings")
        self.assertIn("C51.exe", lst_versions)
        self.assertIn("V9.60", lst_versions["C51.exe"])
        self.assertIn("A51.exe", lst_versions)
        self.assertIn("V8.2", lst_versions["A51.exe"])

    def test_06_cyclonedx_sbom_format(self):
        cdx_file = self.sbom_dir / "sbom.cdx.json"
        self.assertTrue(cdx_file.is_file(), "sbom.cdx.json must exist")
        with open(cdx_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("bomFormat"), "CycloneDX")
        self.assertEqual(data.get("specVersion"), "1.5")
        self.assertIn("metadata", data)
        self.assertIn("components", data)
        self.assertIn("dependencies", data)

        comp_types = [c["type"] for c in data["components"]]
        self.assertIn("device", comp_types, "Must contain device component (W78E052D)")
        self.assertIn("library", comp_types, "Must contain library component (C51S.LIB)")
        self.assertIn("file", comp_types, "Must contain file components (REG52.H, main.c)")

        # Verify device
        dev = next(c for c in data["components"] if c["type"] == "device")
        self.assertEqual(dev["name"], "W78E052D")

        # Verify C51S.LIB properties
        lib = next(c for c in data["components"] if c["name"] == "C51S.LIB")
        mod_props = [p["value"] for p in lib.get("properties", []) if p["name"] == "keil:linked_module"]
        self.assertIn("?C_INIT", mod_props)
        self.assertIn("?C?UIDIV", mod_props)

    def test_07_spdx_sbom_format(self):
        spdx_file = self.sbom_dir / "sbom.spdx.json"
        self.assertTrue(spdx_file.is_file(), "sbom.spdx.json must exist")
        with open(spdx_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data.get("spdxVersion"), "SPDX-2.3")
        self.assertEqual(data.get("dataLicense"), "CC0-1.0")
        self.assertIn("packages", data)
        self.assertIn("files", data)
        self.assertIn("relationships", data)

    def test_08_markdown_report_content(self):
        report_file = self.sbom_dir / "SBOM-REPORT.md"
        self.assertTrue(report_file.is_file(), "SBOM-REPORT.md must exist")
        text = report_file.read_text(encoding="utf-8")

        self.assertIn("W78E052D", text)
        self.assertIn("C51S.LIB", text)
        self.assertIn("?C_INIT", text)
        self.assertIn("?C?UIDIV", text)
        self.assertIn("REG52.H", text)
        self.assertIn("V9.61", text)
        self.assertIn("V9.60.7.0", text)


if __name__ == "__main__":
    unittest.main()
