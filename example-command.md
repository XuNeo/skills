---
description: An example command demonstrating the basic structure and format
argument-hint: "<required-arg> [optional-arg]"
allowed-tools: Bash(*), Read, Write, Grep
---

# Example Command

This is an example command that demonstrates the basic structure and format for creating custom slash commands.

## Parameters

- **$1** (required): The first required argument
- **$2** (optional): An optional argument that can be used to modify behavior

## Workflow

### Step 1: Validate Input

Check that the required argument ($1) is provided. If not, prompt the user for it.

### Step 2: Process the Request

Use the provided arguments to perform the requested task.

### Step 3: Provide Output

Return clear, formatted results to the user.

## Example Usage

```bash
# With required argument only
/example-command "my input"

# With both required and optional arguments
/example-command "my input" "optional parameter"
```

## Error Handling

- If $1 is not provided, ask the user for the required argument
- If the command fails, provide a clear error message and suggest next steps

## Notes

- This command demonstrates the basic structure
- Customize the workflow, parameters, and tools for your specific use case
- The `allowed-tools` field specifies which tools this command can use
