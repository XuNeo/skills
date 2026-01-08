# Personal Skills Repository

A collection of custom agent skills and slash commands for Claude Code and MiCode.

## Directory Structure

```
.
├── skills/           # Agent skills (directories with SKILL.md files)
├── commands/         # Custom slash commands
├── README.md         # This file
└── .gitignore        # Git ignore rules
```

## Skills

Skills are directories containing a `SKILL.md` file with instructions and metadata that Claude loads dynamically to improve performance on specialized tasks. Scripts and supporting files should live inside the skill directory.

### Creating a New Skill

1. Create a new directory in `skills/`:
   ```bash
   mkdir skills/my-skill
   ```

2. Create a `SKILL.md` file in that directory:
   ```bash
   touch skills/my-skill/SKILL.md
   ```

3. Add YAML frontmatter and instructions:
   ```markdown
   ---
   name: my-skill
   description: Brief description of what this skill does
   license: MIT
   ---

   # My Skill

   Detailed instructions for Claude...
   ```

4. Add any scripts or supporting files to the skill directory:
   ```bash
   # Example: Add a helper script
   touch skills/my-skill/helper.sh
   ```

5. The skill will be automatically available in Claude Code and MiCode.

## Commands

Custom slash commands provide reusable workflows for common tasks.

### Creating a New Command

1. Create a new `.md` file in `commands/`:
   ```bash
   touch commands/my-command.md
   ```

2. Add YAML frontmatter and instructions:
   ```markdown
   ---
   description: Brief description of what this command does
   argument-hint: "<required-arg> [optional-arg]"
   allowed-tools: Bash(*), Read, Write
   ---

   # My Command

   Instructions for Claude...
   ```

3. Use the command in Claude Code with `/my-command`

## Integration

### Claude Code

Commands are linked to `~/.claude/commands-custom` and automatically available.

Skills can be loaded from the `skills/` directory.

### MiCode

Configure MiCode to load skills from the `skills/` directory.

## License

This repository contains personal skills and commands. Each skill may have its own license specified in its `SKILL.md` file.

## Contributing

This is a personal repository for custom skills and commands. Feel free to fork and adapt for your own use.
