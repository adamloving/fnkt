#!/usr/bin/env python3
"""
Print the current time.

This script prints the current system time to the console or writes it to a specified output file.
It is fully self-contained and will install its own dependencies when run, if any are specified.

Required packages (installed automatically):
    - None

Usage:
    python print_time.py [--output-file TIME_FILE] [--format TIME_FORMAT]

Example:
    python print_time.py --output-file current_time.txt --format "%Y-%m-%d %H:%M:%S"
"""

import os
import sys
import subprocess
import logging
import argparse
from typing import List, Optional, Tuple
from datetime import datetime

DEPENDENCIES = {
    # No external dependencies required for this script
}



def setup_dependencies() -> None:
    """Install required packages if they're not already installed."""
    if not DEPENDENCIES:
        logging.info("No external dependencies to install.")
        return

    try:
        # Format dependencies with versions
        packages_with_versions = [f"{pkg}>={ver}" for pkg, ver in DEPENDENCIES.items()]

        # Determine if running in a virtual environment using a robust check including the VIRTUAL_ENV env var
        in_virtualenv = (
            'VIRTUAL_ENV' in os.environ or
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.prefix != sys.base_prefix) or
            ('venv' in sys.executable.lower())
        )

        # Build install command conditionally
        install_cmd = [sys.executable, '-m', 'pip', 'install']
        if not in_virtualenv:
            install_cmd.append('--user')
        install_cmd.append('--quiet')
        install_cmd.extend(packages_with_versions)

        subprocess.check_call(
            install_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logging.info("Dependencies checked and installed if needed.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install required packages: {e}")
        sys.exit(1)

def resolve_output_file(output_file: Optional[str], artifacts: List[str]) -> Optional[str]:
    """
    Resolve the output file path based on artifact mappings.

    Args:
        output_file (Optional[str]): The original output file path.
        artifacts (List[str]): List of artifact mappings in the form local_path:container_path.

    Returns:
        Optional[str]: The resolved local output file path, or None if not specified.
    """
    if not output_file:
        return None

    # Expand user directory if present
    output_file = os.path.expanduser(output_file)

    # Check artifact mappings
    for artifact in artifacts:
        try:
            local_path, container_path = artifact.split(':')
            local_path = os.path.expanduser(local_path)
            container_path = os.path.expanduser(container_path)

            # If the container path matches the output file's directory, use the local path
            if os.path.abspath(container_path) == os.path.abspath(os.path.dirname(output_file)):
                resolved_path = os.path.join(local_path, os.path.basename(output_file))
                return resolved_path
        except ValueError:
            logging.warning(f"Invalid artifact mapping: {artifact}. Expected format local_path:container_path.")
            continue

    return output_file

def main():
    parser = argparse.ArgumentParser(
        description="Print the current system time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python print_time.py --output-file current_time.txt --format \"%Y-%m-%d %H:%M:%S\""
    )
    parser.add_argument(
        '--output-file',
        help="File to write the current time instead of printing to stdout"
    )
    parser.add_argument(
        '--format',
        default="%Y-%m-%d %H:%M:%S",
        help="Format string for the current time (default: \"%%Y-%%m-%%d %%H:%%M:%%S\")"
    )
    parser.add_argument(
        '--artifacts',
        action='append',
        default=[],
        help=argparse.SUPPRESS  # Hide from help but still accept it
    )
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Resolve the output file path based on artifacts
    resolved_output_file = resolve_output_file(args.output_file, args.artifacts)

    # Ensure dependencies are installed
    setup_dependencies()

    try:
        # Get current time
        current_time = datetime.now().strftime(args.format)
        logging.info(f"Current time: {current_time}")

        if resolved_output_file:
            # Ensure the output directory exists
            output_dir = os.path.dirname(resolved_output_file)
            if output_dir:
                os.makedirs(output_dir, mode=0o755, exist_ok=True)

            # Write the current time to the specified file
            with open(resolved_output_file, 'w') as f:
                f.write(current_time + '\n')
            logging.info(f"Current time written to {resolved_output_file}")

            # Set permissions on the created file
            os.chmod(resolved_output_file, 0o644)
        else:
            # Print the current time to stdout
            print(current_time)
    except Exception as e:
        logging.error(f"An error occurred while printing the current time: {e}")
        sys.exit(1)

    logging.info("Time retrieval process completed successfully.")

if __name__ == "__main__":
    main()