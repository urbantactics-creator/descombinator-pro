---
name: prompt-engineer
description: >-
  Prompt engineering, LLM interaction design, prompt optimization, and
  AI agent instruction crafting for the Descombinator Pro project.
license: MIT
metadata:
  category: ai
  project: descombinator-pro
---

# Prompt Engineer

## Responsibilities

- Design and optimize prompts for AI agents
- Create instruction sets for automated tasks
- Engineer prompts for code generation and review
- Test and iterate on prompt effectiveness
- Document prompt patterns and best practices

## Prompt Design Principles

1. **Clear Role Definition** — Specify the agent's role and expertise
2. **Context Provision** — Provide relevant project context
3. **Specific Instructions** — Use precise, actionable language
4. **Output Format** — Specify expected output structure
5. **Constraints** — Define boundaries and limitations

## Prompt Structure

```
[Role] You are a senior {role} with expertise in {domain}.

[Context] The project is {project_name}, a {description}.

[Task] Your task is to {specific_task}.

[Instructions] Follow these guidelines:
1. {guideline_1}
2. {guideline_2}
3. {guideline_3}

[Output] Provide your response in the following format:
{output_format}
```

## Skill Prompt Template

Each skill in `.kilo/skills/` follows this structure:

```markdown
---
name: {skill-name}
description: >-
  {concise description of the skill's purpose}
license: MIT
metadata:
  category: {category}
  project: descombinator-pro
---

# {Skill Name}

## Responsibilities
- {responsibility_1}
- {responsibility_2}

## Key Sections
- {section_1}
- {section_2}
```

## Prompt Optimization

### Techniques

- **Chain-of-Thought** — Ask for step-by-step reasoning
- **Few-shot Learning** — Provide examples in the prompt
- **Role Prompting** — Assign specific roles to the AI
- **Constraint Prompting** — Define clear boundaries

### Evaluation

- Test prompts with multiple iterations
- Measure output quality and consistency
- Gather feedback from users
- Refine based on results

## Agent Instructions

### AGENTS.md

The project uses `AGENTS.md` for agent instructions. Key sections:

1. **Project Overview** — What the project does
2. **Architecture** — Module structure and patterns
3. **Coding Standards** — Style and conventions
4. **Testing** — Test framework and practices
5. **Workflow** — Development and deployment process
