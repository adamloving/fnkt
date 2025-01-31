"""Container execution module for running workflows."""
import os
import subprocess
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerExecutionError(Exception):
    """Raised when container execution fails."""
    pass

def run_in_container(container, script_path, script_args, artifacts):
    """
    Run the given Python script inside an ephemeral container.

    Parameters:
        container (str): Container runtime identifier (e.g., 'e2b').
        script_path (str): Path to the Python script.
        script_args (tuple): Arguments to pass to the script.
        artifacts (list): List of artifact mappings in the form "local:container".
    """
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Instead of calling "fnkt-runner", call the Python interpreter with -m or directly invoking the script.
    # Option A: Using the sys.executable to ensure the correct interpreter is used.
    cmd = [sys.executable, script_path]  # Replace fnkt-runner with python interpreter

    # If container specification or artifact mapping are still required, you might handle them here
    if script_args:
        cmd.extend(script_args)

    for mapping in artifacts:
        if ":" not in mapping:
            raise ValueError(f"Invalid artifact mapping format: {mapping}")
        # Depending on your design, you might want to pass artifact mapping as environment variables,
        # or even skip these if not applicable when running outside the container.
        cmd.extend(["--artifacts", mapping])

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