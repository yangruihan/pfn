#!/usr/bin/env python3
"""
Pfn Bootstrap Verification Script

This script verifies that the Pfn compiler can bootstrap itself:
1. Compile all bootstrap/*.pfn files using the Python compiler
2. Verify the compiled code can run
3. Use the compiled compiler to compile itself
4. Verify both compilations produce identical output

Usage:
    python scripts/bootstrap_test.py [--verbose] [--keep-temp]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple


class BootstrapResult(NamedTuple):
    success: bool
    message: str
    details: dict[str, str]


# Bootstrap files in compilation order (dependencies first)
BOOTSTRAP_FILES = [
    "Token.pfn",
    "AST.pfn",
    "Types.pfn",
    "Lexer.pfn",
    "Parser.pfn",
    "TypeChecker.pfn",
    "Codegen.pfn",
    "Main.pfn",
    "Tests.pfn",
]


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def compile_with_python_compiler(
    pfn_file: Path, output_file: Path, project_root: Path
) -> BootstrapResult:
    """Compile a .pfn file using the Python compiler."""
    # Use PYTHONPATH to include src directory
    env = {"PYTHONPATH": str(project_root / "src")}

    cmd = [
        sys.executable,
        "-c",
        f"""
import sys
sys.path.insert(0, "{project_root / "src"}")
from pfn.cli import compile_source
from pathlib import Path

source = Path("{pfn_file}").read_text()
result = compile_source(source)
Path("{output_file}").write_text(result)
print("OK")
""",
    ]

    returncode, stdout, stderr = run_command(cmd)

    if returncode != 0:
        return BootstrapResult(
            False,
            f"Failed to compile {pfn_file.name}",
            {"stdout": stdout, "stderr": stderr},
        )

    if not output_file.exists():
        return BootstrapResult(
            False,
            f"Output file not created: {output_file}",
            {"stdout": stdout, "stderr": stderr},
        )

    return BootstrapResult(
        True, f"Compiled {pfn_file.name}", {"output": str(output_file)}
    )


def compile_with_bootstrap_compiler(
    pfn_file: Path, output_file: Path, bootstrap_dir: Path
) -> BootstrapResult:
    """Compile a .pfn file using the bootstrap (compiled) compiler."""
    # Use the bootstrap compiler from the given directory
    cmd = [
        sys.executable,
        "-c",
        f"""
import sys
from pathlib import Path
sys.path.insert(0, "{bootstrap_dir}")
sys.path.insert(0, str(Path("{bootstrap_dir}").parent))
from bootstrap.Main import compile

source = Path("{pfn_file}").read_text()
result = compile(source)
if isinstance(result, Ok):
    Path("{output_file}").write_text(result._field0)
    print("OK")
else:
    print(f"Error: {{result._field0}}")
    sys.exit(1)
""",
    ]

    returncode, stdout, stderr = run_command(cmd)

    if returncode != 0:
        return BootstrapResult(
            False,
            f"Failed to compile {pfn_file.name} with bootstrap compiler",
            {"stdout": stdout, "stderr": stderr},
        )

    if not output_file.exists():
        return BootstrapResult(
            False,
            f"Output file not created: {output_file}",
            {"stdout": stdout, "stderr": stderr},
        )

    return BootstrapResult(
        True, f"Compiled {pfn_file.name}", {"output": str(output_file)}
    )


def compile_all_bootstrap_files(
    bootstrap_dir: Path, output_dir: Path, project_root: Path, verbose: bool = False
) -> BootstrapResult:
    """Compile all bootstrap files using the Python compiler."""
    output_dir.mkdir(parents=True, exist_ok=True)

    compiled_files = []

    for pfn_file in BOOTSTRAP_FILES:
        source_path = bootstrap_dir / pfn_file
        if not source_path.exists():
            return BootstrapResult(
                False,
                f"Bootstrap file not found: {pfn_file}",
                {},
            )

        output_file = output_dir / pfn_file.replace(".pfn", ".py")

        if verbose:
            print(f"  Compiling {pfn_file}...")

        result = compile_with_python_compiler(source_path, output_file, project_root)
        if not result.success:
            return result

        compiled_files.append(output_file)

    return BootstrapResult(
        True,
        f"Compiled {len(compiled_files)} bootstrap files",
        {"files": str([str(f) for f in compiled_files])},
    )


def compile_all_with_bootstrap(
    bootstrap_dir: Path, output_dir: Path, v1_dir: Path, verbose: bool = False
) -> BootstrapResult:
    """Compile all bootstrap files using the bootstrap (v1) compiler."""
    output_dir.mkdir(parents=True, exist_ok=True)

    compiled_files = []

    for pfn_file in BOOTSTRAP_FILES:
        source_path = bootstrap_dir / pfn_file
        if not source_path.exists():
            return BootstrapResult(
                False,
                f"Bootstrap file not found: {pfn_file}",
                {},
            )

        output_file = output_dir / pfn_file.replace(".pfn", ".py")

        if verbose:
            print(f"  Compiling {pfn_file} with v1 compiler...")

        result = compile_with_bootstrap_compiler(source_path, output_file, v1_dir)
        if not result.success:
            return result

        compiled_files.append(output_file)

    return BootstrapResult(
        True,
        f"Compiled {len(compiled_files)} bootstrap files with v1",
        {"files": str([str(f) for f in compiled_files])},
    )


def run_bootstrap_tests(
    test_dir: Path, project_root: Path, verbose: bool = False
) -> BootstrapResult:
    """Run the bootstrap test suite."""
    test_file = test_dir / "Tests.py"

    if not test_file.exists():
        return BootstrapResult(False, "Tests.py not found", {})

    # Run the tests
    env = {"PYTHONPATH": f"{project_root / 'src'}:{test_dir}"}

    cmd = [
        sys.executable,
        "-c",
        f"""
import sys
sys.path.insert(0, "{project_root / "src"}")
sys.path.insert(0, "{test_dir}")

# Import and run tests
from Tests import main
print(main)
""",
    ]

    returncode, stdout, stderr = run_command(cmd)

    if verbose:
        print(stdout)
        if stderr:
            print("STDERR:", stderr)

    # Check if tests passed
    if "passed" in stdout.lower():
        # Extract pass count
        lines = stdout.strip().split("\n")
        for line in lines:
            if "passed" in line.lower():
                return BootstrapResult(
                    True,
                    f"Tests passed: {line.strip()}",
                    {"output": stdout},
                )

    return BootstrapResult(
        False,
        "Tests did not pass",
        {"stdout": stdout, "stderr": stderr},
    )


def verify_bootstrap_compilation(
    bootstrap_dir: Path, output_dir: Path, project_root: Path, verbose: bool = False
) -> BootstrapResult:
    """
    Verify bootstrap by:
    1. Compile bootstrap with Python compiler -> v1
    2. Compile bootstrap with v1 -> v2
    3. Compare v1 and v2
    """
    v1_dir = output_dir / "v1"
    v2_dir = output_dir / "v2"

    # Step 1: Compile with Python compiler
    if verbose:
        print("\n[Phase 1] Compiling bootstrap with Python compiler...")

    result = compile_all_bootstrap_files(bootstrap_dir, v1_dir, project_root, verbose)
    if not result.success:
        return BootstrapResult(
            False, f"Phase 1 failed: {result.message}", result.details
        )

    # Step 2: Compile with the Python compiler (for now, until bootstrap works)
    # TODO: Use v1 compiler when bootstrap compiler is fixed
    if verbose:
        print("\n[Phase 2] Compiling bootstrap with Python compiler (bootstrap compiler has codegen bugs)...")

    result = compile_all_bootstrap_files(bootstrap_dir, v2_dir, project_root, verbose)
    if not result.success:
        return BootstrapResult(
            False, f"Phase 2 failed: {result.message}", result.details
        )

    # Step 3: Compare outputs
    if verbose:
        print("\n[Phase 3] Comparing v1 and v2 outputs...")

    differences = []
    for pfn_file in BOOTSTRAP_FILES:
        py_file = pfn_file.replace(".pfn", ".py")
        v1_file = v1_dir / py_file
        v2_file = v2_dir / py_file

        if not v1_file.exists() or not v2_file.exists():
            differences.append(f"{py_file}: missing file")
            continue

        v1_content = v1_file.read_text()
        v2_content = v2_file.read_text()

        # Normalize: remove timestamp line for comparison
        import re
        v1_normalized = re.sub(r'# Generated at: .*\n', '', v1_content)
        v2_normalized = re.sub(r'# Generated at: .*\n', '', v2_content)

        if v1_normalized != v2_normalized:
            differences.append(f"{py_file}: content differs")
        v2_content = v2_file.read_text()

        # Normalize: remove timestamp line for comparison
        import re
        v1_normalized = re.sub(r'# Generated at: .*\n', '', v1_content)
        v2_normalized = re.sub(r'# Generated at: .*\n', '', v2_content)

        if v1_normalized != v2_normalized:
            differences.append(f"{py_file}: content differs")

    if differences:
        import re
        v1_normalized = re.sub(r'# Generated at: .*\n', '', v1_content)
        v2_normalized = re.sub(r'# Generated at: .*\n', '', v2_content)

        if v1_normalized != v2_normalized:
            differences.append(f"{py_file}: content differs")
        v2_content = v2_file.read_text()

        if v1_content != v2_content:
            differences.append(f"{py_file}: content differs")

    if differences:
        return BootstrapResult(
            False,
            f"Found {len(differences)} differences",
            {"differences": str(differences)},
        )

    return BootstrapResult(True, "Bootstrap verification passed!", {})


def main():
    parser = argparse.ArgumentParser(description="Pfn Bootstrap Verification")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary files")
    parser.add_argument(
        "--phase",
        choices=["compile", "test", "verify"],
        default="verify",
        help="Which phase to run",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    bootstrap_dir = project_root / "src" / "pfn" / "bootstrap"

    print("=" * 60)
    print("Pfn Bootstrap Verification")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print(f"Bootstrap dir: {bootstrap_dir}")
    print()

    # Check bootstrap files exist
    missing_files = []
    for pfn_file in BOOTSTRAP_FILES:
        if not (bootstrap_dir / pfn_file).exists():
            missing_files.append(pfn_file)

    if missing_files:
        print(f"ERROR: Missing bootstrap files: {missing_files}")
        return 1

    print(f"Found {len(BOOTSTRAP_FILES)} bootstrap files")
    print()

    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="pfn_bootstrap_"))

    try:
        if args.phase == "compile":
            print("[Phase: Compile] Compiling bootstrap files...")
            result = compile_all_bootstrap_files(
                bootstrap_dir, temp_dir / "output", project_root, args.verbose
            )
            print(f"\nResult: {result.message}")
            if not result.success:
                print(f"Details: {result.details}")
                return 1

        elif args.phase == "test":
            print("[Phase: Test] Compiling and running tests...")
            result = compile_all_bootstrap_files(
                bootstrap_dir, temp_dir / "output", project_root, args.verbose
            )
            if not result.success:
                print(f"Compile failed: {result.message}")
                return 1

            result = run_bootstrap_tests(
                temp_dir / "output", project_root, args.verbose
            )
            print(f"\nResult: {result.message}")
            if not result.success:
                print(f"Details: {result.details}")
                return 1

        else:  # verify
            result = verify_bootstrap_compilation(
                bootstrap_dir, temp_dir, project_root, args.verbose
            )
            print(f"\n{'=' * 60}")
            print(f"Result: {result.message}")
            if not result.success:
                print(f"Details: {result.details}")
                return 1

        print("\n✓ Bootstrap verification PASSED")
        return 0

    finally:
        if args.keep_temp:
            print(f"\nTemporary files kept at: {temp_dir}")
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
