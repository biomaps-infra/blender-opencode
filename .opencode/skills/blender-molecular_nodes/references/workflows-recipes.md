# Workflows & Recipes

Six essential end-to-end examples covering the most common MolecularNodes tasks. Each is self-contained and runnable.

## Table of Contents
1. [Fetch Protein and Render](#1-fetch-protein-and-render)
2. [Multiple Styles with Selections](#2-multiple-styles-with-selections)
3. [MD Trajectory with Annotations](#3-md-trajectory-with-annotations)
4. [RMSF Analysis Coloring](#4-rmsf-analysis-coloring)
5. [CryoEM Density with Atomic Coloring](#5-cryoem-density-with-atomic-coloring)
6. [Solvent Density Analysis](#6-solvent-density-analysis)

---

## 1. Fetch Protein and Render

Basic workflow: download a PDB structure, apply cartoon style, render. Also shows AlphaFold variant.

```python
import molecularnodes as mn

# --- RCSB PDB ---
canvas = mn.Canvas(mn.scene.Cycles(samples=32), resolution=(720, 480))
mol = mn.Molecule.fetch("4ozs")
mol.add_style(mn.StyleCartoon())
canvas.frame_object(mol)
canvas.snapshot()  # Saves to auto-generated path

# --- AlphaFold (UniProt accession, NOT PDB code) ---
canvas.clear()
canvas.engine = "eevee"
canvas.resolution = (800, 800)
canvas.transparent = True
mol = mn.Molecule.fetch("Q8W3K0", database="alphafold")
mol.add_style(mn.StyleCartoon(), color="pLDDT", material=mn.material.AmbientOcclusion())
canvas.frame_view(mol)
canvas.snapshot()

# --- Local file ---
canvas.clear()
mol = mn.Molecule.load("/path/to/structure.pdb")
mol.add_style(mn.StyleRibbon())
canvas.frame_object(mol)
canvas.snapshot()
```

**Key points:**
- `database="alphafold"` needs UniProt accession codes, not PDB codes
- `color="pLDDT"` maps AlphaFold confidence (stored in `b_factor`) to blue/cyan/yellow/orange
- `canvas.clear()` removes previous entities before loading new ones

---

## 2. Multiple Styles with Selections

Combine cartoon, surface, and ball-and-stick on different parts. Demonstrates MoleculeSelector, material choices, and style modification after creation.

```python
import molecularnodes as mn

cv = mn.Canvas(mn.scene.Cycles(samples=32), resolution=(860, 540))

# Method chaining: cartoon + transparent surface
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
cv.frame_object(mol)
cv.snapshot()

# Add ball-and-stick for non-protein (ligands, ions)
# bond_find=True is critical — ligands often lack bond data in PDB files
mol.add_style("ball_and_stick", selection=mn.MoleculeSelector().not_peptide())
mol.styles[-1].bond_find = True
cv.snapshot()

# Modify style properties after creation
mol.styles[0].quality = 5
mol.styles[1].material = mn.material.FlatOutline()
cv.snapshot()

# Remove a style
mol.styles[-1].remove()
```

**Key points:**
- `.add_style()` returns `self` for chaining
- `MoleculeSelector` for `Molecule` entities (NOT MDAnalysis strings)
- Set `bond_find=True` for ligands/small molecules without bond data
- Access `mol.styles[N]` to modify or remove styles after creation

---

## 3. MD Trajectory with Annotations

Load a trajectory, add multiple styles, annotate with measurements, and render an animation.

```python
import molecularnodes as mn
import MDAnalysis as mda
from MDAnalysis.tests.datafiles import PSF, DCD

canvas = mn.Canvas()
u = mda.Universe(PSF, DCD)
t = mn.Trajectory(u).add_style("cartoon")

# Highlight residues — note: MDAnalysis selection syntax, NOT MoleculeSelector
t.add_style('spheres', selection="resid 1 129")
t.styles[1].geometry = "mesh"  # Use mesh for EEVEE compatibility

# Annotations: universe info overlay
t.annotations.add_universe_info()

# Annotations: distance between two COMs
t.annotations.add_com_distance(
    selection1="resid 1",
    selection2="resid 129",
    text1="r1", text2="r129"
)

# Annotations: atom labels on alpha carbons
a1 = t.annotations.add_atom_info(
    selection="resid 73:78 and name CA",
    show_resid=True, show_segid=True,
)
a1.text_size = 12

# Render single frame and animation
canvas.frame_object(t)
canvas.snapshot(frame=75)
canvas.animation(frame_start=10, frame_end=50, render_scale=50)

# Annotation management
a1.visible = False              # Hide one
t.annotations.visible = False   # Hide all
t.annotations.clear()           # Remove all
```

**Key points:**
- Trajectory selections use MDAnalysis strings: `"resid 1 129"`, `"name CA"`, `"protein"`
- `geometry="mesh"` on spheres for EEVEE compatibility
- Annotations auto-update each frame (COM distance changes with trajectory)
- `render_scale=50` renders at 50% resolution for preview

### Subframe Interpolation

```python
t.subframes = 4               # 4 subframes per trajectory frame
t.interpolate = True           # Linear interpolation
t.correct_periodic = True      # Fix periodic boundary jumps
```

---

## 4. RMSF Analysis Coloring

Full pipeline: MDAnalysis RMSF analysis, matplotlib colormap, store as named attribute, render.

```python
import molecularnodes as mn
import MDAnalysis as mda
import numpy as np
import matplotlib.cm as cm
from MDAnalysis.analysis import rms, align
from MDAnalysisData import datasets

canvas = mn.Canvas(mn.scene.Cycles(samples=16), (800, 800), transparent=True)

# Load and align trajectory
adk = datasets.fetch_adk_equilibrium()
u = mda.Universe(adk.topology, adk.trajectory)
average = align.AverageStructure(u, u, select="protein and name CA", ref_frame=0).run()
ref = average.results.universe
align.AlignTraj(u, ref, select="protein and name CA", in_memory=True).run()

# Compute RMSF per alpha carbon, spread to all atoms via tempfactors
c_alphas = u.select_atoms("protein and name CA")
R = rms.RMSF(c_alphas).run()
u.add_TopologyAttr("tempfactors")
for residue, r_value in zip(u.select_atoms("protein").residues, R.results.rmsf):
    residue.atoms.tempfactors = r_value

# Map to RGBA colors via matplotlib colormap
col_array = u.atoms.tempfactors.copy()
col_array /= col_array.max()
col_array = cm.get_cmap('inferno')(col_array)  # Nx4 RGBA

# Create trajectory, store colors, render
traj = mn.Trajectory(u)
traj.store_named_attribute(col_array, "custom_color")
traj.add_style(mn.StyleRibbon(quality=6, backbone_radius=1.5), color="custom_color")
canvas.frame_view(traj)
canvas.snapshot()
```

**Key points:**
- `store_named_attribute()` stores any numpy array as a Geometry Nodes named attribute
- `color="custom_color"` references the named attribute by string name
- Matplotlib colormaps return Nx4 RGBA arrays, exactly what MN needs
- RMSF is per-CA; spreading via `tempfactors` maps it to all atoms in each residue

---

## 5. CryoEM Density with Atomic Coloring

Import density map, adjust isosurface, load fitted structure, combine views.

```python
import molecularnodes as mn

canvas = mn.Canvas()

# Load density
d = mn.entities.density.io.load(
    file_path="emd_27874.map.gz",
    style="density_iso_surface",
    overwrite=True,
)

# Configure isosurface
ds = d.styles[0]
ds.iso_value = 1.0
ds.show_contours = True
ds.contour_thickness = 0.1
ds.contour_color = (1.0, 1.0, 1.0, 0.5)
ds.positive_color = (0.7, 1.0, 0.7, 1.0)

# Slice to see interior
ds.slice_left = 35

# Add density annotations
d.annotations.add_grid_axes()
d.annotations.add_density_info()

# Load corresponding atomic structure
mol = mn.Molecule.fetch("8E3Z")
mol.add_style(mn.StyleRibbon())

# Frame both together and render
canvas.frame_view(mol.get_view() + d.get_view(), viewpoint="front")
canvas.snapshot()
```

**GUI coloring workflow** (to color density surface by atom colors):
1. Duplicate the structure object (Shift+D) and its node tree
2. Remove the style node from the duplicate (exposes raw atoms)
3. On the density object, add `Sample Nearest Atoms` node (MolecularNodes > Density)
4. Connect the atom object as input — colors transfer to the density surface

**Key points:**
- Density files are converted to `.vdb` internally — do not move/delete these files
- `mol.get_view() + d.get_view()` combines bounding boxes for framing
- Views from different entities can be added with `+`

---

## 6. Solvent Density Analysis

Full MDAnalysis solvent density pipeline: trajectory alignment, density computation, export, MN visualization.

```python
import MDAnalysis as mda
import molecularnodes as mn
import numpy as np
from MDAnalysis import transformations as trans
from MDAnalysis.analysis import density
from MDAnalysis.tests.datafiles import TPR, XTC

canvas = mn.Canvas()

# Set up universe with alignment transformations
u = mda.Universe(TPR, XTC)
protein = u.select_atoms("protein")
water = u.select_atoms("not protein")

workflow = [
    trans.unwrap(u.atoms),
    trans.center_in_box(protein, center="geometry"),
    trans.wrap(water, compound="residues"),
    trans.fit_rot_trans(protein, protein, weights="mass"),
]
u.trajectory.add_transformations(*workflow)

# Compute and export solvent density
ow = u.select_atoms("name OW")
dens = density.DensityAnalysis(ow, delta=4.0, padding=2)
dens.run()
dens.results.density.convert_density("TIP4P")
dens.results.density.export("water.dx")

# Visualize protein
t = mn.Trajectory(u).add_style(mn.StyleRibbon(quality=5, backbone_radius=2))

# Load and style computed density
d = mn.entities.density.io.load(file_path="water.dx", style="density_iso_surface", overwrite=True)
ds = d.styles[0]
ds.positive_color = (0, 0, 1, 0.5)
ds.iso_value = 0.5
ds.show_contours = True
ds.contour_thickness = 0.25

# Render
canvas.frame_view(t.get_view() + d.get_view(), viewpoint="front")
canvas.snapshot()
```

**Key points:**
- MDAnalysis transformations must be applied before density analysis
- `density.export("water.dx")` writes OpenDX format, directly loadable by MN
- Solvent density + protein trajectory render together naturally
