#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keil C51 SBOM Generator for Zero-BSP 8051 Firmware
Target: Winbond / Nuvoton W78 Series Microcontrollers (e.g. W78E052D)

Extracts SBOM information from build evidence:
  - Keil Project (.uvproj)
  - Compiler / Assembler Listings (.lst)
  - Recursive Standard 8051 Header (#include <REG52.H>, <INTRINS.H>)
  - Linker Map (.m51) for implicitly linked C51S.LIB & internal modules
  - Keil TOOLS.INI and toolchain executable hashes
Outputs:
  - CycloneDX v1.5 JSON (sbom.cdx.json)
  - SPDX v2.3 JSON (sbom.spdx.json)
  - Markdown Audit Report (SBOM-REPORT.md)
"""

import os
import sys
import re
import json
import uuid
import hashlib
import datetime
import argparse
import configparser
import xml.etree.ElementTree as ET
from pathlib import Path


def compute_file_hashes(filepath: Path) -> dict:
    """Compute sha256, sha1, md5 for a file."""
    if not filepath or not filepath.is_file():
        return {}
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
            sha1.update(chunk)
            md5.update(chunk)
    return {
        "SHA-256": sha256.hexdigest(),
        "SHA-1": sha1.hexdigest(),
        "MD5": md5.hexdigest(),
    }


def find_keil_c51_root(custom_path: str = None) -> Path:
    """Locate Keil C51 root folder via argument, registry, or standard locations."""
    if custom_path and Path(custom_path).is_dir():
        return Path(custom_path).resolve()

    # Try Windows Registry
    if sys.platform == "win32":
        try:
            import winreg
            for root_key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                for subkey in (
                    r"SOFTWARE\WOW6432Node\Keil\Products\C51",
                    r"SOFTWARE\Keil\Products\C51",
                ):
                    try:
                        with winreg.OpenKey(root_key, subkey) as key:
                            val, _ = winreg.QueryValueEx(key, "Path")
                            if val and Path(val).is_dir():
                                return Path(val).resolve()
                    except OSError:
                        pass
        except ImportError:
            pass

    # Try typical paths
    candidates = [
        Path(r"C:\Users\tester\AppData\Local\Keil_v5\C51"),
        Path(r"C:\Keil_v5\C51"),
        Path(r"C:\Keil\C51"),
    ]
    for c in candidates:
        if c.is_dir():
            return c.resolve()

    return None


def parse_uvproj(uvproj_path: Path) -> dict:
    """Parse .uvproj XML file for target device, memory model, and source files."""
    if not uvproj_path.is_file():
        return {}

    tree = ET.parse(uvproj_path)
    root = tree.getroot()

    device_elem = root.find(".//TargetCommonOption/Device")
    vendor_elem = root.find(".//TargetCommonOption/Vendor")
    cpu_elem = root.find(".//TargetCommonOption/Cpu")
    output_elem = root.find(".//TargetCommonOption/OutputName")
    aftermake_elem = root.find(".//TargetCommonOption/AfterMake/RunUserProg1")
    aftermake_cmd = root.find(".//TargetCommonOption/AfterMake/UserProg1Name")

    files = []
    for f in root.findall(".//Files/File"):
        fname = f.find("FileName")
        fpath = f.find("FilePath")
        ftype = f.find("FileType")
        files.append({
            "name": fname.text if fname is not None else "",
            "path": fpath.text if fpath is not None else "",
            "type": ftype.text if ftype is not None else "0",
        })

    return {
        "device": device_elem.text if device_elem is not None else "8051",
        "vendor": vendor_elem.text if vendor_elem is not None else "Generic",
        "cpu": cpu_elem.text if cpu_elem is not None else "",
        "output_name": output_elem.text if output_elem is not None else "output",
        "aftermake_enabled": aftermake_elem.text == "1" if aftermake_elem is not None else False,
        "aftermake_cmd": aftermake_cmd.text if aftermake_cmd is not None else "",
        "files": files,
    }


def extract_header_comment(header_path: Path) -> str:
    """Extract copyright or descriptive header comment from a C header file."""
    if not header_path.is_file():
        return ""
    try:
        content = header_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

    match = re.search(r"/\*.*?\*/", content, re.DOTALL)
    if match:
        comment = match.group(0)
        lines = [line.strip().lstrip("/*").rstrip("*/").strip() for line in comment.splitlines()]
        cleaned = " ".join(line for line in lines if line)
        return cleaned[:200]
    return ""


def find_headers_recursively(source_file: Path, inc_dirs: list, visited: set = None) -> list:
    """Recursively find included headers from source and standard include dirs."""
    if visited is None:
        visited = set()

    if not source_file or not source_file.is_file():
        return []

    found = []
    include_pattern = re.compile(r'^\s*#include\s*[<"]([^>"]+)[>"]', re.MULTILINE)
    try:
        content = source_file.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    for match in include_pattern.finditer(content):
        header_name = match.group(1).strip()
        # Search in source file directory first, then inc_dirs
        search_dirs = [source_file.parent] + inc_dirs
        resolved = None
        for sdir in search_dirs:
            candidate = (sdir / header_name).resolve()
            if candidate.is_file():
                resolved = candidate
                break

        if resolved and str(resolved) not in visited:
            visited.add(str(resolved))
            hashes = compute_file_hashes(resolved)
            notice = extract_header_comment(resolved)
            found.append({
                "name": header_name,
                "path": str(resolved),
                "hashes": hashes,
                "notice": notice,
            })
            # Recursive search for nested includes
            nested = find_headers_recursively(resolved, inc_dirs, visited)
            found.extend(nested)

    return found


def parse_m51(m51_path: Path) -> dict:
    """Parse Keil BL51 .m51 linker map file for implicitly linked runtime libraries."""
    if not m51_path.is_file():
        return {}

    content = m51_path.read_text(encoding="utf-8", errors="ignore")
    
    # Extract BL51 version
    v_match = re.search(r"BL51.*?V([0-9\.]+)", content)
    bl51_version = f"V{v_match.group(1)}" if v_match else "Unknown"

    # Extract memory model
    mm_match = re.search(r"MEMORY MODEL:\s*(\w+)", content)
    memory_model = mm_match.group(1) if mm_match else "SMALL"

    # Extract INPUT MODULES INCLUDED
    input_modules = []
    in_section = False
    for line in content.splitlines():
        if "INPUT MODULES INCLUDED:" in line:
            in_section = True
            continue
        if in_section:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("LINK MAP OF MODULE:"):
                break
            # Example: C:\USERS\...\LIB\C51S.LIB (?C_INIT)
            mod_match = re.match(r"(.*?)\s*\((.*?)\)", stripped)
            if mod_match:
                fpath = mod_match.group(1).strip()
                mname = mod_match.group(2).strip()
                input_modules.append({"path": fpath, "module": mname})

    # Group libraries and user objects
    user_objects = []
    libraries = {}
    for item in input_modules:
        p = item["path"]
        m = item["module"]
        if p.upper().endswith(".LIB"):
            lib_path = Path(p).resolve()
            lib_key = str(lib_path)
            if lib_key not in libraries:
                libraries[lib_key] = {
                    "path": str(lib_path),
                    "name": lib_path.name,
                    "modules": [],
                    "hashes": compute_file_hashes(lib_path) if lib_path.is_file() else {},
                }
            libraries[lib_key]["modules"].append(m)
        else:
            user_objects.append({"path": p, "module": m})

    return {
        "bl51_version": bl51_version,
        "memory_model": memory_model,
        "libraries": list(libraries.values()),
        "user_objects": user_objects,
    }


def parse_lst_tool_versions(listings_dir: Path) -> dict:
    """Extract actual compiler and assembler versions from .lst files."""
    versions = {}
    if not listings_dir.is_dir():
        return versions

    for lst in listings_dir.glob("*.lst"):
        content = lst.read_text(encoding="utf-8", errors="ignore")
        c51_match = re.search(r"C51 COMPILER\s+V([0-9\.]+)", content)
        if c51_match:
            versions["C51.exe"] = f"V{c51_match.group(1)}"
        a51_match = re.search(r"(?:A51 MACRO ASSEMBLER|MACRO ASSEMBLER A51)\s+V([0-9\.]+)", content)
        if a51_match:
            versions["A51.exe"] = f"V{a51_match.group(1)}"
    return versions


def parse_tools_ini(keil_c51_path: Path) -> dict:
    """Parse Keil TOOLS.INI for suite version and tools information."""
    if not keil_c51_path:
        return {}
    tools_ini = keil_c51_path.parent / "TOOLS.INI"
    if not tools_ini.is_file():
        return {}

    suite_version = "V9.61"
    try:
        content = tools_ini.read_text(encoding="utf-8", errors="ignore")
        in_c51 = False
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                in_c51 = (line.upper() == "[C51]")
                continue
            if in_c51:
                match = re.match(r"^VERSION\s*=\s*(.+)$", line, re.IGNORECASE)
                if match:
                    suite_version = match.group(1).strip().strip('"').strip("'")
                    break
    except Exception:
        pass

    return {
        "suite_version": suite_version,
        "path": str(tools_ini),
    }


def generate_cyclonedx(metadata: dict, output_path: Path):
    """Generate CycloneDX v1.5 JSON SBOM."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    bom_uuid = f"urn:uuid:{uuid.uuid4()}"

    components = []
    dependencies = []
    root_ref = f"pkg:generic/firmware/{metadata['output_name']}@1.0.0"

    # Hardware Device Component
    dev_ref = f"pkg:hardware/mcu/{metadata['device'].lower()}@1.0.0"
    components.append({
        "type": "device",
        "bom-ref": dev_ref,
        "name": metadata["device"],
        "version": "1.0.0",
        "supplier": {"name": metadata["vendor"]},
        "description": f"Target 8051 Microcontroller: {metadata['device']} ({metadata['vendor']}), {metadata['cpu']}",
    })

    # Standard Headers
    header_refs = []
    for h in metadata["headers"]:
        href = f"pkg:file/header/{h['name']}@{h['hashes'].get('SHA-256', '')[:8]}"
        header_refs.append(href)
        components.append({
            "type": "file",
            "bom-ref": href,
            "name": h["name"],
            "version": "Keil C51 Standard Header",
            "description": h["notice"] or f"Standard 8051 header {h['name']}",
            "hashes": [{"alg": k.replace("-", ""), "content": v} for k, v in h["hashes"].items()],
            "properties": [{"name": "file:path", "value": h["path"]}],
        })

    # Implicitly Linked C51 Runtime Libraries
    lib_refs = []
    for lib in metadata["libraries"]:
        lref = f"pkg:library/keil/{lib['name'].lower()}@{lib['hashes'].get('SHA-256', '')[:8]}"
        lib_refs.append(lref)
        props = [{"name": "file:path", "value": lib["path"]}]
        for mod in lib["modules"]:
            props.append({"name": "keil:linked_module", "value": mod})
        components.append({
            "type": "library",
            "bom-ref": lref,
            "name": lib["name"],
            "version": metadata["suite_version"],
            "description": f"Keil C51 {metadata['memory_model']} Model Runtime Library (implicitly linked by BL51)",
            "hashes": [{"alg": k.replace("-", ""), "content": v} for k, v in lib["hashes"].items()],
            "properties": props,
        })

    # Source Files
    src_refs = []
    for src in metadata["source_files"]:
        sref = f"pkg:file/source/{src['name']}@{src['hashes'].get('SHA-256', '')[:8]}"
        src_refs.append(sref)
        components.append({
            "type": "file",
            "bom-ref": sref,
            "name": src["name"],
            "version": "1.0.0",
            "description": f"Firmware source file: {src['name']}",
            "hashes": [{"alg": k.replace("-", ""), "content": v} for k, v in src["hashes"].items()],
            "properties": [{"name": "file:path", "value": src["path"]}],
        })

    # Root Firmware dependency
    dependencies.append({
        "ref": root_ref,
        "dependsOn": [dev_ref] + lib_refs + src_refs + header_refs,
    })

    # Build tools metadata
    tool_components = []
    for tname, tinfo in metadata["tools"].items():
        tool_components.append({
            "type": "application",
            "name": tname,
            "version": tinfo["version"],
            "hashes": [{"alg": k.replace("-", ""), "content": v} for k, v in tinfo["hashes"].items()],
        })

    cdx = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": bom_uuid,
        "version": 1,
        "metadata": {
            "timestamp": now_iso,
            "tools": {
                "components": tool_components,
            },
            "component": {
                "type": "application",
                "bom-ref": root_ref,
                "name": metadata["output_name"],
                "version": "1.0.0",
                "description": f"Intel HEX Firmware for {metadata['device']} (Winbond / Nuvoton W78 series)",
                "hashes": [{"alg": k.replace("-", ""), "content": v} for k, v in metadata["hex_hashes"].items()],
            },
            "properties": [
                {"name": "keil:suite_version", "value": metadata["suite_version"]},
                {"name": "keil:memory_model", "value": metadata["memory_model"]},
                {"name": "bsp:status", "value": "None (Standard 8051 Bare-Metal)"},
            ],
        },
        "components": components,
        "dependencies": dependencies,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cdx, f, indent=2, ensure_ascii=False)


def generate_spdx(metadata: dict, output_path: Path):
    """Generate SPDX v2.3 JSON SBOM."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc_id = f"SPDXRef-DOCUMENT"
    doc_ns = f"https://spdx.org/spdxdocs/w78_std_8051-{uuid.uuid4()}"

    packages = []
    files = []
    relationships = []

    # Root HEX package
    root_spdx_id = "SPDXRef-Package-FirmwareHex"
    packages.append({
        "SPDXID": root_spdx_id,
        "name": f"{metadata['output_name']}.hex",
        "versionInfo": "1.0.0",
        "downloadLocation": "NOASSERTION",
        "filesAnalyzed": False,
        "checksums": [
            {"algorithm": "SHA256", "checksumValue": metadata["hex_hashes"].get("SHA-256", "")},
            {"algorithm": "MD5", "checksumValue": metadata["hex_hashes"].get("MD5", "")},
        ],
        "description": f"Target firmware image for {metadata['device']}",
    })
    relationships.append({
        "spdxElementId": doc_id,
        "relationshipType": "DESCRIBES",
        "relatedSpdxElement": root_spdx_id,
    })

    # Device hardware package
    dev_spdx_id = "SPDXRef-Package-MCU"
    packages.append({
        "SPDXID": dev_spdx_id,
        "name": metadata["device"],
        "versionInfo": "Standard 8051 Core",
        "downloadLocation": "NOASSERTION",
        "filesAnalyzed": False,
        "supplier": f"Organization: {metadata['vendor']}",
        "description": f"Microcontroller: {metadata['device']}, {metadata['cpu']}",
    })
    relationships.append({
        "spdxElementId": root_spdx_id,
        "relationshipType": "DEPENDS_ON",
        "relatedSpdxElement": dev_spdx_id,
    })

    # Implicitly linked C51S.LIB package
    for idx, lib in enumerate(metadata["libraries"]):
        lib_spdx_id = f"SPDXRef-Package-Lib-{idx}"
        packages.append({
            "SPDXID": lib_spdx_id,
            "name": lib["name"],
            "versionInfo": metadata["suite_version"],
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "supplier": "Organization: Keil / Arm",
            "checksums": [
                {"algorithm": "SHA256", "checksumValue": lib["hashes"].get("SHA-256", "")},
            ],
            "description": f"Keil C51 Runtime Library ({metadata['memory_model']} model), Modules: {', '.join(lib['modules'])}",
        })
        relationships.append({
            "spdxElementId": root_spdx_id,
            "relationshipType": "DEPENDS_ON",
            "relatedSpdxElement": lib_spdx_id,
        })

    # Header files
    for idx, h in enumerate(metadata["headers"]):
        fid = f"SPDXRef-File-Header-{idx}"
        files.append({
            "SPDXID": fid,
            "fileName": h["name"],
            "checksums": [
                {"algorithm": "SHA256", "checksumValue": h["hashes"].get("SHA-256", "")},
            ],
            "noticeText": h["notice"] or "Keil C51 Standard Header",
        })
        relationships.append({
            "spdxElementId": root_spdx_id,
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": fid,
        })

    # Source files
    for idx, s in enumerate(metadata["source_files"]):
        fid = f"SPDXRef-File-Source-{idx}"
        files.append({
            "SPDXID": fid,
            "fileName": s["name"],
            "checksums": [
                {"algorithm": "SHA256", "checksumValue": s["hashes"].get("SHA-256", "")},
            ],
        })
        relationships.append({
            "spdxElementId": root_spdx_id,
            "relationshipType": "CONTAINS",
            "relatedSpdxElement": fid,
        })

    spdx = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": doc_id,
        "name": metadata["output_name"],
        "documentNamespace": doc_ns,
        "creationInfo": {
            "created": now_iso,
            "creators": [
                "Tool: C51-SBOM-Generator-1.0",
                f"Tool: Keil C51-{metadata['suite_version']}",
            ],
        },
        "packages": packages,
        "files": files,
        "relationships": relationships,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spdx, f, indent=2, ensure_ascii=False)


def generate_markdown_report(metadata: dict, output_path: Path):
    """Generate human-readable Markdown Audit Report."""
    md = [
        f"# Software Bill of Materials (SBOM) Report",
        f"",
        f"**Project**: `{metadata['output_name']}`  ",
        f"**Target MCU**: `{metadata['device']}` ({metadata['vendor']})  ",
        f"**Architecture**: Standard 8051 / 8052 Core (Zero-BSP Bare Metal)  ",
        f"**Memory Model**: {metadata['memory_model']}  ",
        f"**Generated**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"",
        f"---",
        f"",
        f"## 1. Deliverable Firmware Image",
        f"",
        f"| Deliverable | File Path | SHA-256 Hash |",
        f"| :--- | :--- | :--- |",
        f"| **Intel HEX** | `{metadata['hex_path']}` | `{metadata['hex_hashes'].get('SHA-256', 'N/A')}` |",
        f"",
        f"## 2. Hardware Component (`device`)",
        f"",
        f"| Component | Vendor | Specs |",
        f"| :--- | :--- | :--- |",
        f"| **{metadata['device']}** | {metadata['vendor']} | {metadata['cpu']} |",
        f"",
        f"## 3. Implicitly Linked Keil Runtime Libraries (`library`)",
        f"",
        f"> **Notice**: Although this project uses no external BSP, the Keil BL51 Linker automatically links C51 runtime routines into the binary.",
        f"",
        f"| Library | Linked Internal Modules | SHA-256 Hash | Path |",
        f"| :--- | :--- | :--- | :--- |",
    ]

    for lib in metadata["libraries"]:
        mods = ", ".join(f"`{m}`" for m in lib["modules"])
        h256 = lib["hashes"].get("SHA-256", "N/A")
        md.append(f"| **{lib['name']}** | {mods} | `{h256}` | `{lib['path']}` |")

    md.extend([
        f"",
        f"## 4. Standard 8051 Header Files (`file`)",
        f"",
        f"| Header | Resolved Include Path | Copyright / Notice | SHA-256 Hash |",
        f"| :--- | :--- | :--- | :--- |",
    ])

    for h in metadata["headers"]:
        h256 = h["hashes"].get("SHA-256", "N/A")
        notice = h["notice"] or "Keil Standard Header"
        md.append(f"| **{h['name']}** | `{h['path']}` | {notice} | `{h256}` |")

    md.extend([
        f"",
        f"## 5. Application Source & Startup Code (`file`)",
        f"",
        f"| File Name | File Path | SHA-256 Hash |",
        f"| :--- | :--- | :--- |",
    ])

    for s in metadata["source_files"]:
        s256 = s["hashes"].get("SHA-256", "N/A")
        md.append(f"| **{s['name']}** | `{s['path']}` | `{s256}` |")

    md.extend([
        f"",
        f"## 6. Build Toolchain Provenance (`metadata.tools`)",
        f"",
        f"| Tool | Suite Release | Executable Version | SHA-256 Hash |",
        f"| :--- | :--- | :--- | :--- |",
    ])

    for tname, tinfo in metadata["tools"].items():
        thash = tinfo["hashes"].get("SHA-256", "N/A")
        md.append(f"| **{tname}** | {metadata['suite_version']} | {tinfo['version']} | `{thash}` |")

    md.append("")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))


def main():
    parser = argparse.ArgumentParser(description="Generate SBOM for Keil C51 8051 Projects")
    parser.add_argument("--project-dir", default="project", help="Path to Keil C51 project directory")
    parser.add_argument("--keil-path", default=None, help="Custom path to Keil C51 installation directory")
    parser.add_argument("--out-dir", default="sbom", help="Output directory for SBOM files")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    out_dir = Path(args.out_dir).resolve()

    # 1. Locate Keil C51
    keil_c51 = find_keil_c51_root(args.keil_path)
    if not keil_c51:
        print("[!] Warning: Keil C51 directory could not be located via registry or standard paths.")
    else:
        print(f"[*] Found Keil C51: {keil_c51}")

    # 2. Parse .uvproj
    uvproj_files = list(project_dir.glob("*.uvproj"))
    if not uvproj_files:
        print(f"[!] Error: No .uvproj file found in {project_dir}")
        sys.exit(1)
    uvproj_path = uvproj_files[0]
    proj_info = parse_uvproj(uvproj_path)
    print(f"[*] Target MCU: {proj_info.get('device')} ({proj_info.get('vendor')})")

    # 3. Parse .m51 Map File
    m51_files = list((project_dir / "Listings").glob("*.m51"))
    if not m51_files:
        m51_files = list(project_dir.glob("*.m51"))
    m51_info = parse_m51(m51_files[0]) if m51_files else {}

    # 4. Parse .lst for tool versions
    lst_versions = parse_lst_tool_versions(project_dir / "Listings")

    # 5. Parse TOOLS.INI
    tools_ini_info = parse_tools_ini(keil_c51)
    suite_version = tools_ini_info.get("suite_version", "V9.61")

    # 6. Resolve Toolchain Tools
    tools_dict = {}
    if keil_c51:
        bin_dir = keil_c51 / "BIN"
        tool_names = ["C51.exe", "A51.exe", "BL51.exe", "OH51.exe"]
        for tname in tool_names:
            tpath = bin_dir / tname
            if tpath.is_file():
                tversion = lst_versions.get(tname)
                if not tversion and tname == "BL51.exe":
                    tversion = m51_info.get("bl51_version")
                elif not tversion and tname == "OH51.exe":
                    try:
                        import subprocess
                        res = subprocess.run([str(tpath)], capture_output=True, text=True)
                        m = re.search(r"OH51\s+V([0-9\.]+)", res.stdout)
                        if m:
                            tversion = f"V{m.group(1)}"
                    except Exception:
                        pass
                if not tversion:
                    tversion = suite_version
                tools_dict[tname] = {
                    "path": str(tpath),
                    "version": tversion,
                    "hashes": compute_file_hashes(tpath),
                }

    # 7. Collect Source Files & Hashes
    source_files = []
    src_dir = project_dir / "src"
    if src_dir.is_dir():
        for sf in src_dir.iterdir():
            if sf.suffix.lower() in (".c", ".a51", ".asm", ".h"):
                source_files.append({
                    "name": sf.name,
                    "path": str(sf),
                    "hashes": compute_file_hashes(sf),
                })

    # 8. Recursively Resolve Headers
    inc_dirs = []
    if keil_c51 and (keil_c51 / "INC").is_dir():
        inc_dirs.append(keil_c51 / "INC")
        for sub in (keil_c51 / "INC").iterdir():
            if sub.is_dir():
                inc_dirs.append(sub)

    resolved_headers = []
    visited_headers = set()
    for s in source_files:
        h_list = find_headers_recursively(Path(s["path"]), inc_dirs, visited_headers)
        resolved_headers.extend(h_list)

    # 9. Deliverable HEX file
    hex_files = list((project_dir / "Objects").glob("*.hex"))
    if not hex_files:
        hex_files = list(project_dir.glob("*.hex"))
    hex_path = hex_files[0] if hex_files else None
    hex_hashes = compute_file_hashes(hex_path) if hex_path else {}

    # Compile Full Metadata
    full_metadata = {
        "output_name": proj_info.get("output_name", "w78_std_8051"),
        "device": proj_info.get("device", "W78E052D"),
        "vendor": proj_info.get("vendor", "Nuvoton"),
        "cpu": proj_info.get("cpu", ""),
        "suite_version": suite_version,
        "memory_model": m51_info.get("memory_model", "SMALL"),
        "hex_path": str(hex_path) if hex_path else "",
        "hex_hashes": hex_hashes,
        "libraries": m51_info.get("libraries", []),
        "headers": resolved_headers,
        "source_files": source_files,
        "tools": tools_dict,
    }

    # 10. Generate SBOM files
    cdx_path = out_dir / "sbom.cdx.json"
    spdx_path = out_dir / "sbom.spdx.json"
    md_path = out_dir / "SBOM-REPORT.md"

    generate_cyclonedx(full_metadata, cdx_path)
    print(f"[+] Generated CycloneDX 1.5 JSON: {cdx_path}")

    generate_spdx(full_metadata, spdx_path)
    print(f"[+] Generated SPDX 2.3 JSON:      {spdx_path}")

    generate_markdown_report(full_metadata, md_path)
    print(f"[+] Generated Markdown Report:   {md_path}")

    print("[*] SBOM Generation completed successfully.")


if __name__ == "__main__":
    main()
