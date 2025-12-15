#!/usr/bin/env python3
"""
Validate ES module imports in TypeScript files.

This script checks that all relative imports include the .js extension,
which is required when compiling TypeScript to ES modules with NodeNext resolution.

Usage:
    python validate-esm-imports.py <directory>
    python validate-esm-imports.py src/

Checks for:
- Relative imports missing .js extensions
- Common ES module compatibility issues
- Special cases (helmet, etc.)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


class ESMImportValidator:
    """Validates ES module imports in TypeScript files."""

    # Pattern to match relative imports
    RELATIVE_IMPORT_PATTERN = r'''import\s+(?:(?:\{[^}]+\})|(?:\*\s+as\s+\w+)|(?:\w+))\s+from\s+['"](\.[^'"]+)['"]'''

    # Imports that should have .js extension
    NEEDS_JS_EXTENSION = re.compile(r'''^\.\.?/[^'"]+$''')

    # Special cases that might not need .js
    SPECIAL_CASES = {
        'helmet': 'Use: import * as helmetModule from "helmet"',
    }

    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.issues: List[Tuple[str, int, str, str]] = []
        self.warnings: List[Tuple[str, int, str, str]] = []

    def check_file(self, file_path: Path) -> None:
        """Check a single TypeScript file for import issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, start=1):
                # Find all relative imports in the line
                matches = re.finditer(self.RELATIVE_IMPORT_PATTERN, line)

                for match in matches:
                    import_path = match.group(1)

                    # Check if it's a relative import
                    if self.NEEDS_JS_EXTENSION.match(import_path):
                        # Check if it already has .js extension
                        if not import_path.endswith('.js'):
                            self.issues.append((
                                str(file_path.relative_to(self.directory)),
                                line_num,
                                f"Missing .js extension in import",
                                line.strip()
                            ))

                # Check for special cases
                for package, suggestion in self.SPECIAL_CASES.items():
                    if f'from "{package}"' in line or f"from '{package}'" in line:
                        if 'import * as' not in line:
                            self.warnings.append((
                                str(file_path.relative_to(self.directory)),
                                line_num,
                                f"Potential ES module issue with {package}",
                                suggestion
                            ))

        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

    def scan_directory(self) -> None:
        """Recursively scan directory for TypeScript files."""
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.ts') and not file.endswith('.d.ts'):
                    file_path = Path(root) / file
                    self.check_file(file_path)

    def print_report(self) -> None:
        """Print a formatted report of issues found."""
        has_issues = bool(self.issues or self.warnings)

        if not has_issues:
            print("✅ All ES module imports are correctly formatted!")
            print("\nAll relative imports have .js extensions.")
            return

        if self.issues:
            print(f"❌ Found {len(self.issues)} import issue(s) that MUST be fixed:\n")

            current_file = None
            for file_path, line_num, description, code in sorted(self.issues):
                if file_path != current_file:
                    print(f"\n📄 {file_path}")
                    current_file = file_path

                print(f"  Line {line_num}: {description}")
                print(f"    {code}")

        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} potential compatibility warning(s):\n")

            current_file = None
            for file_path, line_num, description, suggestion in sorted(self.warnings):
                if file_path != current_file:
                    print(f"\n📄 {file_path}")
                    current_file = file_path

                print(f"  Line {line_num}: {description}")
                print(f"    💡 {suggestion}")

        if self.issues:
            print("\n" + "=" * 80)
            print("🔧 How to fix:")
            print("=" * 80)
            print("""
1. Add .js extension to all relative imports:
   ❌ import { foo } from './utils'
   ✅ import { foo } from './utils.js'

   ❌ import { bar } from '../config/env'
   ✅ import { bar } from '../config/env.js'

2. Update tsconfig.json:
   {
     "compilerOptions": {
       "module": "NodeNext",
       "moduleResolution": "NodeNext"
     }
   }

3. For special packages like helmet:
   ❌ import helmet from 'helmet'
   ✅ import * as helmetModule from 'helmet'
      const helmet = (helmetModule as any).default || helmetModule

Note: You add .js even when importing .ts files. TypeScript will resolve correctly.
""")

    def run(self) -> int:
        """Run the validator and return exit code."""
        if not self.directory.exists():
            print(f"Error: Directory '{self.directory}' not found", file=sys.stderr)
            return 1

        print(f"Validating ES module imports in {self.directory}...\n")
        self.scan_directory()
        self.print_report()

        return 1 if self.issues else 0


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python validate-esm-imports.py <directory>")
        print("Example: python validate-esm-imports.py src/")
        return 1

    validator = ESMImportValidator(sys.argv[1])
    return validator.run()


if __name__ == '__main__':
    sys.exit(main())
