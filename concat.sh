#!/usr/bin/env zsh
# This script recursively finds files with extensions .py, .md, and .toml,
# skipping any ignored folders, and concatenates their contents into a single output file.
#
# Usage:
#   ./concat_files.zsh [-o output_file] [-i comma,separated,ignored,dirs]
#
# Options:
#   -o   Specify the output file (default: ./all-files.txt)
#   -i   Comma-separated list of directories to ignore (relative to current folder)

# Default output file and empty list for ignored directories.
output_file="./all-files.txt"
ignored_dirs=()

# Parse command line options.
while getopts "o:i:" opt; do
  case $opt in
    o)
      output_file="$OPTARG"
      ;;
    i)
      # Split comma-separated string into an array.
      IFS=',' read -rA ignored_dirs <<< "$OPTARG"
      ;;
    *)
      echo "Usage: $0 [-o output_file] [-i comma,separated,ignored,dirs]"
      exit 1
      ;;
  esac
done

# Clear (or create) the output file.
> "$output_file"

# Build the arguments for the find command.
# If there are ignored directories, we build a prune expression.
find_args=()
if (( ${#ignored_dirs} > 0 )); then
  prune_expr=()
  for dir in $ignored_dirs; do
    # We want to exclude both the directory itself and anything under it.
    prune_expr+=(-path "./$dir" -o -path "./$dir/*" -o)
  done
  # Remove the trailing "-o".
  unset 'prune_expr[-1]'
  # Add the prune expression to the find args.
  find_args+=( \( ${prune_expr[@]} \) -prune -o )
fi

# Add the file type filtering: .py, .md, or .toml.
find_args+=( -type f \( -iname "*.py" -o -iname "*.md" -o -iname "*.toml" \) -print )

# Run the find command and process each file.
while IFS= read -r file; do
  # Remove the leading "./" for a cleaner relative path in the delimiter.
  rel_path=${file#./}
  # Print a delimiter with the file's relative path.
  echo "------ $rel_path ------" >> "$output_file"
  # Append the file contents.
  cat "$file" >> "$output_file"
  # Optionally, add an extra newline between files.
  echo >> "$output_file"
done < <(find . "${find_args[@]}")

echo "All matching files have been concatenated into $output_file"
