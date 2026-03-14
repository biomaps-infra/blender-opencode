---
name: blender-molecular_nodes
description: MolecularNodes (MN) Python API and Geometry Nodes reference for molecular visualization in Blender. Use this skill whenever working with molecular data in Blender — including importing PDB/mmCIF/SDF structures, molecular dynamics trajectories via MDAnalysis, CryoEM density maps, protein visualization styles (cartoon, ribbon, spheres, surface, ball-and-stick), molecular selections, animation, and rendering. Also use when the user mentions molecularnodes, mn.Molecule, mn.Trajectory, mn.Canvas, molecular rendering, protein structures, PDB codes, AlphaFold, pLDDT, scientific visualization in Blender, or any molecular biology visualization task. This skill extends the blender-core_api skill — use both together when mixing general Blender scripting with molecular operations.
metadata:
    skill-author: Biomaps
---

# MolecularNodes — Blender Molecular Visualization

MolecularNodes (MN) is an open-source Blender addon for importing, visualizing, animating, and rendering molecular data. It uses Blender's Geometry Nodes system and ships ~160 custom nodes for molecular operations. The Python API (`molecularnodes` package) enables scripted workflows.

**Version**: This skill documents MolecularNodes as of early 2026, compatible with Blender 4.2+. The API is marked experimental and may change between releases.

**Backends**: Biotite (static structures) + MDAnalysis (trajectories)
**Install**: Inside Blender via Extensions platform, or `pip install molecularnodes[bpy]` (Python 3.11 only, numpy 1.26)

## Decision Trees

### "Which class do I use?"

```
User has molecular data
├── Static structure (PDB, mmCIF, SDF, MOL)?
│   └── mn.Molecule.fetch() or mn.Molecule.load()
├── MD simulation (trajectory files)?
│   └── mn.Trajectory(mda.Universe(topology, trajectory))
├── CryoEM density map (.map, .map.gz, .dx)?
│   └── mn.entities.density.io.load()
├── Live-streaming simulation (GROMACS)?
│   └── mn.Trajectory(mda.Universe(top, "imd://host:port"))
└── Starfile / ensemble data?
    └── mn.entities.Ensemble (see advanced API)
```

### "Which rendering engine?"

```
Need fast previews?
├── Yes → EEVEE (mn.scene.EEVEE())
│   ⚠ StyleSpheres geometry="Point" will NOT render — use "Instance" or "Mesh"
│   ⚠ Some MN materials look different in EEVEE
└── No, need publication quality?
    └── Cycles (mn.scene.Cycles(samples=32..256))
        ✓ All geometry types work
        ✓ Path-traced lighting, AO, reflections
```

### "Which style for my use case?"

| Goal | Style | Notes |
|------|-------|-------|
| Publication protein figure | `StyleCartoon` | Helices, sheets, loops. The standard. |
| Quick protein overview | `StyleRibbon` | Simpler, just alpha-carbon tube |
| Space-filling / VDW | `StyleSpheres` | Set `geometry="Instance"` for EEVEE |
| Ligand / small molecule | `StyleBallAndStick` | Set `bond_find=True` if bonds missing |
| Molecular surface | `StyleSurface` | Good with `TransparentOutline` material |
| Clean bond view | `StyleSticks` | Minimalist |
| Combined view | Multiple styles + `Join Geometry` | Use selections to partition |

### "Molecule selections: MoleculeSelector vs MDAnalysis strings?"

```
Working with mn.Molecule (static structure)?
├── Use MoleculeSelector: mn.MoleculeSelector().is_peptide().chain_id("A")
├── Or string shorthand: selection="is_peptide"
└── NOT MDAnalysis syntax — Molecule uses Biotite, not MDAnalysis

Working with mn.Trajectory (MD simulation)?
├── Use MDAnalysis selection strings: selection="resid 1 129 and name CA"
├── Or AtomGroup objects: selection=u.select_atoms("protein")
└── NOT MoleculeSelector — Trajectory uses MDAnalysis Universe
```

## Execution Context: GUI vs Headless

MolecularNodes code can run in three contexts. **Always determine the target context before generating code.**

| Context | How it runs | Detection |
|---------|------------|-----------|
| **GUI** | Interactive Blender with full UI | `bpy.context.area is not None` |
| **Background** | `blender --background --python script.py` | `bpy.app.background == True` |
| **Standalone** | `pip install molecularnodes[bpy]` (no Blender app) | `bpy.app.background == True` |

**Detection snippet** (include when context matters):
```python
import bpy
HEADLESS = bpy.app.background  # True for --background and standalone
```

### What works where

| Operation | GUI | Headless | Notes |
|-----------|-----|----------|-------|
| `Molecule.fetch()` / `.load()` | Yes | Yes | |
| `Trajectory()` | Yes | Yes | |
| `add_style()` (all styles) | Yes | Yes | |
| `Canvas.snapshot()` / `.animation()` | Yes | Yes | Core headless use case |
| `Canvas.frame_object()` / `.frame_view()` | Yes | Yes | |
| All style classes | Yes | Yes | |
| All material classes | Yes | Yes | |
| `MoleculeSelector` | Yes | Yes | |
| `store_named_attribute()` | Yes | Yes | |
| Density loading (`density.io.load()`) | Yes | Yes | |
| `StyleSpheres(geometry="Point")` | Yes* | Yes* | *Cycles only — invisible in EEVEE |
| **All annotations** (`add_atom_info`, `add_com`, `add_label_2d/3d`, etc.) | **Yes** | **No** | GPU viewport overlays — crash or no-op headless |
| **All `draw_*()` methods** (custom annotations) | **Yes** | **No** | GPU drawing requires active viewport |
| `add_com_distance(line_mode="mesh")` | Yes | Yes | Exception: mesh geometry renders headless |
| `add_simulation_box()` | **Yes** | **No** | Viewport overlay |
| `add_canonical_dihedrals()` | **Yes** | **No** | Viewport overlay |

### Key rules

1. **Annotations are GUI-only.** All `t.annotations.add_*()` methods draw GPU viewport overlays that require an active 3D viewport. In headless mode they either crash or produce nothing. The one exception: `add_com_distance(line_mode="mesh")` creates actual mesh geometry.

2. **Everything else works headless.** The entire Molecule/Trajectory/Canvas/Style/Material pipeline is headless-compatible. This is the recommended scripting workflow.

3. **For headless renders, use `Canvas.snapshot()`.** Do NOT use `bpy.ops.render.opengl()` (requires viewport). Use `Canvas.snapshot()` or `bpy.ops.render.render(write_still=True)`.

4. **`Select Cube` / `Select Sphere` GN nodes** technically evaluate headless but require interactively positioned Empty objects — practically GUI-only.

## Integration with blender-core_api

This skill covers MolecularNodes-specific operations. For general Blender Python, use `blender-core_api`. When both apply, read from both.

| Task | Which Skill | Specific Reference |
|------|------------|-------------------|
| General bpy scripting | `blender-core_api` | `core-api.md` |
| Mesh/BMesh manipulation | `blender-core_api` | `mesh-and-bmesh.md` |
| Custom shader materials for MN objects | `blender-core_api` | `materials-and-nodes.md` — assign via `mol.object.data.materials.append(mat)` |
| Geometry Nodes concepts (general) | `blender-core_api` | `geometry-nodes.md` — how to create/link node trees |
| MN custom nodes (Style, Select, Color) | `molecular-nodes` | `nodes-essential.md` |
| Modifiers on MN objects | `blender-core_api` | `modifiers-and-constraints.md` |
| Animation / keyframes on MN objects | `blender-core_api` | `handlers-and-timers.md` for frame handlers |
| Import PDB / style / render | `molecular-nodes` | `python-api-core.md` + `workflows-recipes.md` |
| MD trajectories, CryoEM density | `molecular-nodes` | `python-api-core.md` + `python-api-advanced.md` |
| Debugging render issues | Both | `molecular-nodes/gotchas.md` + `blender-core_api/gotchas-and-pitfalls.md` |

## Domain Router

Read the reference file(s) matching the user's task.

| Domain | Reference File | When to Read |
|--------|---------------|--------------|
| Gotchas & failure modes | `references/gotchas.md` | **Always read** when debugging, when things look wrong, or before generating substantial code |
| Core Python API | `references/python-api-core.md` | Molecule, Trajectory, Canvas classes, camera, rendering |
| Styles & Materials | `references/python-api-styles.md` | Style classes, material classes, MoleculeSelector, colors |
| Advanced API | `references/python-api-advanced.md` | Annotations, density loading, custom annotations, streaming |
| Essential Nodes | `references/nodes-essential.md` | The ~20 most-used nodes with examples and patterns |
| Full Node Catalog | `references/nodes-catalog.md` | Complete 160+ node reference (lookup only) |
| Data Formats & Attributes | `references/data-formats-attributes.md` | File formats, data sources, attribute tables, lookup tables |
| Workflows & Recipes | `references/workflows-recipes.md` | End-to-end examples: fetch+render, trajectory, density, RMSF |

**Always read `references/gotchas.md`** before generating MN code. It prevents the most common failures.

**Always read `references/workflows-recipes.md`** when the user wants a complete working example.

## Core Concepts

### Data Model
- **Atoms = Mesh Vertices** (points). Each atom is one vertex.
- **Bonds = Mesh Edges**. Each bond is one edge.
- All molecular properties stored as **Named Attributes** on the mesh.
- Strings (chain IDs, residue names, atom names) are stored as **integers** with lookup tables.

### World Scale
- **1 Angstrom = 1 cm** in Blender (scale factor `0.01`)
- Will change to 1 nm = 1 m in Blender 5.0 (scale factor `0.1`)

### Pipeline
```
Import/Fetch → [Select] → [Color] → [Style] → Rendered Geometry
```

Geometry Nodes flow left-to-right:
```
Group Input (Atomic Data) → Manipulation → Style Node → Group Output
```

Multiple styles combine via `Join Geometry`. Selection inputs accept Boolean fields.

### Key Attributes (stored per-atom on points)
| Attribute | Type | Description |
|-----------|------|-------------|
| `chain_id` | Int | Chain identifier (alphabetical, from 0) |
| `res_name` | Int | Residue name (ALA=0 ... VAL=19; DNA 30-33; RNA 40-43) |
| `res_id` | Int | Residue number within chain |
| `atomic_number` | Int | Periodic table number |
| `b_factor` | Float | Temperature factor / pLDDT for AlphaFold |
| `sec_struct` | Int | 0=non-protein, 1=helix, 2=sheet, 3=loop |
| `is_backbone` | Bool | Backbone atom flag |
| `is_peptide` | Bool | Peptide/protein flag |
| `Color` | Color | RGBA color |

Full attribute table in `references/data-formats-attributes.md`.

## Quick Recipes

### Fetch and render a protein
```python
import molecularnodes as mn

canvas = mn.Canvas(mn.scene.Cycles(samples=32), resolution=(720, 480))
mol = mn.Molecule.fetch("4ozs")
mol.add_style(mn.StyleCartoon())
canvas.frame_object(mol)
canvas.snapshot()
```

### AlphaFold with pLDDT coloring
```python
canvas = mn.Canvas(engine="eevee", resolution=(800, 800), transparent=True)
mol = mn.Molecule.fetch("Q8W3K0", database="alphafold")
mol.add_style(mn.StyleCartoon(), color="pLDDT", material=mn.material.AmbientOcclusion())
canvas.frame_view(mol)
canvas.snapshot()
```

### Load local file
```python
mol = mn.Molecule.load("/path/to/structure.pdb")
mol.add_style(mn.StyleRibbon())
```

### Multiple styles with selections
```python
mol = (
    mn.Molecule.fetch("8H1B")
    .add_style("cartoon", material=mn.material.AmbientOcclusion())
    .add_style(
        style="surface",
        selection=mn.MoleculeSelector().is_peptide(),
        color=(0.6, 0.6, 0.8, 1.0),
        material=mn.material.TransparentOutline()
    )
)
```

### MD trajectory
```python
import MDAnalysis as mda
from MDAnalysis.tests.datafiles import PSF, DCD

canvas = mn.Canvas(mn.scene.Cycles(samples=16), (800, 800), transparent=True)
u = mda.Universe(PSF, DCD)
traj = mn.Trajectory(u)
traj.add_style("cartoon")
traj.add_style("spheres", selection="resid 1 129")
canvas.frame_view(traj)
canvas.snapshot()
```

### Custom RMSF coloring
```python
import matplotlib.cm as cm
import numpy as np

# After RMSF analysis...
viridis = cm.get_cmap('inferno')
col_array = viridis(normalized_rmsf_values)
traj.store_named_attribute(col_array, "custom_color")
traj.add_style(mn.StyleRibbon(quality=6, backbone_radius=1.5), color="custom_color")
```

### CryoEM density
```python
d = mn.entities.density.io.load(
    file_path="density.map.gz",
    style="density_iso_surface",
    overwrite=True,
)
ds = d.styles[0]
ds.iso_value = 1.0
ds.show_contours = True
```

### Render animation
```python
canvas.frame_object(traj)
canvas.snapshot(frame=75)                           # Single frame
canvas.animation(frame_start=10, frame_end=50)      # Animation
```

### Camera control
```python
canvas.camera.lens = 150        # Zoom in
canvas.camera.lens = 35         # Zoom out
canvas.frame_view(mol, viewpoint="front")
canvas.frame_view(mol, (90, 0, -45))  # Custom angle (radians)
```

## Key Classes Summary

| Class | Purpose | Key Methods |
|-------|---------|-------------|
| `mn.Molecule` | Static structures (PDB, mmCIF, SDF) | `.fetch()`, `.load()`, `.add_style()`, `.get_view()` |
| `mn.Trajectory` | MD trajectories (MDAnalysis) | `.add_style()`, `.store_named_attribute()`, `.get_view()` |
| `mn.Canvas` | Scene/render controller | `.snapshot()`, `.animation()`, `.frame_object()`, `.clear()` |
| `mn.StyleCartoon` | Cartoon style (helices, sheets) | `quality`, `peptide_*`, `nucleic_*` params |
| `mn.StyleSpheres` | Space-filling VDW spheres | `geometry`, `radius`, `subdivisions` |
| `mn.StyleRibbon` | Tube through alpha carbons | `backbone_radius`, `quality` |
| `mn.StyleSurface` | Molecular surface | `probe_size`, `scale_radius` |
| `mn.StyleBallAndStick` | Atoms + bond cylinders | `sphere_radius`, `bond_radius`, `bond_find` |
| `mn.StyleSticks` | Clean stick representation | `radius` |

**Style shorthand strings** (for `add_style()`): `"cartoon"`, `"ribbon"`, `"spheres"`, `"surface"`, `"ball_and_stick"`, `"sticks"`, `"vdw"`

**Materials**: `mn.material.Default()`, `mn.material.AmbientOcclusion()`, `mn.material.FlatOutline()`, `mn.material.Squishy()`, `mn.material.TransparentOutline()`

**Color options**: `"common"` (default), `"pLDDT"`, `"element"`, `(r,g,b,a)` tuple, named attribute string (e.g. `"custom_color"`)

## Pitfalls Summary

See `references/gotchas.md` for the full list with fixes. Top 5:

1. **`geometry="Point"` is Cycles-only** — Use `"Instance"` or `"Mesh"` for EEVEE. This is the #1 "invisible molecule" cause.
2. **MoleculeSelector vs MDAnalysis strings** — `Molecule` uses `MoleculeSelector`. `Trajectory` uses MDAnalysis selection strings. Mixing them up produces silent failures.
3. **Density .vdb files** — Do not move/delete the intermediate `.vdb` files created on density import.
4. **`bond_find = True`** — Small molecules and ligands often lack bond data. Set `bond_find = True` on `StyleBallAndStick` or they render as disconnected spheres.
5. **Python 3.11 + numpy 1.26** — The standalone `pip install molecularnodes[bpy]` has strict version requirements.
