# Blender OpenCode Project

Blender scripting and molecular visualization project. Uses headless `bpy` (Blender 5.0) and MolecularNodes via a uv-managed Python 3.11 environment.

## Environment

**All scripts run headless via `uv run`.** No Blender GUI installation required.

```bash
# Run any script
uv run python scripts/my_script.py

# Run with arguments
uv run python scripts/render_protein.py --pdb 4ozs --output render.png

# Run tests
uv run pytest tests/

# One-liner
uv run python -c "import molecularnodes as mn; mol = mn.Molecule.fetch('4ozs')"
```

- **Python**: 3.11 (exact — required by bpy)
- **bpy**: 5.0.1 (headless, `bpy.app.background == True`)
- **molecularnodes**: 4.5.10 (with Biotite + MDAnalysis backends)
- **numpy**: pinned to 1.26.x (required by bpy)
- Dependencies managed in `pyproject.toml`, locked in `uv.lock`

**Never install packages manually.** Add dependencies to `pyproject.toml` and run `uv lock && uv sync`.

## Project Structure

```
.
├── pyproject.toml         # Dependencies and project metadata
├── uv.lock                # Locked dependency versions
├── opencode.json          # OpenCode configuration
├── AGENTS.md              # This file — project rules
├── .opencode/
│   └── skills/            # Reusable skill definitions (blender-api, molecular-nodes, skill-creator)
├── scripts/               # Standalone Blender Python scripts
├── addons/                # Blender addon packages
├── tests/                 # Test files
└── workspace/
    └── tmp/{session-id}/  # Ephemeral per-session artifacts (renders, exports, intermediate files)
```

## Workspace Convention

All output artifacts (rendered images, exported meshes, .blend files, intermediate data) go into `workspace/tmp/{session-id}/` where `{session-id}` is a unique identifier per task or session. This keeps the project root clean and makes artifacts easy to find and clean up.

**Rules:**
1. **Always create a session directory** before writing any output. Use a short descriptive ID (e.g., `workspace/tmp/protein-4ozs-render/`, `workspace/tmp/trajectory-analysis/`).
2. **Never write artifacts to the project root**, `scripts/`, or any other directory.
3. **Set render output paths** to the session directory:
   ```python
   import os
   session_dir = "workspace/tmp/my-session"
   os.makedirs(session_dir, exist_ok=True)
   canvas.snapshot(path=os.path.join(session_dir, "render.png"))
   ```
4. **The workspace/tmp/ directory is gitignored.** Artifacts are ephemeral and not committed.
5. **Scripts themselves** go in `scripts/`. Only their output goes in `workspace/tmp/`.

## Code Standards

- Python 3.11 only (matches bpy requirement)
- All scripts run headless — never assume a GUI viewport exists
- Use `bpy` for all Blender API interactions
- Use `molecularnodes` (`mn`) for molecular data
- Use snake_case for functions and variables, PascalCase for classes
- Use type annotations for function signatures
- Follow Blender addon conventions for addons: `bl_info`, `register()`/`unregister()`
- Prefix operator classes with `OT_`, panel classes with `PT_`, menu classes with `MT_`

## Headless Rules

All code in this project runs in headless mode (`bpy.app.background == True`). Follow these rules:

1. **No viewport operations.** `bpy.context.area`, `.region`, `.screen` are all `None`. Do not use `bpy.ops.view3d.*`, `bpy.ops.screen.*`, `bpy.ops.node.*`, or `bpy.ops.render.opengl()`.
2. **Use direct API, not operators** where possible. Create nodes via `node_tree.nodes.new()`, link via `node_tree.links.new()`, position camera via `camera.location = ...`.
3. **Render with `bpy.ops.render.render(write_still=True)`** or `mn.Canvas.snapshot()`. Never `render.opengl()`.
4. **No MolecularNodes annotations.** All `t.annotations.add_*()` methods are GPU viewport overlays — they silently fail headless.
5. **Use `mn.Canvas`** for scene/camera/render management — it handles headless correctly.

## Skills

This project has three skills in `.opencode/skills/`:

| Skill | Purpose |
|-------|---------|
| `blender-api` | Blender 5.0 Python API reference (bpy, bmesh, mathutils, operators) |
| `molecular-nodes` | MolecularNodes API for molecular visualization (Molecule, Trajectory, Canvas, Styles) |
| `skill-creator` | How to create new skills |

Use the `blender-api` and `molecular-nodes` skills together when writing scripts. Both include GUI vs headless compatibility tables.

## Common Pitfalls

- Never access `bpy.context` during module import; it is not available yet
- `bpy.data` objects can become invalid after undo/redo; always re-fetch references
- Mesh data must be accessed in the correct mode (OBJECT vs EDIT mode)
- Use `bmesh` for efficient mesh manipulation; remember to call `bmesh.free()` when done
- `StyleSpheres(geometry="Point")` is Cycles-only — use `"Instance"` for EEVEE
- `Molecule` uses `MoleculeSelector`, `Trajectory` uses MDAnalysis selection strings — do not mix them
