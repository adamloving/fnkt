"""Container execution module for running workflows."""
import os
import subprocess
import logging
import sys
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerExecutionError(Exception):
    """Raised when container execution fails."""
    pass

def run_in_container(container: str, script_path: str, script_args: List[str], artifacts: List[str]) -> None:
    """
    Run the given Python script inside an ephemeral container.

    Parameters:
        container (str): Container runtime identifier (e.g., 'e2b').
        script_path (str): Path to the Python script.
        script_args (list): Arguments to pass to the script.
        artifacts (list): List of artifact mappings in the form "local:container".
    """
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Base command with script path
    cmd = [sys.executable, script_path]

    # Add any artifact mappings as arguments to the script
    artifact_args = []
    for mapping in artifacts:
        if ":" not in mapping:
            raise ValueError(f"Invalid artifact mapping format: {mapping}")
        artifact_args.extend(["--artifacts", mapping])

    # Add script arguments and artifact arguments
    if script_args:
        cmd.extend(script_args)
    if artifact_args:
        cmd.extend(artifact_args)

    logger.info("Executing command: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Command output:\n%s", result.stdout)
        if result.stderr:
            logger.warning("Command stderr:\n%s", result.stderr)
            
    except subprocess.CalledProcessError as e:
        error_msg = f"Container execution failed with exit code {e.returncode}"
        if e.stderr:
            error_msg += f"\nError output:\n{e.stderr}"
        raise ContainerExecutionError(error_msg) from e
    except Exception as e:
        raise ContainerExecutionError(f"Unexpected error during container execution: {str(e)}") from e 