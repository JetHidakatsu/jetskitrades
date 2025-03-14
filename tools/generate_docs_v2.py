#!/usr/bin/env python3
"""Documentation generator for the Solana Bot project."""

import ast
from pathlib import Path
from typing import Dict, Any


class DocStringParser:
    """Parse Python file for docstrings without importing."""

    @staticmethod
    def parse_file(file_path: Path) -> Dict[str, Any]:
        """Parse a Python file and extract documentation."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            return DocStringParser._parse_module(tree, content)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return {"doc": "", "classes": {}, "functions": {}}

    @staticmethod
    def _get_docstring(node: ast.AST, content: str) -> str:
        """Extract docstring from an AST node."""
        if (docstring := ast.get_docstring(node)) is not None:
            return docstring
        return ""

    @staticmethod
    def _parse_arguments(node: ast.arguments, content: str) -> list:
        """Parse function arguments."""
        args = []
        for arg in node.args:
            arg_info = f"- {arg.arg}"
            if arg.annotation:
                annotation = content[
                    arg.annotation.col_offset : arg.annotation.end_col_offset
                ]
                arg_info += f": {annotation}"
            args.append(arg_info)
        return args

    @staticmethod
    def _parse_function(node: ast.FunctionDef, content: str) -> Dict[str, Any]:
        """Parse a function definition."""
        return {
            "doc": DocStringParser._get_docstring(node, content),
            "params": DocStringParser._parse_arguments(node.args, content),
            "returns": "Any",  # Default return type
        }

    @staticmethod
    def _parse_class(node: ast.ClassDef, content: str) -> Dict[str, Any]:
        """Parse a class definition."""
        methods = {}
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                methods[item.name] = DocStringParser._parse_function(item, content)

        return {
            "doc": DocStringParser._get_docstring(node, content),
            "methods": methods,
        }

    @staticmethod
    def _parse_module(tree: ast.Module, content: str) -> Dict[str, Any]:
        """Parse a module."""
        module_doc = DocStringParser._get_docstring(tree, content)
        classes = {}
        functions = {}

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes[node.name] = DocStringParser._parse_class(node, content)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                functions[node.name] = DocStringParser._parse_function(node, content)

        return {"doc": module_doc, "classes": classes, "functions": functions}


def generate_markdown(file_path: Path, output_dir: Path):
    """Generate markdown documentation for a Python file."""
    try:
        docs = DocStringParser.parse_file(file_path)
        output_path = output_dir / f"{file_path.stem}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            # Module header
            f.write(f"# {file_path.stem}\n\n")
            if docs["doc"]:
                f.write(f"{docs['doc']}\n\n")

            # Classes
            if docs["classes"]:
                f.write("## Classes\n\n")
                for name, cls in docs["classes"].items():
                    f.write(f"### {name}\n\n")
                    if cls["doc"]:
                        f.write(f"{cls['doc']}\n\n")

                    if cls["methods"]:
                        f.write("#### Methods\n\n")
                        for method_name, method in cls["methods"].items():
                            f.write(f"##### `{method_name}`\n\n")
                            if method["doc"]:
                                f.write(f"{method['doc']}\n\n")
                            if method["params"]:
                                f.write("Parameters:\n")
                                for param in method["params"]:
                                    f.write(f"{param}\n")
                                f.write("\n")
                            f.write(f"Returns: {method['returns']}\n\n")

            # Functions
            if docs["functions"]:
                f.write("## Functions\n\n")
                for name, func in docs["functions"].items():
                    f.write(f"### `{name}`\n\n")
                    if func["doc"]:
                        f.write(f"{func['doc']}\n\n")
                    if func["params"]:
                        f.write("Parameters:\n")
                        for param in func["params"]:
                            f.write(f"{param}\n")
                        f.write("\n")
                    f.write(f"Returns: {func['returns']}\n\n")

        return True
    except Exception as e:
        print(f"Error generating documentation for {file_path}: {e}")
        return False


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "env"
    output_dir = project_root / "docs" / "api"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating documentation...")

    # Track successfully documented files
    documented_files = []

    # Process Python files in the env directory
    for file_path in source_dir.glob("*.py"):
        if not file_path.name.startswith("_"):
            print(f"Processing {file_path.name}...")
            if generate_markdown(file_path, output_dir):
                documented_files.append(file_path.stem)

    # Generate index file
    index_path = output_dir / "index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# API Documentation\n\n")
        f.write("## Core Components\n\n")

        # Group files by category
        core_files = [
            name
            for name in documented_files
            if name
            in {
                "trading_bot",
                "trading_logic",
                "position_manager",
                "transaction_executor",
            }
        ]
        util_files = [
            name
            for name in documented_files
            if name in {"config", "utils", "monitor", "latency_tracker"}
        ]
        integration_files = [
            name
            for name in documented_files
            if name in {"raydium", "helius_provider", "websocket_server"}
        ]
        other_files = [
            name
            for name in documented_files
            if name not in set(core_files + util_files + integration_files)
        ]

        # Write categorized links
        for name in core_files:
            f.write(f"- [{name}]({name}.md)\n")

        f.write("\n## Utilities\n\n")
        for name in util_files:
            f.write(f"- [{name}]({name}.md)\n")

        f.write("\n## Integrations\n\n")
        for name in integration_files:
            f.write(f"- [{name}]({name}.md)\n")

        if other_files:
            f.write("\n## Other Components\n\n")
            for name in other_files:
                f.write(f"- [{name}]({name}.md)\n")

    print("Documentation generation complete!")


if __name__ == "__main__":
    main()
