# Agent Skills Repository

A collection of custom agent skills following the [Agent Skills](https://agentskills.io) specification.

## Directory Structure

```
.
├── <skill-name>/     # Each skill is a directory with SKILL.md
│   ├── SKILL.md      # Required: skill definition
│   ├── scripts/      # Optional: executable scripts
│   ├── references/   # Optional: documentation
│   └── assets/       # Optional: static resources
├── README.md
└── .gitignore
```

## Skills

Skills are directories containing a `SKILL.md` file with YAML frontmatter and Markdown instructions. Claude loads them dynamically to improve performance on specialized tasks.

### Creating a New Skill

1. Create a new directory:
   ```bash
   mkdir my-skill
   ```

2. Create a `SKILL.md` file:
   ```markdown
   ---
   name: my-skill
   description: Brief description of what this skill does
   license: MIT
   ---

   # My Skill

   Detailed instructions for Claude...
   ```

3. Add optional resources:
   - `scripts/` - Executable code (Python/Bash/etc.)
   - `references/` - Documentation loaded on demand
   - `assets/` - Static files used in output

## License

Each skill may have its own license specified in its `SKILL.md` file.
