#!/usr/bin/env python3
"""Workflow generator using LiteLLM."""
import os
import uuid
import re
from litellm import completion
from jinja2 import Template

WORKFLOW_TEMPLATE = """#!/usr/bin/env python3
\"\"\"{{ description }}\"\"\"

{{ helper_functions }}

def setup_dependencies():
    \"\"\"
    Install any missing dependencies required by the workflow.
    This function will attempt to install packages using pip.
    \"\"\"
    import subprocess
    import sys
    # List your required packages here. The LLM should add any additional ones needed.
    required_packages = [
        "requests",
        "Pillow",
        "beautifulsoup4"
    ]
    for pkg in required_packages:
        try:
            # For packages with different import names, adjust accordingly (e.g., 'beautifulsoup4' vs. 'bs4')
            if pkg == "beautifulsoup4":
                __import__("bs4")
            else:
                __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def main():
    # Ensure all dependencies are installed.
    setup_dependencies()
    # Initialize external artifacts if the function is provided.
    if 'init_artifacts' in globals():
        init_artifacts()
    {{ workflow_logic }}

if __name__ == '__main__':
    main()
"""

def clean_generated_code(code):
    """
    Remove markdown formatting (e.g., triple backticks) and any extraneous markdown symbols.
    """
    # Remove markdown code fences (``` and ```python)
    code = re.sub(r'```(?:python)?', '', code)
    # Remove markdown headers (lines starting with '# ')
    code = re.sub(r'^#+\s+', '', code, flags=re.MULTILINE)
    return code.strip()

def generate_workflow(description, output_dir, name=None):
    """Use an LLM to generate a self-contained Python workflow."""
    prompt = (
        f"Generate a self-contained Python script that implements the following task:\n"
        f"{description}\n"
        f"Requirements:\n"
        f"1. Include all necessary helper functions and required imports at the top.\n"
        f"2. Include a setup_dependencies() function that installs missing packages at runtime using pip.\n"
        f"3. Include a main() function that first calls setup_dependencies(), then an optional init_artifacts() function, "
        f"and finally executes the workflow logic.\n"
        f"4. Include proper error handling and logging.\n"
        f"5. **Do not use any markdown formatting or code fences; output only valid Python code.**\n"
        f"Separate your response into two sections marked by the exact tokens:\n"
        f"HELPER_FUNCTIONS:\n"
        f"WORKFLOW_LOGIC:\n"
    )

    # Call the LLM
    response = completion(
        model="openai/o1-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    
    # Parse and clean the response
    content = response.choices[0].message.content
    content = clean_generated_code(content)
    
    helper_section = ""
    workflow_section = ""
    
    if "HELPER_FUNCTIONS:" in content and "WORKFLOW_LOGIC:" in content:
        parts = content.split("WORKFLOW_LOGIC:")
        helper_section = parts[0].replace("HELPER_FUNCTIONS:", "").strip()
        workflow_section = parts[1].strip()
    else:
        # Fallback if the response isn't properly formatted
        helper_section = "# No helper functions provided"
        workflow_section = content.strip()

    # Generate the complete script using the template
    template = Template(WORKFLOW_TEMPLATE)
    code = template.render(
        description=description,
        helper_functions=helper_section,
        workflow_logic=workflow_section
    )

    # Clean the final code to ensure no markdown remains
    code = clean_generated_code(code)

    # Generate filename if not provided
    if not name:
        name = f"workflow_{uuid.uuid4().hex[:8]}.py"
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
