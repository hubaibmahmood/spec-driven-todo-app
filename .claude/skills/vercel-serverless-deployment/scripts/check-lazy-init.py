#!/usr/bin/env python3
"""
Check for module-level initialization that can cause serverless cold start issues.

This script scans TypeScript files for patterns that execute code at module load time,
which can cause FUNCTION_INVOCATION_FAILED errors on Vercel.

Usage:
    python check-lazy-init.py <directory>
    python check-lazy-init.py src/

Checks for:
- Module-level constant assignments with function calls
- Module-level class instantiations
- Module-level async operations
- Direct environment variable access at module level
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


class LazyInitChecker:
    """Checks TypeScript files for module-level initialization issues."""

    # Patterns that indicate module-level execution
    PATTERNS = [
        # Constant assignment with function call
        (r'^export const \w+ = \w+\(', 'Export constant with function call'),
        # Direct class instantiation
        (r'^export const \w+ = new \w+\(', 'Export constant with class instantiation'),
        # Direct environment variable access
        (r'^export const \w+ = process\.env\.', 'Direct environment variable access'),
        # Module-level new instantiation (not in function)
        (r'^const \w+ = new \w+\(', 'Module-level class instantiation'),
        # Module-level function calls assigned to const
        (r'^const \w+ = \w+\(', 'Module-level function call'),
    ]

    # Safe patterns that should be ignored
    SAFE_PATTERNS = [
        r'^export const \w+: \w+ = ',  # Type annotations without initialization
        r'^const \w+: \w+ = ',  # Type annotations
        r'^\s*//',  # Comments
        r'^\s*/\*',  # Block comments
        r'^import ',  # Imports
        r'^export \{ ',  # Re-exports
        r'^export type ',  # Type exports
        r'^export interface ',  # Interface exports
    ]

    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.issues: List[Tuple[str, int, str, str]] = []

    def is_safe_line(self, line: str) -> bool:
        """Check if a line matches safe patterns."""
        return any(re.match(pattern, line) for pattern in self.SAFE_PATTERNS)

    def check_file(self, file_path: Path) -> None:
        """Check a single TypeScript file for initialization issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            in_function = False
            brace_count = 0

            for line_num, line in enumerate(lines, start=1):
                stripped = line.strip()

                # Skip empty lines and safe patterns
                if not stripped or self.is_safe_line(stripped):
                    continue

                # Track if we're inside a function
                if re.match(r'^(export\s+)?function\s+\w+', stripped) or \
                   re.match(r'^(export\s+)?(async\s+)?function\s+\w+', stripped):
                    in_function = True
                    brace_count = 0

                # Count braces to track function boundaries
                brace_count += stripped.count('{') - stripped.count('}')

                # Exit function when braces balance
                if in_function and brace_count <= 0:
                    in_function = False

                # Only check module-level code (not inside functions)
                if not in_function:
                    for pattern, description in self.PATTERNS:
                        if re.match(pattern, stripped):
                            self.issues.append((
                                str(file_path.relative_to(self.directory)),
                                line_num,
                                description,
                                stripped[:80]  # First 80 chars
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
        if not self.issues:
            print("✅ No module-level initialization issues found!")
            print("\nAll code appears to use lazy initialization patterns.")
            return

        print(f"⚠️  Found {len(self.issues)} potential module-level initialization issue(s):\n")

        current_file = None
        for file_path, line_num, description, code in sorted(self.issues):
            if file_path != current_file:
                print(f"\n📄 {file_path}")
                current_file = file_path

            print(f"  Line {line_num}: {description}")
            print(f"    {code}")

        print("\n" + "=" * 80)
        print("💡 Recommended fixes:")
        print("=" * 80)
        print("""
1. Environment Variables:
   ❌ export const env = validateEnv()
   ✅ export const env = new Proxy({}, { get() { return validateEnv() } })

2. Database Clients:
   ❌ export const prisma = new PrismaClient()
   ✅ function getPrisma() { ... }
      export const prisma = new Proxy({}, { get() { return getPrisma() } })

3. External Services:
   ❌ export const resend = new Resend(apiKey)
   ✅ function getResend() { ... }
      export const resend = new Proxy({}, { get() { return getResend() } })

4. App Initialization:
   ❌ const app = express(); app.use(...)
   ✅ function createApp() { const app = express(); ...; return app; }

See the vercel-serverless-deployment skill for complete examples.
""")

    def run(self) -> int:
        """Run the checker and return exit code."""
        if not self.directory.exists():
            print(f"Error: Directory '{self.directory}' not found", file=sys.stderr)
            return 1

        print(f"Scanning {self.directory} for module-level initialization issues...\n")
        self.scan_directory()
        self.print_report()

        return 1 if self.issues else 0


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python check-lazy-init.py <directory>")
        print("Example: python check-lazy-init.py src/")
        return 1

    checker = LazyInitChecker(sys.argv[1])
    return checker.run()


if __name__ == '__main__':
    sys.exit(main())
