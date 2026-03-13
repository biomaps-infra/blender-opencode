# Python API — Core Classes

## Table of Contents
1. [Molecule](#molecule)
2. [Trajectory](#trajectory)
3. [Canvas](#canvas)
4. [Camera](#camera)
5. [Scene Engines](#scene-engines)
6. [Session Management](#session-management)

---

## Molecule

Primary class for static molecular structures. Backend: **Biotite** (`AtomArray`).

### Class Methods

```python
mn.Molecule.fetch(
    code: str,                    # PDB code (e.g., "4ozs") or UniProt ID for AlphaFold
    format: str = '.bcif',        # Download format: '.bcif', '.pdb', '.cif'
    centre: str | None = None,    # Centering method: 'centroid', 'mass', or None
    remove_solvent: bool = True,  # Remove water molecules
    cache = download.CACHE_DIR,   # Cache directory (~/.MolecularNodes/)
    database: str = 'rcsb',       # 'rcsb' or 'alphafold'
) -> Molecule
```

```python
mn.Molecule.load(
    file_path: str,               # Path to local file (.pdb, .cif, .bcif, .sdf, .mol)
    name: str | None = None,      # Object name in Blender
    remove_solvent: bool = True,
) -> Molecule
```

### Instance Methods

```python
mol.add_style(
    style = 'spheres',            # Style class instance or shorthand string
    color = 'common',             # Color scheme: 'common', 'pLDDT', 'element', (r,g,b,a) tuple, named attribute
    selection = None,             # MoleculeSelector, string shorthand, or None (all atoms)
    assembly: bool = False,       # Apply biological assembly
    material = None,              # Material class instance or string (e.g., "MN Transparent Outline")
    name: str | None = None,      # Style name
) -> Molecule                     # Returns self for method chaining
```

```python
mol.assemblies(as_array: bool = False)    # Get biological assembly data
mol.centre_molecule(method='centroid')     # Center on origin ('centroid' or 'mass')
mol.create_object(name='NewObject')        # Create Blender 3D object
mol.get_view()                             # Get bounding box for camera framing
mol.set_frame(frame: int)                  # Update for specific animation frame
```

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `mol.object` | `bpy.types.Object` | The Blender mesh object |
| `mol.frames` | `bpy.types.Collection` | Collection of trajectory frames |
| `mol.array` | `AtomArray` or `AtomArrayStack` | Biotite atom array |
| `mol.select` | `MoleculeSelector` | Selector bound to this molecule |
| `mol.styles` | Style list | Access/modify applied styles |

### Usage Patterns

```python
# Method chaining
mol = (
    mn.Molecule.fetch("8H1B")
    .add_style("cartoon", material=mn.material.AmbientOcclusion())
    .add_style("surface", selection="is_peptide", color=(0.6, 0.6, 0.8, 1.0))
)

# Access styles after creation
mol.styles[0].quality = 5
mol.styles[1].remove()

# Iterate styles
for s in mol.styles:
    print(s)
```

---

## Trajectory

MD trajectory class. Backend: **MDAnalysis** (`Universe`).

### Constructor

```python
mn.Trajectory(
    universe: mda.Universe,           # MDAnalysis Universe object
    name: str = 'NewUniverseObject',  # Blender object name
    world_scale: float = 0.01,        # 1 Angstrom = 0.01 Blender units
    create_object: bool = True,       # Auto-create Blender object
) -> Trajectory
```

### Instance Methods

```python
traj.add_style(
    style = 'spheres',            # Style class instance or shorthand string
    color = 'common',             # Color scheme or named attribute
    selection = None,             # MDAnalysis selection string, AtomGroup, or None
    material = None,              # Material class instance or string
    name: str | None = None,
) -> Trajectory                   # Returns self for method chaining
```

```python
traj.create_object(name='NewUniverseObject')  # Returns bpy.types.Object
traj.get_view(selection=None, frame=None)      # Bounding box; selection is MDA string
traj.reset_playback()                          # Reset playback settings
traj.set_frame(frame: int)                     # Update trajectory state
traj.store_named_attribute(data, name: str)    # Store custom array as Named Attribute
```

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `traj.universe` | `mda.Universe` | MDAnalysis Universe |
| `traj.frame_manager` | `FrameManager` | Frame playback controller |
| `traj.selections` | `SelectionManager` | Manages named selections |
| `traj.calculations` | | Calculation manager |
| `traj.annotations` | `TrajectoryAnnotationManager` | Annotation system |
| `traj.styles` | Style list | Access/modify applied styles |
| `traj.world_scale` | `float` | Scale factor (default 0.01) |
| `traj.frame` | `int` | Current frame |
| `traj.subframes` | `int` | Interpolation subframes |
| `traj.offset` | `int` | Frame offset |
| `traj.average` | `bool` | Average positions |
| `traj.correct_periodic` | `bool` | Periodic boundary correction |
| `traj.interpolate` | `bool` | Linear interpolation between frames |
| `traj.dssp` | `DSSPManager` | Secondary structure computation |

### Selection Options

Selections can be provided as:
1. **MDAnalysis selection string**: `"resid 1 129"`, `"name CA"`, `"protein and name CA"`, `"prop x > 5"`
2. **AtomGroup**: `u.select_atoms("resname LYS")`
3. **Direct AtomGroup slice**: `u.atoms[u.atoms.names == "CA"]`
4. **String shorthand**: `"is_peptide"`, `"is_backbone"` (stored boolean attributes)

```python
# MDAnalysis selection string
traj.add_style("cartoon", selection="resid 100:150")

# AtomGroup
traj.add_style("spheres", selection=u.select_atoms("resid 1 129"))

# Direct slice
traj.add_style("spheres", selection=u.atoms[u.atoms.names == "CA"])

# Boolean attribute shorthand
traj.add_style("ribbon", selection="is_peptide")
```

### Custom Attributes

```python
import numpy as np

# Store a float array
values = np.random.random(len(traj.universe.atoms))
traj.store_named_attribute(values, "my_values")

# Store color array (Nx4 RGBA)
colors = np.ones((len(traj.universe.atoms), 4))
colors[:, 0] = values  # Red channel from values
traj.store_named_attribute(colors, "custom_color")
traj.add_style("spheres", color="custom_color")
```

---

## Canvas

Scene and render controller. Manages camera, engine, resolution, and output.

### Constructor

```python
mn.Canvas(
    engine = 'EEVEE',                 # 'EEVEE', 'CYCLES', or mn.scene.Cycles(samples=N)
    resolution: tuple = (1280, 720),  # (width, height) in pixels
    transparent: bool = False,        # Transparent background
    template: str = 'Molecular Nodes', # Scene template
)
```

### Instance Methods

```python
cv.snapshot(
    path: str | None = None,       # Output file path (auto-generated if None)
    frame: int | None = None,      # Frame to render (current if None)
    file_format: str = 'PNG',      # Output format
)

cv.animation(
    path: str | None = None,       # Output directory
    frame_start: int | None = None,
    frame_end: int | None = None,
    render_scale: int = 100,       # Render scale percentage
)

cv.clear()                         # Remove all MN entities from scene
cv.frame_object(obj, viewpoint=None)   # Frame an object in camera
cv.frame_view(view, viewpoint=None)    # Frame a bounding box in camera
cv.load(path: str)                     # Load a .blend file
cv.scene_reset(template='Molecular Nodes', engine='EEVEE')
```

### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `cv.scene` | `bpy.types.Scene` | Blender scene |
| `cv.camera` | `Camera` | Camera controller |
| `cv.engine` | str or Engine | Rendering engine |
| `cv.resolution` | `tuple` | (width, height) |
| `cv.transparent` | `bool` | Transparent background |
| `cv.fps` | `int` | Frames per second |
| `cv.frame_start` | `int` | Animation start frame |
| `cv.frame_end` | `int` | Animation end frame |
| `cv.background` | `tuple` | Background color (r, g, b, a) |
| `cv.view_transform` | `str` | Color management view transform |

### Viewpoint Options

The `viewpoint` parameter accepts:
- **String presets**: `"front"`, `"back"`, `"top"`, `"bottom"`, `"left"`, `"right"`
- **Custom rotation**: `(x, y, z)` tuple in radians

```python
cv.frame_object(mol, viewpoint="front")
cv.frame_view(mol.get_view(), viewpoint="top")
cv.frame_view(mol, (90, 0, -45))  # Custom angle
cv.frame_view(mol, (-3.14, 0, 0))  # Flip view
```

### Combining Views

Views from different entities can be combined with `+`:

```python
# Frame both trajectories together
combined = t1.get_view("resid 184") + t2.get_view("resid 141")
cv.frame_view(combined, viewpoint="front")

# Frame trajectory + density
cv.frame_view(traj.get_view() + density.get_view(), viewpoint="left")
```

---

## Camera

Camera controller accessed via `canvas.camera`.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `camera.lens` | `float` | Focal length in mm (default 50) |
| `camera.rotation` | `tuple` | Current rotation (x, y, z) |
| `camera.clip_start` | `float` | Near clipping distance |
| `camera.clip_end` | `float` | Far clipping distance |
| `camera.camera` | `bpy.types.Object` | Camera object |
| `camera.camera_data` | `bpy.types.Camera` | Camera data block |

### Methods

```python
camera.set_viewpoint(viewpoint)  # "front", "back", "top", "bottom", "left", "right" or (x,y,z)
```

### Zoom Control

```python
cv.camera.lens = 150   # Zoom in (telephoto)
cv.camera.lens = 50    # Default
cv.camera.lens = 35    # Zoom out (wide angle)
```

---

## Scene Engines

```python
# EEVEE (real-time, fast)
cv.engine = "eevee"
cv.engine = "EEVEE"
cv.engine = mn.scene.EEVEE()

# Cycles (path-traced, high quality)
cv.engine = "CYCLES"
cv.engine = mn.scene.Cycles(samples=32)
cv.engine = mn.scene.Cycles(samples=128)   # Higher quality

# Pass as constructor argument
canvas = mn.Canvas(mn.scene.Cycles(samples=32), resolution=(720, 480))
```

**Engine choice affects style rendering:**
- `StyleSpheres(geometry="Point")` — Cycles only (point cloud)
- `StyleSpheres(geometry="Instance")` — Works in both engines
- `StyleSpheres(geometry="Mesh")` — Works in both engines (highest quality, slowest)

---

## Cross-References to blender-api

| Task on MN objects | See blender-api reference |
|-------------------|--------------------------|
| Custom shader materials for MN objects | `blender-api/references/materials-and-nodes.md` — assign via `mol.object.data.materials.append(mat)` |
| Geometry Nodes concepts (creating/linking node trees) | `blender-api/references/geometry-nodes.md` |
| Modifiers on MN objects | `blender-api/references/modifiers-and-constraints.md` |
| Animation keyframes on MN objects | `blender-api/references/handlers-and-timers.md` for frame handlers |
| Stale references after undo/redo | `blender-api/references/gotchas-and-pitfalls.md` — re-fetch `mol.object` after undo |
| Render operators (headless render) | `blender-api/references/operators-reference.md` — `render.render(write_still=True)` |
| Math/transforms/BVHTree | `blender-api/references/math-and-spatial.md` |
| Headless mode pitfalls | `blender-api/references/gotchas-and-pitfalls.md` — "Headless / Background Mode" section |

---

## Session Management

`MNSession` manages all MN entities in a Blender session.

```python
session = mn.session.MNSession()

# Add entities
session.add_trajectory(universe, style='vdw', name='MyTraj')

# Retrieve
traj = session.get_trajectory("MyTraj")
obj = session.get_object(uuid)

# Clean up
session.remove_trajectory(traj)
session.remove(uuid)
session.clear()         # Remove all MN entities
session.prune()         # Remove invalid/deleted entities
```

**Session persistence**: A `.MNSession` file is saved alongside the `.blend` file to preserve MDAnalysis Universe objects between saves. Both files must remain together for trajectory playback to work after reopening.
