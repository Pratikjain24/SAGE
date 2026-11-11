#!/usr/bin/env python3
"""
compile_paper.py — Automated LaTeX Verification & Compilation Engine for SAGE.

Verifies:
1. All `\input{...}` file paths resolve to existing files.
2. All `\label{...}` and `\ref{...}` cross-references resolve cleanly.
3. All `\cite{...}` citation keys match entries in references.bib.
4. Compiles both `paper/main.tex` (extended report) and `paper/main_ieee6page.tex` (conference version).
5. Confirms generation of valid PDF binaries.

Usage:
    python scripts/compile_paper.py
    python scripts/compile_paper.py --target main.tex
    python scripts/compile_paper.py --target main_ieee6page.tex
"""

from __future__ import annotations
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO_ROOT / "paper"
BIB_FILE = PAPER_DIR / "references.bib"


def find_latex_compiler() -> tuple[str, list[str]]:
    """Locate available LaTeX compiler (pdflatex or tectonic)."""
    # 1. Check system pdflatex
    pdflatex = shutil.which("pdflatex")
    if pdflatex:
        return "pdflatex", [pdflatex]

    # 2. Check local tectonic binary
    tectonic_paths = [
        shutil.which("tectonic"),
        r"C:\Users\kruti\Downloads\tectonic_bin\tectonic.exe",
        str(REPO_ROOT / "tools" / "tectonic.exe"),
    ]
    for tp in tectonic_paths:
        if tp and os.path.exists(tp):
            return "tectonic", [tp]

    raise RuntimeError(
        "No LaTeX engine detected (neither pdflatex nor tectonic found). "
        "Please ensure pdflatex or tectonic is in PATH."
    )


def verify_inputs_and_references(tex_path: Path) -> dict[str, any]:
    """Audit all \\input, \\ref, \\label, and \\cite entries in a LaTeX document."""
    if not tex_path.exists():
        raise FileNotFoundError(f"LaTeX document not found: {tex_path}")

    content = tex_path.read_text(encoding="utf-8")
    base_dir = tex_path.parent

    # Check and expand \\input statements
    inputs = re.findall(r'\\input\{([^}]+)\}', content)
    missing_inputs = []
    expanded_content = content

    for inp in inputs:
        inp_filename = inp if inp.endswith(".tex") else inp + ".tex"
        target_path = base_dir / inp_filename
        if not target_path.exists():
            missing_inputs.append(str(inp))
        else:
            try:
                child_text = target_path.read_text(encoding="utf-8")
                expanded_content += "\n" + child_text
            except Exception as e:
                missing_inputs.append(f"{inp} (error: {e})")

    # Match labels and refs
    labels = set(re.findall(r'\\label\{([^}]+)\}', expanded_content))
    labels.update(re.findall(r'label=\{([^}]+)\}', expanded_content))
    refs = set(re.findall(r'\\ref\{([^}]+)\}', expanded_content))
    missing_refs = refs - labels

    # Match citations
    cites = set()
    for c in re.findall(r'\\cite\{([^}]+)\}', expanded_content):
        for key in c.split(','):
            key = key.strip()
            if key:
                cites.add(key)

    bib_keys = set()
    if BIB_FILE.exists():
        bib_text = BIB_FILE.read_text(encoding="utf-8")
        bib_keys = set(re.findall(r'@[a-zA-Z]+\{([^,]+),', bib_text))
    missing_cites = cites - bib_keys

    result = {
        "file": tex_path.name,
        "inputs_count": len(inputs),
        "missing_inputs": missing_inputs,
        "labels_count": len(labels),
        "refs_count": len(refs),
        "missing_refs": list(missing_refs),
        "cites_count": len(cites),
        "missing_cites": list(missing_cites),
        "valid": len(missing_inputs) == 0 and len(missing_refs) == 0 and len(missing_cites) == 0,
    }
    return result


def compile_tex(tex_path: Path, compiler_type: str, compiler_cmd: list[str]) -> Path:
    """Compile a LaTeX document into PDF using the specified compiler."""
    print(f"\n[*] Compiling {tex_path.name} using {compiler_type}...")
    cwd = tex_path.parent

    if compiler_type == "pdflatex":
        base_name = tex_path.stem
        # Pass 1: pdflatex
        print("  - Pass 1/3: pdflatex...")
        subprocess.run(compiler_cmd + ["-interaction=nonstopmode", tex_path.name], cwd=cwd, check=True)
        # BibTeX
        bibtex = shutil.which("bibtex")
        if bibtex and (cwd / f"{base_name}.aux").exists():
            print("  - Running bibtex...")
            subprocess.run([bibtex, base_name], cwd=cwd, check=False)
        # Pass 2: pdflatex
        print("  - Pass 2/3: pdflatex...")
        subprocess.run(compiler_cmd + ["-interaction=nonstopmode", tex_path.name], cwd=cwd, check=True)
        # Pass 3: pdflatex
        print("  - Pass 3/3: pdflatex...")
        subprocess.run(compiler_cmd + ["-interaction=nonstopmode", tex_path.name], cwd=cwd, check=True)
    elif compiler_type == "tectonic":
        # Tectonic executes full multi-pass compilation and bibtex automatically
        cmd = compiler_cmd + ["--print", tex_path.name]
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"[!] Compilation error in {tex_path.name}:", file=sys.stderr)
            print(res.stderr[-1000:], file=sys.stderr)
            raise RuntimeError(f"Tectonic compilation failed with exit code {res.returncode}")

    pdf_path = cwd / f"{tex_path.stem}.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"Expected output PDF not generated: {pdf_path}")

    size_kb = pdf_path.stat().st_size / 1024
    print(f"[✓] Successfully compiled: {pdf_path.name} ({size_kb:.1f} KB)")
    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Audit and compile SAGE research paper LaTeX files.")
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Optional specific tex file to compile (e.g. main.tex or main_ieee6page.tex)",
    )
    args = parser.parse_args()

    targets = [args.target] if args.target else ["main.tex", "main_ieee6page.tex"]
    compiler_type, compiler_cmd = find_latex_compiler()
    print(f"[*] Detected LaTeX engine: {compiler_type} ({compiler_cmd[0]})")

    all_valid = True
    for t in targets:
        tex_path = PAPER_DIR / t
        audit = verify_inputs_and_references(tex_path)
        print(f"\n=======================================================")
        print(f"Audit for {audit['file']}:")
        print(f"  - Inputs: {audit['inputs_count']} found, {len(audit['missing_inputs'])} missing")
        if audit['missing_inputs']:
            print(f"    Missing inputs: {audit['missing_inputs']}")
        print(f"  - References: {audit['refs_count']} used, {audit['labels_count']} defined, {len(audit['missing_refs'])} missing")
        if audit['missing_refs']:
            print(f"    Missing refs: {audit['missing_refs']}")
        print(f"  - Citations: {audit['cites_count']} used, {len(audit['missing_cites'])} missing")
        if audit['missing_cites']:
            print(f"    Missing cites: {audit['missing_cites']}")

        if not audit["valid"]:
            print(f"[!] Audit failed for {t}!")
            all_valid = False
            continue

        print(f"[✓] All \\input{{}}, \\ref{{}}, and \\cite{{}} references 100% resolved!")
        compile_tex(tex_path, compiler_type, compiler_cmd)

    if not all_valid:
        sys.exit(1)

    print("\n=======================================================")
    print("✅ ALL SAGE MANUSCRIPTS SUCCESSFULLY AUDITED AND COMPILED!")
    print("=======================================================\n")


if __name__ == "__main__":
    main()

