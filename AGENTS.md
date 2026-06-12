## For Every task
 
### docs/CURRENT_TASK.md
Keep this file up to date at all times. It should always reflect exactly what is happening right now and should be updated
before working on the step:
- The current step number and name
- What you are actively working on
- Any blockers or decisions being made
- What the next step will be

Overwrite it completely each time you move to a new step. It should never describe a completed step — only the live current state.

### docs/CHANGELOG.md
Append an entry after every commit. Each entry should include:
- The step number and commit message
- A plain-English summary of what was built
- Any refactors or improvements made beyond the spec (see below)
- Any deviations from the spec and why

**Move anything from the next section that is not completed to `docs/TODO.md`** 



---
 
**Output a commit message, commit and push to the current github branch:**
```
<type>(<scope>): <summary>
- <what changed>
```
Types: `feat` `fix` `test` `refactor` `chore` `docs`
 
---

- Never commit secrets, keys, or credentials — use .env
