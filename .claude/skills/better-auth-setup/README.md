# Better-Auth Setup Skill

A reusable Claude Code skill for implementing better-auth authentication in FastAPI applications with microservices architecture.

## What is This?

This is a **Claude Code Skill** - a portable knowledge base that can be used across multiple projects. It contains:

- ✅ Production-ready templates for auth server and FastAPI integration
- ✅ Common issue solutions with auto-fix scripts
- ✅ Best practices and configuration patterns
- ✅ Comprehensive diagnostics and troubleshooting guides
- ✅ Helper scripts for schema sync and setup

## Structure

```
.claude/skills/better-auth-setup/
├── SKILL.md                    # Entry point (quick reference)
├── README.md                   # This file (portability guide)
├── templates/                  # Code templates with {{PLACEHOLDERS}}
│   ├── auth-server/           # Node.js auth server templates
│   ├── fastapi/               # FastAPI integration templates
│   ├── docker/                # Docker configs
│   └── docs/                  # Documentation templates
├── patterns/                   # Architecture patterns (to be added)
│   ├── AUTHENTICATION_FLOW.md
│   ├── SESSION_MANAGEMENT.md
│   └── DATABASE_SYNC.md
├── diagnostics/               # Common issues and solutions
│   └── COMMON_ISSUES.md       # All 6 common issues documented
├── examples/                  # Complete working examples (to be added)
│   ├── neon-vercel-example/
│   ├── supabase-railway-example/
│   └── local-docker-example/
└── scripts/                   # Helper scripts
    ├── sync-schemas.sh        # Prisma ↔ Alembic schema sync
    ├── setup-dev.sh           # (to be added)
    └── health-check.sh        # (to be added)
```

## Using the Skill

### Method 1: With better-auth-fastapi-agent (Recommended)

The skill is automatically referenced by the `better-auth-fastapi-agent`:

```bash
# In Claude Code
"Use the better-auth-fastapi-agent to set up authentication"
```

The agent will:
1. Reference this skill for patterns and templates
2. Generate code using skill templates
3. Run diagnostics using skill documentation
4. Apply fixes using skill scripts

### Method 2: Direct Reference

Claude can directly reference skill knowledge:

```bash
"According to the better-auth-setup skill, what's the correct route ordering for Express?"

"Show me the database validation pattern from better-auth-setup skill"

"Use the better-auth-setup skill to diagnose my 404 error on auth endpoints"
```

### Method 3: Use Templates Directly

```typescript
// Read template
const template = await readFile(
  '.claude/skills/better-auth-setup/templates/auth-server/src/auth/auth.config.ts.template'
);

// Replace placeholders
const config = template
  .replace('{{DATABASE_PROVIDER}}', 'postgresql')
  .replace('{{SESSION_EXPIRATION}}', '604800');
```

## Portability: Using in Other Projects

This skill is **project-independent** and designed for maximum reusability.

### Option A: Copy to New Project (Project-Level Skill)

```bash
# Copy skill to any FastAPI project
cp -r .claude/skills/better-auth-setup /path/to/new-project/.claude/skills/

# Now available in that project
cd /path/to/new-project
claude "Use better-auth-setup skill to implement authentication"
```

**When to use**: Project-specific customizations needed.

### Option B: Install Globally (System-Wide Skill)

```bash
# Install for ALL your projects
cp -r .claude/skills/better-auth-setup ~/.claude/skills/

# Now available everywhere!
cd any-project
claude "Use better-auth-setup skill"
```

**When to use**: Same configuration across all projects.

### Option C: Git Repository (Shareable Skill)

**Step 1**: Create a Git repo for the skill

```bash
cd .claude/skills/better-auth-setup
git init
git add .
git commit -m "Initial better-auth-setup skill"
git remote add origin https://github.com/yourusername/better-auth-setup-skill
git push -u origin main
```

**Step 2**: Install in any project

```bash
# Clone into project
git clone https://github.com/yourusername/better-auth-setup-skill \
  .claude/skills/better-auth-setup

# Or install globally
git clone https://github.com/yourusername/better-auth-setup-skill \
  ~/.claude/skills/better-auth-setup
```

**Step 3**: Stay updated

```bash
cd .claude/skills/better-auth-setup
git pull origin main
```

**When to use**: Share with team, version control, updates.

### Option D: NPM Package (Advanced)

```bash
# Package skill as npm module
cd .claude/skills/better-auth-setup
npm init -y
npm publish @yourusername/better-auth-setup-skill

# Install in projects
npm install -g @yourusername/better-auth-setup-skill
ln -s $(npm root -g)/@yourusername/better-auth-setup-skill ~/.claude/skills/better-auth-setup
```

**When to use**: Professional distribution, versioning, dependencies.

## Customizing for Your Organization

### 1. Update Templates with Defaults

Edit templates to include your organization's defaults:

```typescript
// templates/auth-server/src/auth/auth.config.ts.template

// Before (generic)
trustedOrigins: env.corsOrigins,

// After (your org's domains)
trustedOrigins: env.corsOrigins || [
  'https://app.yourcompany.com',
  'https://staging.yourcompany.com'
],
```

### 2. Add Custom Diagnostics

Add your organization-specific issues to `diagnostics/CUSTOM_ISSUES.md`:

```markdown
## Issue 7: Internal SSO Integration

### Symptom
SSO redirect fails with "Invalid issuer"

### Solution
Update auth.config.ts with company SSO endpoint...
```

### 3. Add Custom Scripts

```bash
# Add to scripts/
scripts/deploy-to-company-k8s.sh
scripts/sync-with-ldap.sh
```

### 4. Update SKILL.md

Update `SKILL.md` to reference your customizations:

```markdown
## Company-Specific Patterns

- SSO Integration: See `patterns/SSO_INTEGRATION.md`
- LDAP Sync: See `scripts/sync-with-ldap.sh`
```

## Versioning

### Semantic Versioning

Tag skill versions for tracking:

```bash
git tag -a v1.0.0 -m "Initial release"
git tag -a v1.1.0 -m "Added OAuth templates"
git push --tags
```

### Version-Specific Installation

```bash
# Install specific version
git clone -b v1.0.0 https://github.com/yourusername/better-auth-setup-skill \
  .claude/skills/better-auth-setup
```

### Compatibility Matrix

Document compatibility in `SKILL.md`:

| Skill Version | better-auth | FastAPI | Python | Node.js |
|---------------|-------------|---------|--------|---------|
| 1.0.0         | 1.0+        | 0.104+  | 3.12+  | 20+     |
| 1.1.0         | 1.1+        | 0.110+  | 3.12+  | 20+     |

## Maintenance

### Updating the Skill

**After updating templates or docs**:

```bash
cd .claude/skills/better-auth-setup

# Commit changes
git add .
git commit -m "Updated cookie configuration template"

# Tag new version
git tag -a v1.0.1 -m "Fix: Cookie SameSite policy"
git push --tags

# Notify users
echo "New version available: v1.0.1" > CHANGELOG.md
```

### Testing Changes

Before publishing updates:

```bash
# Test in isolated project
mkdir /tmp/test-project
cp -r .claude/skills/better-auth-setup /tmp/test-project/.claude/skills/
cd /tmp/test-project

# Run agent with updated skill
claude "Use better-auth-fastapi-agent to test the setup"
```

## Contributing

### Adding New Templates

1. Create template in `templates/` with `{{PLACEHOLDERS}}`
2. Document placeholders in comments
3. Test generation in real project
4. Update `SKILL.md` with template reference

### Adding Diagnostics

1. Document issue in `diagnostics/COMMON_ISSUES.md`
2. Include: symptom, root cause, solution, auto-fix, verification
3. Add to diagnostic checklist
4. Create auto-fix script if possible

### Adding Examples

1. Create complete working example in `examples/`
2. Include README with setup instructions
3. Test from scratch in clean environment
4. Document in `SKILL.md`

## FAQ

### Q: Can I use this skill without the agent?

**Yes!** The skill is standalone. Claude can reference it directly:

```
"Show me the session management pattern from better-auth-setup skill"
```

### Q: Can I use this with other agents?

**Absolutely!** Any agent can reference this skill:

```markdown
---
name: my-custom-auth-agent
---

When implementing authentication:
1. Reference better-auth-setup skill for patterns
2. Use templates from skill directory
3. Run diagnostics from skill docs
```

### Q: How do I keep multiple projects in sync?

**Option 1**: Install globally (`~/.claude/skills/`) - all projects use same version

**Option 2**: Git submodule in each project - pull updates as needed

**Option 3**: Symlink to global installation

```bash
ln -s ~/.claude/skills/better-auth-setup .claude/skills/better-auth-setup
```

### Q: Can I customize templates per-project?

**Yes!** Two approaches:

1. **Override in project**: Create project-specific template
```
.claude/skills/better-auth-setup/templates/auth.config.ts.template  # Skill default
.claude/templates/auth.config.ts.template                           # Project override
```

2. **Fork the skill**: Make project-specific copy and customize

### Q: How do I share this with my team?

1. Push to GitHub (public or private repo)
2. Share installation command:
```bash
git clone https://github.com/yourteam/better-auth-setup-skill \
  .claude/skills/better-auth-setup
```

3. Or add to company's internal package registry

## License

MIT License - Feel free to customize and redistribute!

## Related

- **Agent**: `.claude/agents/better-auth-fastapi-agent.md`
- **better-auth Documentation**: https://docs.better-auth.com
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Prisma Documentation**: https://www.prisma.io/docs

## Support

- Issues: File in GitHub repo
- Questions: Reference this skill in Claude Code
- Updates: Watch GitHub repo for new versions
