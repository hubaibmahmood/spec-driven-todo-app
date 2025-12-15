#!/usr/bin/env python3
"""
Analyze module dependencies to identify initialization order issues.

This script analyzes TypeScript imports to identify potential circular dependencies
and module initialization order issues that can cause problems in serverless environments.

Usage:
    python analyze-module-deps.py <directory>
    python analyze-module-deps.py src/

Outputs:
- Dependency graph
- Circular dependency detection
- Module initialization order recommendations
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque


class ModuleDependencyAnalyzer:
    """Analyzes module dependencies in TypeScript projects."""

    IMPORT_PATTERN = r'''import\s+(?:(?:\{[^}]+\})|(?:\*\s+as\s+\w+)|(?:\w+))\s+from\s+['"]([^'"]+)['"]'''

    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.all_modules: Set[str] = set()

    def normalize_import_path(self, current_file: Path, import_path: str) -> str:
        """Normalize import path to be relative to root directory."""
        if not import_path.startswith('.'):
            # External package, skip
            return None

        # Remove .js extension if present
        import_path = re.sub(r'\.js$', '', import_path)

        # Resolve relative path
        current_dir = current_file.parent
        resolved = (current_dir / import_path).resolve()

        try:
            # Make relative to root directory
            relative = resolved.relative_to(self.directory.resolve())
            return str(relative)
        except ValueError:
            # Import is outside the scanned directory
            return None

    def analyze_file(self, file_path: Path) -> None:
        """Analyze imports in a single TypeScript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Get module name relative to root
            module_name = str(file_path.relative_to(self.directory))
            module_name = re.sub(r'\.ts$', '', module_name)
            self.all_modules.add(module_name)

            # Find all imports
            for match in re.finditer(self.IMPORT_PATTERN, content):
                import_path = match.group(1)
                normalized = self.normalize_import_path(file_path, import_path)

                if normalized:
                    self.dependencies[module_name].add(normalized)
                    self.all_modules.add(normalized)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}", file=sys.stderr)

    def scan_directory(self) -> None:
        """Recursively scan directory for TypeScript files."""
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.ts') and not file.endswith('.d.ts'):
                    file_path = Path(root) / file
                    self.analyze_file(file_path)

    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies using DFS."""
        def dfs(node: str, visited: Set[str], rec_stack: Set[str], path: List[str]) -> List[str]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    cycle = dfs(neighbor, visited, rec_stack, path)
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return None

        visited = set()
        cycles = []

        for module in self.all_modules:
            if module not in visited:
                cycle = dfs(module, visited, set(), [])
                if cycle:
                    cycles.append(cycle)

        return cycles

    def topological_sort(self) -> List[str]:
        """Perform topological sort to determine initialization order."""
        # Calculate in-degrees
        in_degree = {module: 0 for module in self.all_modules}
        for module in self.all_modules:
            for dep in self.dependencies.get(module, []):
                if dep in in_degree:
                    in_degree[dep] += 1

        # Find modules with no dependencies
        queue = deque([module for module, degree in in_degree.items() if degree == 0])
        sorted_modules = []

        while queue:
            module = queue.popleft()
            sorted_modules.append(module)

            # Reduce in-degree for dependent modules
            for dep_module in self.all_modules:
                if module in self.dependencies.get(dep_module, []):
                    in_degree[dep_module] -= 1
                    if in_degree[dep_module] == 0:
                        queue.append(dep_module)

        return sorted_modules

    def print_report(self) -> None:
        """Print dependency analysis report."""
        print("=" * 80)
        print("MODULE DEPENDENCY ANALYSIS")
        print("=" * 80)

        print(f"\nTotal modules analyzed: {len(self.all_modules)}\n")

        # Check for circular dependencies
        cycles = self.find_circular_dependencies()

        if cycles:
            print("⚠️  CIRCULAR DEPENDENCIES DETECTED:\n")
            for i, cycle in enumerate(cycles, 1):
                print(f"Cycle {i}:")
                for j, module in enumerate(cycle):
                    if j < len(cycle) - 1:
                        print(f"  {module}")
                        print(f"    ↓ imports")
                    else:
                        print(f"  {module} (back to start)")
                print()

            print("💡 Circular dependencies can cause initialization issues in serverless environments.")
            print("   Consider refactoring to extract shared types/interfaces into separate files.\n")
        else:
            print("✅ No circular dependencies detected.\n")

        # Show module initialization order
        sorted_modules = self.topological_sort()

        if len(sorted_modules) == len(self.all_modules):
            print("📊 RECOMMENDED INITIALIZATION ORDER:\n")
            print("Modules should be initialized in this order (dependencies first):\n")

            for i, module in enumerate(sorted_modules, 1):
                deps = self.dependencies.get(module, set())
                dep_count = len(deps)

                if dep_count == 0:
                    print(f"{i:3d}. {module} (no dependencies)")
                else:
                    print(f"{i:3d}. {module} (depends on {dep_count} module(s))")

            print("\n💡 Modules at the top have fewer dependencies and are safer to initialize early.")
            print("   Modules at the bottom depend on many others - use lazy initialization for these.\n")
        else:
            print("⚠️  Could not determine complete initialization order due to cycles.\n")

        # Show dependency statistics
        print("=" * 80)
        print("DEPENDENCY STATISTICS")
        print("=" * 80)

        dep_counts = [(module, len(deps)) for module, deps in self.dependencies.items()]
        dep_counts.sort(key=lambda x: x[1], reverse=True)

        print("\nModules with most dependencies (highest risk for initialization issues):\n")
        for module, count in dep_counts[:10]:
            if count > 0:
                print(f"  {module}: {count} dependencies")

        print("\n💡 Modules with many dependencies should use lazy initialization patterns.")
        print("   See the vercel-serverless-deployment skill for examples.\n")

    def run(self) -> int:
        """Run the analyzer and return exit code."""
        if not self.directory.exists():
            print(f"Error: Directory '{self.directory}' not found", file=sys.stderr)
            return 1

        print(f"Analyzing module dependencies in {self.directory}...\n")
        self.scan_directory()
        self.print_report()

        return 0


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python analyze-module-deps.py <directory>")
        print("Example: python analyze-module-deps.py src/")
        return 1

    analyzer = ModuleDependencyAnalyzer(sys.argv[1])
    return analyzer.run()


if __name__ == '__main__':
    sys.exit(main())
