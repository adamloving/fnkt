# fnkt

Generate and run self-contained Python workflows using natural language descriptions.

## Features

- Generate complete Python scripts from natural language descriptions using LLMs
- Run workflows in ephemeral containers for isolation and reproducibility
- Simple CLI interface for workflow generation and execution
- Support for artifact mapping between host and container

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fnkt.git
cd fnkt

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install the package
pip install -e .
```

## Usage

### Generating a Workflow

Use the `gen` command to create a new workflow from a natural language description:

```bash
fnkt gen "download all images from a webpage and resize them to 800x600"
```

Options:

- `--output-dir`, `-o`: Specify output directory (default: ./workflows)
- `--name`: Custom name for the workflow file

### Running a Workflow

Use the `run` command to execute a workflow in a container:

```bash
fnkt run path/to/workflow.py
```

Options:

- `--container`: Container runtime to use (default: e2b)
- `--artifacts`: Map files/directories between host and container (format: local_path:container_path)

Example with artifacts:

```bash
fnkt run workflow.py --artifacts "data:/data" --artifacts "output:/output"
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key for LLM integration
- `FNKT_CONTAINER_RUNTIME`: Default container runtime (optional)

## Development

1. Clone the repository
2. Create a virtual environment and activate it
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Run tests:
   ```bash
   pytest
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.
