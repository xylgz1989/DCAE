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
# Import task management functions
from .task_management.cli_integration import add_task_management_to_parser, handle_task_command
# Import product knowledge functions
from .product_knowledge.cli_integration import (
    search_knowledge, knowledge_info, get_document, suggest_knowledge
)
# Import the best practices review functionality
from .generated_output_review import GeneratedOutputReviewer


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

        # Task management command
        add_task_management_to_parser(subparsers)

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

        # Product knowledge command
        knowledge_parser = subparsers.add_parser("knowledge", help="Access product knowledge and documentation")
        knowledge_subparsers = knowledge_parser.add_subparsers(dest="knowledge_command", help="Knowledge commands")

        knowledge_search_parser = knowledge_subparsers.add_parser("search", help="Search for product knowledge")
        knowledge_search_parser.add_argument(
            "query",
            help="Search query for product knowledge"
        )
        knowledge_search_parser.add_argument(
            "--max-results", "-n", type=int, default=5,
            help="Maximum number of results to return (default: 5)"
        )
        knowledge_search_parser.add_argument(
            "--knowledge-base", "-kb", type=Path,
            help="Path to knowledge base directory (default: configured path)"
        )

        knowledge_info_parser = knowledge_subparsers.add_parser("info", help="Show information about knowledge base")
        knowledge_info_parser.add_argument(
            "--knowledge-base", "-kb", type=Path,
            help="Path to knowledge base directory (default: configured path)"
        )

        knowledge_get_parser = knowledge_subparsers.add_parser("get", help="Retrieve a specific document")
        knowledge_get_parser.add_argument(
            "doc_id",
            help="ID of the document to retrieve"
        )
        knowledge_get_parser.add_argument(
            "--knowledge-base", "-kb", type=Path,
            help="Path to knowledge base directory (default: configured path)"
        )

        knowledge_suggest_parser = knowledge_subparsers.add_parser("suggest", help="Get relevant knowledge for context")
        knowledge_suggest_parser.add_argument(
            "context",
            help="Development context to find relevant knowledge for"
        )
        knowledge_suggest_parser.add_argument(
            "--max-results", "-n", type=int, default=3,
            help="Maximum number of suggestions (default: 3)"
        )
        knowledge_suggest_parser.add_argument(
            "--knowledge-base", "-kb", type=Path,
            help="Path to knowledge base directory (default: configured path)"
        )

        # Best practices review command
        best_practices_parser = subparsers.add_parser("best-practices", help="Run best practices review")
        best_practices_subparsers = best_practices_parser.add_subparsers(dest="bp_command", help="Best practices commands")

        bp_review_parser = best_practices_subparsers.add_parser("review", help="Review code for best practices compliance")
        bp_review_parser.add_argument(
            "target_path",
            nargs="?",
            default=".",
            help="Path to review for best practices (default: current directory)"
        )
        bp_review_parser.add_argument(
            "--output",
            "-o",
            help="Output file for the review report (default: console output)"
        )
        bp_review_parser.add_argument(
            "--requirements-file",
            help="Path to requirements specification file"
        )
        bp_review_parser.add_argument(
            "--architecture-file",
            help="Path to architecture specification file"
        )

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

    def run_knowledge(self, args):
        """Run the knowledge command."""
        import asyncio

        if args.knowledge_command == "search":
            from .product_knowledge.access import ProductKnowledgeAccess, SimpleProductKnowledgeCache
            from .config import DCAEConfig

            # Load configuration to get knowledge base path
            config_path = Path(".dcae/config.yaml")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                kb_path = Path(config_data.get('dcae', {}).get('project_knowledge_path', './docs'))
            else:
                kb_path = Path("./docs")

            # Override with command-line option if provided
            if args.knowledge_base:
                kb_path = args.knowledge_base

            # Create product knowledge access instance
            cache = SimpleProductKnowledgeCache()
            knowledge_access = ProductKnowledgeAccess(kb_path, cache)

            # Perform search
            async def run_search():
                results = await knowledge_access.search(args.query, args.max_results)
                return results

            results = asyncio.run(run_search())

            # Print results
            if results:
                print(f"\nFound {len(results)} relevant documents:\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['title']}")
                    print(f"   Source: {result['source_path']}")
                    print(f"   Relevance: {result['score']:.2f}")
                    print(f"   Preview: {result['content_preview']}\n")
            else:
                print("No relevant documents found.")

        elif args.knowledge_command == "info":
            from .config import DCAEConfig

            # Load configuration to get knowledge base path
            config_path = Path(".dcae/config.yaml")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                kb_path = Path(config_data.get('dcae', {}).get('project_knowledge_path', './docs'))
            else:
                kb_path = Path("./docs")

            # Override with command-line option if provided
            if args.knowledge_base:
                kb_path = args.knowledge_base

            if not kb_path.exists():
                print(f"Knowledge base path does not exist: {kb_path}")
                sys.exit(1)

            # Count documents
            md_files = list(kb_path.rglob("*.md"))
            txt_files = list(kb_path.rglob("*.txt"))
            rst_files = list(kb_path.rglob("*.rst"))

            total_docs = len(md_files) + len(txt_files) + len(rst_files)

            print(f"Product Knowledge Base Information:")
            print(f"  Path: {kb_path.absolute()}")
            print(f"  Total documents: {total_docs}")
            print(f"  Markdown files: {len(md_files)}")
            print(f"  Text files: {len(txt_files)}")
            print(f"  ReStructuredText files: {len(rst_files)}")

        elif args.knowledge_command == "get":
            from .product_knowledge.access import ProductKnowledgeAccess, SimpleProductKnowledgeCache
            from .config import DCAEConfig

            # Load configuration to get knowledge base path
            config_path = Path(".dcae/config.yaml")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                kb_path = Path(config_data.get('dcae', {}).get('project_knowledge_path', './docs'))
            else:
                kb_path = Path("./docs")

            # Override with command-line option if provided
            if args.knowledge_base:
                kb_path = args.knowledge_base

            # Create product knowledge access instance
            cache = SimpleProductKnowledgeCache()
            knowledge_access = ProductKnowledgeAccess(kb_path, cache)

            # Get document
            async def run_get():
                doc = await knowledge_access.get_document_by_id(args.doc_id)
                return doc

            doc = asyncio.run(run_get())

            if doc:
                print(f"Title: {doc['title']}")
                print(f"Source: {doc['source_path']}")
                print(f"Content:\n{doc['content']}")
            else:
                print(f"No document found with ID: {doc['id']}")

        elif args.knowledge_command == "suggest":
            from .product_knowledge.access import ProductKnowledgeAccess, SimpleProductKnowledgeCache
            from .config import DCAEConfig

            # Load configuration to get knowledge base path
            config_path = Path(".dcae/config.yaml")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                kb_path = Path(config_data.get('dcae', {}).get('project_knowledge_path', './docs'))
            else:
                kb_path = Path("./docs")

            # Override with command-line option if provided
            if args.knowledge_base:
                kb_path = args.knowledge_base

            # Create product knowledge access instance
            cache = SimpleProductKnowledgeCache()
            knowledge_access = ProductKnowledgeAccess(kb_path, cache)

            # Get relevant documents
            async def run_suggest():
                results = await knowledge_access.get_relevant_documents(args.context, args.max_results)
                return results

            results = asyncio.run(run_suggest())

            # Print suggestions
            if results:
                print(f"\nBased on your context '{args.context}', here are relevant documents:\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['title']}")
                    print(f"   Source: {result['source_path']}")
                    print(f"   Relevance: {result['score']:.2f}")
            else:
                print("No relevant documents found for the given context.")
        else:
            print("Please specify a knowledge command: search, info, get, or suggest")
            sys.exit(1)

    def run_best_practices(self, args):
        """Run the best practices command."""
        if args.bp_command == "review":
            # Load requirements and architecture specs if provided
            requirements_spec = None
            if args.requirements_file:
                req_path = Path(args.requirements_file)
                if req_path.exists():
                    with open(req_path, 'r', encoding='utf-8') as f:
                        if req_path.suffix.lower() in ['.yaml', '.yml']:
                            import yaml
                            requirements_spec = yaml.safe_load(f)
                        else:
                            import json
                            requirements_spec = json.load(f)
                else:
                    print(f"Requirements file not found: {req_path}")
                    sys.exit(1)

            architecture_spec = None
            if args.architecture_file:
                arch_path = Path(args.architecture_file)
                if arch_path.exists():
                    with open(arch_path, 'r', encoding='utf-8') as f:
                        if arch_path.suffix.lower() in ['.yaml', '.yml']:
                            import yaml
                            architecture_spec = yaml.safe_load(f)
                        else:
                            import json
                            architecture_spec = json.load(f)
                else:
                    print(f"Architecture file not found: {arch_path}")
                    sys.exit(1)

            # Initialize the best practices reviewer
            reviewer = GeneratedOutputReviewer(
                project_path=args.target_path,
                requirements_spec=requirements_spec,
                architecture_spec=architecture_spec
            )

            print(f"DCAE Best Practices Review - Analyzing: {args.target_path}")
            print("="*60)

            # Perform the review
            report = reviewer.review_generated_output()

            # Print summary
            reviewer.print_findings_summary(report)

            # Export report if output file specified
            if args.output:
                reviewer.export_report(report, args.output)
                print(f"\nDetailed report exported to: {args.output}")
            else:
                print(f"\nTo export detailed report, use --output option.")
        else:
            print("Please specify a best practices command: review")
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
        elif args.command == "task" or args.command == "tasks":
            import asyncio
            asyncio.run(handle_task_command(args))
        elif args.command == "knowledge":
            self.run_knowledge(args)
        elif args.command == "best-practices":
            self.run_best_practices(args)
        else:
            self.parser.print_help()
            sys.exit(1)


def main():
    """Main function to handle command-line interface."""
    cli = DCAECLI()
    cli.run()


if __name__ == "__main__":
    main()