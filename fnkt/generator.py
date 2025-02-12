#!/usr/bin/env python3
"""Workflow generator using LiteLLM."""
import os
import re
from litellm import completion
from pathlib import Path

def clean_generated_code(code):
    """
    Remove markdown formatting and clean up indentation.
    """
    # Remove markdown code fences (``` and ```python)
    code = re.sub(r'```(?:python)?', '', code)
    # Remove markdown headers (lines starting with '# ')
    code = re.sub(r'^#+\s+', '', code, flags=re.MULTILINE)
    # Clean up empty lines
    code = re.sub(r'\n\s*\n+', '\n\n', code)
    return code.strip()

def normalize_indentation(code):
    """
    Normalize indentation of code blocks to use 4 spaces.
    """
    lines = code.split('\n')
    # Find the minimum indentation level (excluding empty lines)
    min_indent = float('inf')
    for line in lines:
        if line.strip():
            leading_spaces = len(line) - len(line.lstrip())
            min_indent = min(min_indent, leading_spaces)
    
    if min_indent == float('inf'):
        return code
    
    # Remove the common indentation from all lines
    normalized_lines = []
    for line in lines:
        if line.strip():
            normalized_lines.append(line[min_indent:])
        else:
            normalized_lines.append(line)
    
    return '\n'.join(normalized_lines)

def create_filename_from_description(description):
    """
    Create a filename-friendly slug from the workflow description.
    """
    # Convert to lowercase and replace spaces/special chars with underscores
    slug = description.lower()
    # Remove any special characters except alphanumeric and spaces
    slug = re.sub(r'[^a-z0-9\s]', '', slug)
    # Replace spaces with underscores and limit length
    slug = re.sub(r'\s+', '_', slug)[:50]  # Limit to 50 chars
    return f"{slug}.py"

def generate_workflow(description, output_dir, name=None):
    """Use an LLM to generate a self-contained Python workflow."""
    # Load the example workflow
    example_path = Path(__file__).parent.parent / "workflows" / "download_images.py"
    with open(example_path, 'r') as f:
        example_code = f.read()

    prompt = (
        f"Generate a self-contained Python script that implements the following task:\n"
        f"{description}\n\n"
        f"Below is an example of a well-structured workflow script. Your generated script should follow "
        f"similar patterns and best practices, but implement the requested functionality:\n\n"
        f"EXAMPLE SCRIPT:\n{example_code}\n\n"
        f"Requirements for your generated script:\n"
        f"1. Must be a completely self-contained Python script that can run in a container\n"
        f"2. Must include proper command-line argument handling using argparse\n"
        f"3. Must include a setup_dependencies() function that installs required packages at runtime\n"
        f"4. Must handle artifacts properly (input/output paths) using the --artifacts argument\n"
        f"5. Must include comprehensive error handling and logging\n"
        f"6. Must use consistent 4-space indentation\n"
        f"7. Must include clear comments and docstrings\n"
        f"8. Must specify all package dependencies with versions\n\n"
        f"**Do not use any markdown formatting or code fences; output only valid Python code.**\n"
    )

    # Call the LLM
    response = completion(
        model="openai/o1-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    
    # Clean and normalize the generated code
    code = clean_generated_code(response.choices[0].message.content)
    code = normalize_indentation(code)

    # Generate filename if not provided
    if not name:
        name = create_filename_from_description(description)
    elif not name.endswith(".py"):
        name += ".py"

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define the full path for the output file
    output_file_path = os.path.join(output_dir, name)

    # Write the generated code to the specified output directory
    with open(output_file_path, 'w') as file:
        file.write(code)

    return output_file_path
