# Scientific Computing & 3D Visualization Platform

Comprehensive scientific research platform combining end-to-end workflows from database access to professional 3D molecular visualization. Serves academic institutions and pharmaceutical/biotech companies with integrated analysis, visualization, and publication capabilities using headless Blender 5.0 and MolecularNodes via a uv-managed Python 3.11 environment.

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

### Scientific Domain Installation

```bash
# Core scientific platform
uv sync --extra databases --extra analysis

# Bioinformatics workflow (single-cell, genomics, proteomics)
uv sync --extra bioinformatics --extra visualization

# Drug discovery pipeline (chemistry, ML, 3D visualization)
uv sync --extra databases --extra machine-learning --extra visualization

# Clinical research (trials, statistical analysis, reporting)
uv sync --extra databases --extra workflows --extra documentation
```

## Project Structure

```
.
├── pyproject.toml         # Dependencies and project metadata
├── uv.lock                # Locked dependency versions
├── Claude.json          # Claude Code configuration
├── AGENTS.md              # This file — project rules
├── .opencode/
│   └── skills/            # Reusable skill definitions (blender-api, molecular-nodes, skill-creator)
├── scripts/               # Standalone Blender Python scripts
├── addons/                # Blender addon packages
├── tests/                 # Test files
└── workspace/
    └── tmp/{session-id}/  # Ephemeral per-session artifacts (renders, exports, intermediate files)
```

## Scientific Capabilities

This platform provides **177 scientific skills** across 13 domains, enabling complete research workflows:

| Domain | Skills | Purpose |
|--------|--------|---------|
| **databases** (`db-*`) | 36 skills | Scientific data sources (PubMed, AlphaFold, ChEMBL, UniProt) |
| **libraries** (`lib-*`) | 60+ skills | Python scientific stack (SciPy, PyTorch, RDKit, Scanpy) |
| **bioinformatics** (`bio-*`) | 17 skills | Life sciences tools (single-cell, MD simulations, phylogenetics) |
| **analysis** (`analysis-*`) | 10 skills | Statistical analysis and hypothesis generation |
| **visualization** (`viz-*`) | 6 skills | Publication-ready scientific graphics |
| **documentation** (`doc-*`) | 12 skills | Scientific writing and manuscript preparation |
| **workflows** (`workflow-*`) | 8 skills | Clinical decision support and research management |
| **services** (`service-*`) | 16 skills | Lab automation and cloud platforms (Opentrons, Benchling) |
| **machine-learning** (`ml-*`) | 5 skills | Specialized ML for scientific applications |

### Example Research Workflows

**Protein Structure Analysis** (Academic/Pharma):
```python
# 1. Fetch AlphaFold structure → 2. 3D visualization → 3. Publication render
mol = mn.Molecule.fetch("P04637")  # p53 protein
canvas = mn.Canvas(); canvas.add(mol, style="cartoon")
canvas.snapshot("p53_structure.png", samples=128)  # Cycles rendering
```

**Drug Discovery Pipeline** (Pharmaceutical):
```python
# 1. ChEMBL target search → 2. Chemical analysis → 3. Docking → 4. 3D results
from db_chembl import query_target
from lib_rdkit import filter_druglike
from bio_diffdock import dock_compounds
# → 3D visualization of binding poses with Blender + MolecularNodes
```

**Clinical Research** (Healthcare):
```python
# 1. ClinicalTrials.gov → 2. Statistical analysis → 3. Decision support
from db_clinicaltrials import search_trials
from analysis_statistical_analysis import survival_analysis
from workflow_clinical_decision_support import generate_recommendations
```

## 3D Molecular Visualization

Professional molecular visualization powered by **Blender 5.0** + **MolecularNodes 4.5.10**:

- **Publication-quality rendering** using Cycles engine with path tracing
- **Molecular dynamics animations** from MD simulation trajectories
- **Multiple representation styles**: cartoon, surface, spheres, ball-and-stick
- **CryoEM density maps** and **AlphaFold confidence visualization** (pLDDT)
- **Headless automation** for high-throughput structure analysis
- **Professional lighting** and **camera controls** for scientific imaging

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

This project has three core skills in `.opencode/skills/`:

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
