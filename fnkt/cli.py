"""Command-line interface for fnkt."""
import click
from fnkt import generator, runner

@click.group()
def main():
    """fnkt: Generate and run self-contained Python workflows."""
    pass

@main.command()
@click.argument("description")
@click.option("--output-dir", "-o", default="./workflows", help="Output directory for the generated script.")
@click.option("--name", default=None, help="Optional name for the workflow file.")
def gen(description, output_dir, name):
    """Generate a Python workflow from a natural language description."""
    filepath = generator.generate_workflow(description, output_dir, name)
    click.echo(f"Workflow generated at: {filepath}")

@main.command()
@click.option("--container", default="e2b", help="Container runtime to use (e.g., e2b).")
@click.argument("script_path")
@click.option("--url", help="URL to process for the workflow")
@click.argument("script_args", nargs=-1)
@click.option("--artifacts", multiple=True, help="Artifact mapping in the form local_path:container_path")
def run(container, script_path, url, script_args, artifacts):
    """Run a generated Python workflow inside an ephemeral container."""
    # If URL is provided, add it to script_args
    if url:
        script_args = (url,) + script_args
    runner.run_in_container(container, script_path, script_args, artifacts)

if __name__ == "__main__":
    main() 