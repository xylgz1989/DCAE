#!/usr/bin/env python3
"""
DCAE CLI - Command-line interface for DCAE Framework

Usage:
    dcae run --task "Implement feature" --test tests/test.py --source src/code.py
    dcae design --test tests/test.py
    dcae code --source src/code.py
    dcae analyze --threshold 80
    dcae evolve --optimize
    dcae init project_name
    dcae status
"""

import argparse
import json
import sys
from pathlib import Path

from dcae.core import DCAEFramework


def main():
    """Main entry point for DCAE CLI."""
    parser = argparse.ArgumentParser(
        description="DCAE Framework - TDD-driven development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dcae run --task "Implement quick sort" --test tests/test_sort.py --source src/sort.py
  dcae design --test tests/test_feature.py
  dcae code --source src/feature.py
  dcae analyze --threshold 80
  dcae evolve --optimize
  dcae init my_project
        """
    )
    
    parser.add_argument(
        "--project-root", "-p",
        default=".",
        help="Project root directory (default: current directory)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (for programmatic use)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="DCAE commands")
    
    # run command - Full TDD cycle
    run_parser = subparsers.add_parser("run", help="Run complete DCAE cycle")
    run_parser.add_argument("--task", "-t", required=True, help="Task description")
    run_parser.add_argument("--test", required=True, help="Test file path")
    run_parser.add_argument("--source", required=True, help="Source file path")
    run_parser.add_argument("--max-iterations", type=int, default=10, help="Max iterations")
    
    # design command
    design_parser = subparsers.add_parser("design", help="Phase 1: Design")
    design_parser.add_argument("--test", required=True, help="Test file path")
    design_parser.add_argument("--test-cases", nargs="*", help="Test case descriptions")
    
    # code command
    code_parser = subparsers.add_parser("code", help="Phase 2: Code")
    code_parser.add_argument("--source", required=True, help="Source file path")
    
    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Phase 3: Analyze")
    analyze_parser.add_argument("--threshold", type=float, default=80.0, help="Coverage threshold")
    
    # evolve command
    evolve_parser = subparsers.add_parser("evolve", help="Phase 4: Evolve")
    evolve_parser.add_argument("--optimize", action="store_true", help="Include optimization")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize project")
    init_parser.add_argument("project_name", help="Project name")
    
    # status command
    subparsers.add_parser("status", help="Show current status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create framework instance
    dcae = DCAEFramework(args.project_root)
    
    # Execute command
    result = None
    
    try:
        if args.command == "run":
            result = dcae.run(args.test, args.source, args.max_iterations)
        elif args.command == "design":
            result = dcae.design(args.test, args.test_cases)
        elif args.command == "code":
            result = dcae.code(args.source)
        elif args.command == "analyze":
            result = dcae.analyze(args.threshold)
        elif args.command == "evolve":
            result = dcae.evolve(args.optimize)
        elif args.command == "init":
            result = dcae.init(args.project_name)
        elif args.command == "status":
            result = dcae.status()
        
        # Output result
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"DCAE {result.phase.upper()} Phase")
            print(f"{'='*60}")
            print(f"Status: {result.status.upper()}")
            print(f"Timestamp: {result.timestamp}")
            
            if result.tests_total > 0:
                print(f"\nTests: {result.tests_passed}/{result.tests_total} passed")
            
            if result.coverage_lines > 0:
                print(f"Coverage: {result.coverage_lines:.1f}% lines, {result.coverage_functions:.1f}% functions")
            
            if result.iterations > 0:
                print(f"Iterations: {result.iterations}")
            
            if result.artifacts:
                print(f"\nArtifacts:")
                for artifact in result.artifacts:
                    print(f"  - {artifact}")
            
            if result.recommendations:
                print(f"\nRecommendations:")
                for rec in result.recommendations:
                    print(f"  • {rec}")
            
            if result.errors:
                print(f"\nErrors:")
                for err in result.errors:
                    print(f"  ✗ {err}")
            
            print(f"{'='*60}\n")
        
        # Exit with appropriate code
        sys.exit(0 if result.status == "success" else 1)
        
    except Exception as e:
        if args.json:
            print(json.dumps({
                "status": "failed",
                "phase": "error",
                "error": str(e)
            }, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
