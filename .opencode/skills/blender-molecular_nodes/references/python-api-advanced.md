# Python API — Advanced Features

## Table of Contents
1. [Annotations System](#annotations-system)
2. [Built-in Annotation Types](#built-in-annotation-types)
3. [Custom Annotations](#custom-annotations)
4. [Density Loading & Visualization](#density-loading--visualization)
5. [Streaming Trajectories](#streaming-trajectories)
6. [Ensemble Entity](#ensemble-entity)
7. [OXDNA Entity](#oxdna-entity)
8. [Drawing Utilities (Custom Annotations)](#drawing-utilities)

---

## Annotations System

> **[GUI-ONLY]** All annotations are GPU viewport overlays. They require an active 3D viewport and do NOT work in headless/background mode (`blender --background` or standalone `molecularnodes[bpy]`). Exception: `add_com_distance(line_mode="mesh")` creates renderable mesh geometry.

Annotations add measurements, labels, and informational overlays to trajectories and density objects. Managed via the `.annotations` attribute.

### Discovering Available Types

```python
# List all add_* methods
[a for a in t.annotations.__dir__() if a.startswith("add_")]

# Get method signature
t.annotations.add_atom_info.func.__signature__
```

### Accessing Annotations

```python
# By name
a = t.annotations["r1 atom info"]
a = t.annotations.get("r1 atom info")

# By index
a = t.annotations[0]
a = t.annotations[-1]

# Count
len(t.annotations)

# Iteration
for a in t.annotations:
    print(a.name)
```

### Controlling Visibility

```python
# All at once
t.annotations.visible = False    # Hide all
t.annotations.visible = True     # Show all

# Individual
a1.visible = False               # Hide one
a1.visible = True                # Show one
```

### Removing Annotations

```python
t.annotations.remove("r1 atom info")  # By name
t.annotations.remove(a4)               # By instance
t.annotations.clear()                   # Remove all
```

### Listing Properties

```python
# Discover all configurable properties
[(p, getattr(a1, p)) for p in a1.__dir__() if not p.startswith("_")]
```

---

## Built-in Annotation Types

> **[GUI-ONLY]** All methods below are GPU viewport overlays unless noted otherwise.

### Trajectory Annotations

#### add_atom_info [GUI-ONLY]

Atom labels at specified positions.

```python
a = t.annotations.add_atom_info(
    selection="resid 73:78 and name CA",  # MDAnalysis selection string
    show_resid: bool = True,
    show_segid: bool = True,
    name: str = "atom info",
)
a.text_size = 12
```

#### add_com [GUI-ONLY]

Center of mass marker.

```python
a = t.annotations.add_com(
    selection="protein",           # MDAnalysis selection
    text="Protein|COM",
    name="Protein COM",
)
```

#### add_com_distance [GUI-ONLY, except `line_mode="mesh"`]

Distance line between two centers of mass. When `line_mode="mesh"` or `"mesh_and_overlay"`, the mesh component creates renderable geometry that works headless.

```python
a = t.annotations.add_com_distance(
    selection1="resid 1",                    # String or AtomGroup
    selection2=u.select_atoms("resid 129"),  # String or AtomGroup
    text1="resid 1|COM",
    text2="resid 129|COM",
    name="r1-129 distance",
)
a.line_mode = "mesh_and_overlay"    # "overlay", "mesh", "mesh_and_overlay"
a.mesh_color = (0, 1, 0, 1)        # RGBA
```

#### add_canonical_dihedrals [GUI-ONLY]

Phi/Psi/Omega dihedral angles for a residue.

```python
a = t.annotations.add_canonical_dihedrals(resid=200)
```

#### add_universe_info [GUI-ONLY]

Frame number, simulation time, topology info overlay.

```python
a = t.annotations.add_universe_info()
```

#### add_simulation_box [GUI-ONLY]

Visualize the simulation periodic boundary box.

```python
a = t.annotations.add_simulation_box()
```

#### add_label_2d [GUI-ONLY]

2D text label at a screen position.

```python
a = t.annotations.add_label_2d(
    text="Any|2D Label",
    location=(0.1, 0.8),    # (x, y) normalized screen coords (0-1)
)
```

#### add_label_3d [GUI-ONLY]

3D text label at world coordinates.

```python
r1 = t.universe.select_atoms("resid 1 and name CA")
a = t.annotations.add_label_3d(
    text=f"CA|resid 1|{r1.atoms[0].segid}",
    location=r1.atoms[0].position,     # 3D world position
)
a.line_pointer_length = 2    # Leader line length
a.line_width = 2
```

### Density Annotations [GUI-ONLY]

```python
# Grid axes visualization
dg = d.annotations.add_grid_axes()       # [GUI-ONLY]
dg = d.annotations.add_grid_axes_3d()    # [GUI-ONLY] 3D version

# Density metadata info
di = d.annotations.add_density_info()    # [GUI-ONLY]
di.show_origin = False
di.show_delta = False
di.show_shape = False
```

---

## Custom Annotations [GUI-ONLY]

> **[GUI-ONLY]** Custom annotations use GPU drawing via `draw()` — they only work in interactive Blender with an active viewport.

Define custom annotation classes that auto-register with the Trajectory entity.

### Basic Custom Annotation

```python
from MDAnalysis.core.groups import AtomGroup

class CustomAnnotation(mn.entities.trajectory.TrajectoryAnnotation):
    annotation_type = "custom_annotation"   # Unique type identifier

    # Required parameter (no default)
    selection: str

    # Optional parameters (with defaults)
    bool_param: bool = False

    def defaults(self) -> None:
        """Set default annotation properties."""
        params = self.interface
        params.text_size = 20

    def validate(self, input_name: str = None) -> bool:
        """Validate inputs. Return True on success, raise on failure."""
        params = self.interface
        universe = self.trajectory.universe

        if isinstance(params.selection, str):
            self.atom_group = universe.select_atoms(params.selection)
        elif isinstance(params.selection, AtomGroup):
            self.atom_group = params.selection
        else:
            raise ValueError(f"Need str or AtomGroup. Got {type(params.selection)}")
        return True

    def draw(self) -> None:
        """Render the annotation. Called every frame."""
        for atom in self.atom_group:
            self.draw_text_3d(atom.position, atom.name)
```

### Using Custom Annotations

```python
# Auto-registered as add_custom_annotation
t.add_style(selection="resid 75", style="ball_and_stick")
ca = t.annotations.add_custom_annotation(selection="resid 75")

# Works with all standard annotation controls
ca.visible = False
ca.text_size = 24
t.annotations.remove(ca)
```

### Unregistering

```python
manager = mn.entities.trajectory.TrajectoryAnnotationManager
manager.unregister_type("custom_annotation")
```

### Parameter Overrides in Drawing

Override annotation-level properties per draw call:

```python
def draw(self) -> None:
    self.draw_circle_3d(
        center, radius, normal_vector,
        overrides={"line_color": (1.0, 0.5, 0.0, 1)}
    )
    self.draw_circle_3d(
        center, radius * 2, normal_vector,
        overrides={"line_color": self.interface.line_color_input}
    )
```

Custom color input parameters:

```python
class MyAnnotation(mn.entities.trajectory.TrajectoryAnnotation):
    annotation_type = "my_annotation"
    selection: str
    line_color_input: tuple[float, float, float, float] = (1, 1, 1, 1)
    # ...
```

---

## Density Loading & Visualization

### Loading Density Files

```python
import molecularnodes as mn
from pathlib import Path

d = mn.entities.density.io.load(
    file_path="density.map.gz",          # .map, .map.gz, .dx, .dx.gz
    style="density_iso_surface",         # or "density_wire"
    overwrite: bool = True,              # Overwrite existing .vdb
)
```

### Density Style Properties

```python
ds = d.styles[0]

# Isosurface threshold
ds.iso_value = 1.0              # Adjust density cutoff

# Contour lines
ds.show_contours = True
ds.contour_thickness = 0.1
ds.contour_color = (1.0, 1.0, 1.0, 0.5)
ds.only_contours = True         # Show only contours, no surface

# Slicing (percentage from each side)
ds.slice_left = 35
ds.slice_right = 0
ds.slice_front = 0
ds.slice_back = 0
ds.slice_top = 0
ds.slice_bottom = 0

# Colors (for electrostatic maps with positive/negative values)
ds.positive_color = (0.7, 1.0, 0.7, 1.0)   # Green
ds.negative_color = (0.7, 0.0, 1.0, 1.0)   # Purple

# Material
ds.material = "MN Flat Outline"
ds.material = mn.material.AmbientOcclusion()
```

### Density Annotations

```python
# Grid axes
dg = d.annotations.add_grid_axes()       # 2D axes overlay
dg = d.annotations.add_grid_axes_3d()    # 3D axes in scene

# Metadata
di = d.annotations.add_density_info()
di.show_origin = False
di.show_delta = False
di.show_shape = False

# Toggle visibility
dg.visible = False
di.visible = False
```

### Density + Atomic Structure

```python
# Load density and structure — they auto-align if from the same experiment
d = mn.entities.density.io.load(file_path="emd_27874.map.gz", style="density_iso_surface", overwrite=True)
mol = mn.Molecule.fetch("8E3Z").add_style(mn.StyleRibbon())

# Frame both together
canvas.frame_view(mol.get_view() + d.get_view(), viewpoint="front")
```

---

## Streaming Trajectories

Connect to a live running MD simulation via IMD protocol.

```python
import MDAnalysis as mda
import molecularnodes as mn

# Connect to running GROMACS simulation
# Instead of a file path, use imd:// URL
u = mda.Universe("topology.tpr", "imd://localhost:8889")

traj = mn.Trajectory(u)
traj.add_style("cartoon")

# Each Blender frame change fetches latest simulation frame
# No caching — cannot scrub backward without advancing simulation
```

**Requirements:**
- MDAnalysis 2.10+ with IMDClient
- Simulation must support IMD protocol (e.g., GROMACS with `-imd` flag)

**Limitations:**
- Experimental feature
- No frame caching currently
- Scrubbing backward still advances the simulation
- If simulation supports GO/PAUSE, pausing Blender pauses simulation

---

## Ensemble Entity

For multi-model/ensemble structures and starfile data.

```python
# Reference: mn.entities.Ensemble
ensemble = mn.entities.Ensemble(...)
```

Used internally for:
- Biological assemblies (rotation/translation matrices)
- Starfile mapback visualizations
- Multi-model NMR structures

---

## OXDNA Entity

Coarse-grained DNA/RNA simulation data via oxDNA format.

```python
# Reference: mn.entities.OXDNA
oxdna = mn.entities.OXDNA(universe)
```

Loaded through MDAnalysis as a Universe, then wrapped in the OXDNA entity class for specialized visualization.

---

## Drawing Utilities [GUI-ONLY]

> **[GUI-ONLY]** All drawing utilities require an active GPU context (interactive viewport). None of these work in headless/background mode.

Available within the `draw()` method of custom `TrajectoryAnnotation` subclasses:

### Text

```python
self.draw_text_2d(position_2d, text)      # 2D screen-space text
self.draw_text_3d(position_3d, text)      # 3D world-space text
```

### Lines

```python
self.draw_line_2d(p1, p2)                 # 2D line
self.draw_line_3d(p1, p2)                 # 3D line
```

### Shapes

```python
self.draw_circle_2d(center, radius)
self.draw_circle_3d(center, radius, normal_vector)
self.draw_sphere(position, radius)
self.draw_cone(start, end)
self.draw_cylinder(start, end)
self.draw_n_sided_cylinder(...)
self.draw_n_sided_pyramid(...)
```

### Measurement

```python
self.distance(v1, v2)                     # Euclidean distance
```

### Simulation Box

```python
self.draw_triclinic_cell(...)
self.draw_wigner_seitz_cell(...)
```

### Mesh/Image

```python
self.draw_bmesh(bmesh)                    # Custom BMesh geometry
self.draw_bpy_image(image, position_2d)   # Blender image at screen position
self.bpy_image_to_pil_image(bpy_image)    # Convert to PIL
self.pil_image_to_bpy_image(pil_image)    # Convert from PIL
```
