"""
DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework
Main CLI Module

This module provides the main command-line interface for the DCAE framework,
including the initialization functionality for new projects.
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Import the initialization function from the init module
from .init import initialize_dcae_project
# Import the requirements functions
from .requirements import (
    initialize_requirements_project,
    input_requirements_interactively,
    edit_requirements_interactively,
    load_requirements,
    validate_requirements,
    save_requirements,
    print_requirements_summary as req_print_summary
)
# Import the requirements document generator functions
from .req_docs_generator import (
    generate_preliminary_requirements_documents,
    create_sample_project_inputs
)


class DCAECLI:
    """Main CLI class for DCAE framework."""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            prog="dcae",
            description="DCAE (Disciplined Consensus-Driven Agentic Engineering) Framework"
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Init command
        init_parser = subparsers.add_parser("init", help="Initialize a new DCAE project")
        init_parser.add_argument(
            "project_path",
            nargs="?",
            default=".",
            help="Path where to create the new DCAE project (default: current directory)"
        )
        init_parser.add_argument(
            "--name",
            help="Name of the project (default: directory name)"
        )

        # Run command
        run_parser = subparsers.add_parser("run", help="Run the BMAD workflow")
        run_parser.add_argument(
            "--stage",
            choices=["business", "architect", "developer", "qa"],
            help="Run specific stage of the BMAD workflow"
        )
        run_parser.add_argument(
            "--discipline-level",
            choices=["fast", "balanced", "strict"],
            help="Override the configured discipline level"
        )

        # Config command
        config_parser = subparsers.add_parser("config", help="Manage DCAE configuration")
        config_parser.add_argument(
            "--show",
            action="store_true",
            help="Show current configuration"
        )
        config_parser.add_argument(
            "--llm-provider",
            choices=["openai", "anthropic", "qwen", "glm"],
            help="Set LLM provider"
        )
        config_parser.add_argument(
            "--api-key",
            help="Set API key for the LLM provider"
        )

        # Status command
        status_parser = subparsers.add_parser("status", help="Show project status")

        # Requirements command
        req_parser = subparsers.add_parser("requirements", help="Manage project requirements")
        req_subparsers = req_parser.add_subparsers(dest="req_command", help="Requirements commands")

        req_init_parser = req_subparsers.add_parser("init", help="Initialize requirements for project")
        req_init_parser.add_argument(
            "--project-name",
            help="Name of the project (default: directory name)"
        )

        req_input_parser = req_subparsers.add_parser("input", help="Interactively input requirements")
        req_input_parser.add_argument(
            "--project-name",
            help="Name of the project (default: directory name)"
        )

        req_edit_parser = req_subparsers.add_parser("edit", help="Edit existing requirements")

        req_validate_parser = req_subparsers.add_parser("validate", help="Validate requirements")

        req_view_parser = req_subparsers.add_parser("view", help="View current requirements")

        # Requirements document generation command
        req_doc_parser = subparsers.add_parser("req-docs", help="Generate requirements documents")
        req_doc_subparsers = req_doc_parser.add_subparsers(dest="req_docs_command", help="Requirements document commands")

        req_doc_generate_parser = req_doc_subparsers.add_parser("generate", help="Generate preliminary requirements documents")
        req_doc_generate_parser.add_argument(
            "--input-file",
            help="Path to input file containing project information (JSON or YAML)"
        )
        req_doc_generate_parser.add_argument(
            "--output-dir",
            default="./requirements-docs",
            help="Directory to save generated documents (default: ./requirements-docs)"
        )
        req_doc_generate_parser.add_argument(
            "--sample",
            action="store_true",
            help="Generate documents using sample project inputs"
        )

        req_doc_sample_parser = req_doc_subparsers.add_parser("sample", help="Create sample project inputs file")

        return parser

    def run_init(self, args):
        """Run the init command."""
        success = initialize_dcae_project(args.project_path)
        if not success:
            sys.exit(1)

    def run_run(self, args):
        """Run the run command."""
        print("Running BMAD workflow...")

        # Check if we're in a DCAE project directory
        config_path = Path(".dcae/config.yaml")
        if not config_path.exists():
            print("Error: Not in a DCAE project directory. Run 'dcae init' first.")
            sys.exit(1)

        # Load the configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        discipline_level = args.discipline_level or config['dcae']['bmad_workflow']['discipline_level']
        print(f"Using discipline level: {discipline_level}")

        if args.stage:
            print(f"Running {args.stage} stage of BMAD workflow...")
            # Implement specific stage execution
        else:
            print("Running full BMAD workflow...")
            # Implement full workflow execution
            self._run_business_stage(config)
            self._run_architecture_stage(config)
            self._run_development_stage(config)
            self._run_qa_stage(config)

        print("BMAD workflow completed.")

    def _run_business_stage(self, config):
        """Run the business (requirements) stage."""
        print("  Running Business Stage...")
        # Implementation would go here
        print("  ✓ Business stage completed")

    def _run_architecture_stage(self, config):
        """Run the architecture stage."""
        print("  Running Architecture Stage...")
        # Implementation would go here
        print("  ✓ Architecture stage completed")

    def _run_development_stage(self, config):
        """Run the development stage."""
        print("  Running Development Stage...")
        # Implementation would go here
        print("  ✓ Development stage completed")

    def _run_qa_stage(self, config):
        """Run the quality assurance stage."""
        print("  Running QA Stage...")
        # Implementation would go here
        print("  ✓ QA stage completed")

    def run_config(self, args):
        """Run the config command."""
        config_path = Path(".dcae/config.yaml")

        if not config_path.exists():
            print("Error: Not in a DCAE project directory. Run 'dcae init' first.")
            sys.exit(1)

        if args.show:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print("Current DCAE Configuration:")
            print(yaml.dump(config, default_flow_style=False, allow_unicode=True))
        elif args.llm_provider and args.api_key:
            # Update the configuration with the new API key
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            config['dcae']['llm_providers'][args.llm_provider]['api_key'] = args.api_key
            config['dcae']['llm_providers'][args.llm_provider]['enabled'] = True

            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            print(f"Updated {args.llm_provider} API key in configuration")
        else:
            print("Config command requires either --show or --llm-provider and --api-key arguments")
            sys.exit(1)

    def run_status(self, args):
        """Run the status command."""
        state_path = Path(".dcae/state.json")

        if not state_path.exists():
            print("Error: Not in a DCAE project directory. Run 'dcae init' first.")
            sys.exit(1)

        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        print("DCAE Project Status:")
        print(f"  Current Stage: {state['current_stage']}")
        print("  Stage Completion:")
        for stage, info in state['stages'].items():
            status = "✓ Completed" if info['completed'] else "⏳ Pending"
            timestamp = info['timestamp'] if info['timestamp'] else "Not started"
            print(f"    {stage}: {status} ({timestamp})")

    def run_requirements(self, args):
        """Run the requirements command."""
        project_path = Path(".")

        if args.req_command == "init":
            success = initialize_requirements_project(str(project_path), args.project_name)
            if not success:
                sys.exit(1)
        elif args.req_command == "input":
            requirements = input_requirements_interactively(args.project_name or project_path.name)
            if requirements:
                requirements_path = project_path / "requirements.yaml"
                if save_requirements(requirements, requirements_path):
                    print(f"\n✓ Requirements saved to {requirements_path}")
                else:
                    print("Failed to save requirements")
                    sys.exit(1)
        elif args.req_command == "edit":
            requirements_path = project_path / "requirements.yaml"
            success = edit_requirements_interactively(requirements_path)
            if not success:
                sys.exit(1)
        elif args.req_command == "validate":
            requirements_path = project_path / "requirements.yaml"
            requirements = load_requirements(requirements_path)
            if not requirements:
                print(f"No requirements found at {requirements_path}")
                sys.exit(1)

            errors = validate_requirements(requirements)
            if errors:
                print("Validation errors found:")
                for error in errors:
                    print(f"- {error}")
                sys.exit(1)
            else:
                print("✓ Requirements are valid!")
        elif args.req_command == "view":
            requirements_path = project_path / "requirements.yaml"
            requirements = load_requirements(requirements_path)
            if not requirements:
                print(f"No requirements found at {requirements_path}")
                sys.exit(1)

            req_print_summary(requirements)
        else:
            print("Please specify a requirements command: init, input, edit, validate, or view")
            sys.exit(1)

    def run_req_docs(self, args):
        """Run the requirements documents command."""
        if args.req_docs_command == "generate":
            if args.sample:
                project_inputs = create_sample_project_inputs()
                print("Using sample project inputs...")
            elif args.input_file:
                input_path = Path(args.input_file)
                if not input_path.exists():
                    print(f"Error: Input file {input_path} does not exist.")
                    sys.exit(1)

                with open(input_path, 'r', encoding='utf-8') as f:
                    if input_path.suffix.lower() in ['.yaml', '.yml']:
                        project_inputs = yaml.safe_load(f)
                    else:
                        project_inputs = json.load(f)
            else:
                print("Error: Please specify either --input-file or --sample")
                sys.exit(1)

            output_dir = Path(args.output_dir)

            try:
                documents = generate_preliminary_requirements_documents(
                    project_inputs,
                    output_dir=output_dir
                )

                print(f"Generated {len(documents)} requirements documents in {output_dir}/:")
                for filename in documents.keys():
                    print(f"  - {filename}")

                print("\n✓ Preliminary requirements documents generation completed successfully!")
            except Exception as e:
                print(f"Error generating requirements documents: {e}")
                sys.exit(1)
        elif args.req_docs_command == "sample":
            sample_inputs = create_sample_project_inputs()
            output_path = Path("sample-project-inputs.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sample_inputs, f, indent=2, ensure_ascii=False)
            print(f"Sample project inputs saved to {output_path}")
        else:
            print("Please specify a requirements documents command: generate or sample")
            sys.exit(1)

    def run(self):
        """Run the CLI."""
        if len(sys.argv) == 1:
            self.parser.print_help()
            sys.exit(1)

        args = self.parser.parse_args()

        if args.command == "init":
            self.run_init(args)
        elif args.command == "run":
            self.run_run(args)
        elif args.command == "config":
            self.run_config(args)
        elif args.command == "status":
            self.run_status(args)
        elif args.command == "requirements":
            self.run_requirements(args)
        elif args.command == "req-docs":
            self.run_req_docs(args)
        else:
            self.parser.print_help()
            sys.exit(1)


def main():
    """Main function to handle command-line interface."""
    cli = DCAECLI()
    cli.run()


if __name__ == "__main__":
    main()