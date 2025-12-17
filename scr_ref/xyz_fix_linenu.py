#!/usr/bin/env python3
"""
xyz_fix_linenu - Fix Line Counts in .ref Files

Updates the line count at the beginning of each frame in concatenated .ref files.
The line count includes all atom lines, NetF, Torq, and M-site lines in that frame.
"""

import sys

def print_help():
    """Print help message."""
    print("""
=== xyz_fix_linenu - Fix Line Counts in .ref Files ===

PURPOSE:
  Updates line counts in .ref files to reflect the actual number of lines
  in each frame (including atoms, NetF, Torq, and M-site lines).

USAGE:
  xyz_fix_linenu [input_ref_file]

  Example: xyz_fix_linenu system.ref > system_fixed.ref

  If input_ref_file is not provided, reads from stdin.

FILE FORMAT:
  The script expects .ref files with frames in this format:
    <line_count>
    <comment_line>
    <atom_lines...>
    <NetF_line>
    <Torq_line>
    <line_count>
    <comment_line>
    ...

  The line count represents the number of lines following the comment line
  until the next line count (or EOF).
""")

def is_line_count(line):
    """Check if line is a line count (single integer)."""
    parts = line.strip().split()
    if len(parts) == 1:
        try:
            int(parts[0])
            return True
        except ValueError:
            return False
    return False

def main():
    """Main function."""
    if '-h' in sys.argv or '--help' in sys.argv:
        print_help()
        sys.exit(0)

    input_file = sys.argv[1] if len(sys.argv) > 1 else None

    # Open input
    if input_file:
        try:
            f = open(input_file, 'r')
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found", file=sys.stderr)
            sys.exit(1)
    else:
        f = sys.stdin

    # Read all lines
    lines = f.readlines()
    if f != sys.stdin:
        f.close()

    # Process frames
    i = 0
    frames = []

    while i < len(lines):
        line = lines[i]

        # Check if this is a line count line
        if is_line_count(line):
            frame_start = i
            i += 1

            # Next line should be comment
            if i < len(lines):
                comment_line = lines[i]
                i += 1

                # Collect all lines until next line count or EOF
                frame_lines = []
                while i < len(lines) and not is_line_count(lines[i]):
                    frame_lines.append(lines[i])
                    i += 1

                # Store frame info
                frames.append({
                    'count_line_index': frame_start,
                    'comment': comment_line,
                    'lines': frame_lines,
                    'actual_count': len(frame_lines)
                })
        else:
            # Shouldn't happen in well-formed file, but skip
            i += 1

    # Output corrected file
    for frame in frames:
        sys.stdout.write(f"{frame['actual_count']}\n")
        sys.stdout.write(frame['comment'])
        for line in frame['lines']:
            sys.stdout.write(line)

if __name__ == '__main__':
    main()
