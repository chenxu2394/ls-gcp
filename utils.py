def parse_stdout(output):
    result_dict = {}
    lines = output.strip().split("\n")
    for line in lines:
        if line.strip():  # Ensures the line is not empty
            parts = line.split()
            try:
                # Assuming that the key is always a string followed by an integer value
                key = " ".join(parts[:-1])
                value = int(parts[-1])
                result_dict[key] = value
            except ValueError:
                # Handle cases where conversion to int fails (non-integer outputs are ignored)
                continue
    return result_dict