# How-To: Configure Keil µVision to Automatically Generate SBOM on F7

This guide explains how to set up a Post-Build User Command in the Keil µVision IDE, enabling automatic SBOM generation whenever you build or rebuild the project (`F7`).

---

## When to Use

- When developing inside the Keil µVision GUI.
- To ensure that `sbom/` outputs always reflect the latest build without switching to a terminal.

---

## Step-by-Step Instructions

### Step 1: Open Target Options
1. Launch Keil µVision.
2. Open `project\w78_std_8051.uvproj`.
3. In the Project window, right-click `Target 1` and select **Options for Target 'Target 1'...** (or press `Alt + F7`).

### Step 2: Open the User Tab
1. In the Options dialog, switch to the **User** tab.
2. Locate the **After Build/Rebuild** section.

### Step 3: Configure User Program #1
1. Check the box for **Run #1**.
2. Enter the following command in the text field:
   ```text
   python ..\tools\generate_c51_sbom.py --project-dir .
   ```
   > **Path Note**: Keil executes user commands with the current working directory set to the project folder (`project\`). Therefore, `..\tools\generate_c51_sbom.py` correctly points to the script, and `--project-dir .` analyzes the current directory.
3. Click **OK** to save.

### Step 4: Verify the Build Hook
1. Press **F7** (Build Target).
2. Look at the **Build Output** console. After linking, you will see:
   ```text
   linking...
   Program Size: data=14.0 xdata=0 code=395
   creating hex file from ".\Objects\w78_std_8051"...
   ".\Objects\w78_std_8051" - 0 Error(s), 0 Warning(s).
   User command #1: python ..\tools\generate_c51_sbom.py --project-dir .
   [*] Found Keil C51: C:\Users\tester\AppData\Local\Keil_v5\C51
   [*] Target MCU: W78E052D (Nuvoton)
   [+] Generated CycloneDX 1.5 JSON: ...\sbom\sbom.cdx.json
   [+] Generated SPDX 2.3 JSON:      ...\sbom\sbom.spdx.json
   [+] Generated Markdown Report:   ...\sbom\SBOM-REPORT.md
   [*] SBOM Generation completed successfully.
   ```
3. Check the timestamps in `sbom/` to confirm the update.

---

## Troubleshooting

### Error: `'python' is not recognized as an internal or external command`
- Ensure Python is in your Windows `PATH`.
- Restart Keil µVision after modifying system environment variables.
- Alternatively, provide the absolute path to `python.exe` in the command field.
