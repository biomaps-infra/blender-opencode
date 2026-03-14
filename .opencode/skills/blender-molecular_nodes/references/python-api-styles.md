# Python API — Styles, Materials & Selectors

## Table of Contents
1. [Style Classes](#style-classes)
2. [Style Shorthand Strings](#style-shorthand-strings)
3. [Style Management](#style-management)
4. [Material Classes](#material-classes)
5. [Color Options](#color-options)
6. [MoleculeSelector](#moleculeselector)

---

## Style Classes

All style classes share:
- `update_style_node(node_style)` — Updates the Blender GeometryNodeGroup inputs
- `material` attribute — Get/set material
- `remove()` — Remove this style from the entity

### StyleSpheres

Space-filling Van der Waals spheres.

```python
mn.StyleSpheres(
    geometry: str = 'Point',     # 'Point' (Cycles only), 'Instance', or 'Mesh'
    radius: float = 0.8,         # Sphere radius multiplier
    subdivisions: int = 2,       # Icosphere subdivisions (Instance/Mesh only)
    shade_smooth: bool = True,
)
```

**`geometry` options:**
- `"Point"` — Point cloud, Cycles only, fastest
- `"Instance"` — Instanced icospheres, both engines, good performance
- `"Mesh"` — Realized mesh, both engines, highest quality, slowest

### StyleCartoon

Traditional protein cartoon (helices, sheets, loops). The most-used style.

```python
mn.StyleCartoon(
    quality: int = 2,
    peptide_dssp: bool = False,       # Compute secondary structure (DSSP)
    peptide_cylinders: bool = False,  # Cylinders for helices
    peptide_arrows: bool = True,      # Arrows for beta sheets
    peptide_rounded: bool = False,    # Rounded ends
    peptide_thickness: float = 0.6,
    peptide_width: float = 2.2,
    peptide_loop_radius: float = 0.3,
    peptide_smoothing: float = 0.5,
    backbone_shape: str = 'Cylinder', # Backbone tube shape
    nucleic_width: float = 3.0,
    nucleic_thickness: float = 1.0,
    nucleic_radius: float = 2.0,
    base_shape: str = 'Rectangle',    # 'Rectangle' or other shape
    base_realize: bool = False,
    color_blur: bool = True,          # Smooth color transitions
    shade_smooth: bool = True,
)
```

### StyleRibbon

Simplified tube through alpha carbons.

```python
mn.StyleRibbon(
    quality: int = 3,
    backbone_smoothing: float = 0.5,
    backbone_threshold: float = 4.5,   # CA distance threshold for chain splitting
    backbone_radius: float = 1.6,
    nucleic_backbone_shape: str = 'Cylinder',
    nucleic_backbone_radius: float = 1.6,
    backbone_width: float = 3.0,
    backbone_thickness: float = 1.0,
    base_scale: tuple = (2.5, 0.5, 7.0),
    base_resolution: int = 4,
    base_realize: bool = False,
    uv_map: bool = False,
    u_component: str = 'Factor',
    color_blur: bool = False,
    shade_smooth: bool = True,
)
```

### StyleSurface

Solvent-accessible surface approximation.

```python
mn.StyleSurface(
    quality: int = 3,
    scale_radius: float = 1.5,        # VDW radius multiplier
    probe_size: float = 1.0,          # Probe sphere radius (Angstroms)
    relaxation_steps: int = 10,
    separate_by: str = 'chain_id',    # Separate surface by attribute
    group_id: int = 0,
    color_source: str = 'Alpha Carbon',
    color_blur: int = 2,
    shade_smooth: bool = True,
)
```

### StyleBallAndStick

Atoms as spheres with bond cylinders.

```python
mn.StyleBallAndStick(
    quality: int = 2,
    sphere_geometry: str = 'Instance',  # 'Instance' or 'Mesh'
    sphere_radius: float = 0.3,
    bond_split: bool = False,           # Split bonds at midpoint for two-tone color
    bond_radius: float = 0.3,
    bond_find: bool = False,            # Auto-find bonds by distance
    bond_find_scale: float = 1.0,       # Distance scale for bond finding
    color_blur: bool = False,
    shade_smooth: bool = True,
)
```

**Important**: Set `bond_find = True` when viewing small molecules or ligands that may not have bonds defined in the PDB file.

### StyleSticks

Clean stick representation with half-sphere termination at each end.

```python
mn.StyleSticks(
    quality: int = 3,
    radius: float = 0.2,
    color_blur: bool = False,
    shade_smooth: bool = True,
)
```

---

## Style Shorthand Strings

Instead of creating style class instances, you can pass shorthand strings to `add_style()`:

| String | Equivalent Class |
|--------|-----------------|
| `"cartoon"` | `StyleCartoon()` |
| `"ribbon"` | `StyleRibbon()` |
| `"spheres"` | `StyleSpheres()` |
| `"vdw"` | `StyleSpheres()` |
| `"surface"` | `StyleSurface()` |
| `"ball_and_stick"` | `StyleBallAndStick()` |
| `"sticks"` | `StyleSticks()` |

```python
# These are equivalent:
mol.add_style("cartoon")
mol.add_style(mn.StyleCartoon())
```

---

## Style Management

### Accessing Styles

```python
# By index
style = mol.styles[0]       # First style
style = mol.styles[-1]      # Last style

# Iteration
for s in mol.styles:
    print(s)

# Count
len(mol.styles)
```

### Modifying Style Properties

```python
# Access style properties directly
style = mol.styles[0]
style.quality = 5
style.backbone_radius = 1.5
style.shade_smooth = True

# Change material
style.material = mn.material.AmbientOcclusion()
style.material.ambient_occlusion_distance = 0.1
```

### Removing Styles

```python
# Remove specific style
mol.styles[-1].remove()

# Clear all styles
mol.styles.clear()
# Then add new ones:
mol.add_style("cartoon")
```

### Creating and Configuring Before Adding

```python
# Create style instance
s = mn.StyleSticks()
s.radius = 0.1

# Add the pre-configured style
traj.add_style(style=s, selection="resid 40:50")
```

---

## Material Classes

### Available Materials

| Class | Description |
|-------|-------------|
| `mn.material.Default()` | Standard material |
| `mn.material.AmbientOcclusion()` | AO-based shading, scientific look |
| `mn.material.FlatOutline()` | Flat shading with outlines |
| `mn.material.Squishy()` | Soft, subsurface-scattering look |
| `mn.material.TransparentOutline()` | Transparent with outlines |

### Material Properties (AmbientOcclusion example)

```python
mat = mn.material.AmbientOcclusion()

# Available properties:
mat.ambient_occlusion_color
mat.ambient_occlusion_distance   # e.g., 0.1
mat.ambient_occlusion_normal
mat.emission_color
mat.emission_strength
mat.material                      # bpy.types.Material
mat.math_value
mat.mix_a
mat.mix_b
mat.mix_factor
mat.tree                          # Node tree
```

### Setting Materials

```python
# At add_style time
mol.add_style("cartoon", material=mn.material.AmbientOcclusion())

# After creation
mol.styles[0].material = mn.material.FlatOutline()

# By string name
mol.add_style("surface", material="MN Transparent Outline")

# Modify material properties
mol.styles[0].material.ambient_occlusion_distance = 0.1
mol.styles[0].material.math_value = 0.1
```

### Listing Material Properties

```python
# Discover properties programmatically
[x for x in dir(mn.material.AmbientOcclusion()) if not x.startswith("_")]
```

---

## Color Options

Colors can be specified in several ways:

### Color Scheme Strings

| String | Description |
|--------|-------------|
| `"common"` | Default: element-based (H=white, C=gray, N=blue, O=red, S=yellow, P=orange) |
| `"pLDDT"` | AlphaFold confidence: blue (>90), cyan (70-90), yellow (50-70), orange (<50) |
| `"element"` | Full periodic table coloring |

### Color Tuples

```python
# RGBA tuple (0.0 to 1.0)
mol.add_style("surface", color=(0.6, 0.6, 0.8, 1.0))   # Light blue, opaque
mol.add_style("cartoon", color=(0.2, 1.0, 0.3, 0.5))    # Green, 50% transparent
mol.add_style("spheres", color=(0, 0, 0, 1))             # Black
```

### Named Attribute String

Reference a custom attribute stored on the mesh:

```python
# Store custom RGBA color data
traj.store_named_attribute(color_array, "custom_color")
traj.add_style("spheres", color="custom_color")
```

### Selection-Based Coloring

Use `"is_peptide"`, `"is_backbone"` etc. as selection, each part gets separate color treatment via the node graph.

---

## MoleculeSelector

Builder pattern for creating atom selections on `Molecule` entities.

### Constructor

```python
mn.MoleculeSelector(mol=None)
```

### Selection Methods (all return `self` for chaining)

#### Identity-Based

```python
selector.atom_name(atom_name)      # By atom name
selector.chain_id(chain_id)        # By chain ID
selector.element(element)          # By element symbol
selector.res_id(num)               # By residue number
selector.res_name(res_name)        # By residue name
```

#### Type-Based

```python
selector.is_amino_acid()
selector.is_backbone()
selector.is_canonical_amino_acid()
selector.is_canonical_nucleotide()
selector.is_carbohydrate()
selector.is_hetero()
selector.is_ligand()
selector.is_monoatomic_ion()
selector.is_nucleotide()
selector.is_peptide_backbone()
selector.is_peptide()              # Shorthand via string "is_peptide"
selector.is_phosphate_backbone()
selector.is_polymer()
selector.is_solvent()
selector.linear_bond_continuity()
```

#### Negation Methods

Every `is_*` and identity method has a `not_*` counterpart:

```python
selector.not_peptide()
selector.not_solvent()
selector.not_hetero()
selector.not_amino_acids()
selector.not_atom_names()
selector.not_canonical_amino_acids()
selector.not_canonical_nucleotides()
selector.not_carbohydrates()
selector.not_chain_id()
selector.not_element()
selector.not_monoatomic_ions()
selector.not_nucleotides()
selector.not_peptide_backbone()
selector.not_phosphate_backbone()
selector.not_polymer()
selector.not_res_id()
selector.not_res_name()
selector.not_solvent()
```

### Evaluation

```python
# Get boolean mask
mask = selector.evaluate_on_array(array)   # Returns numpy boolean array

# Store as named attribute on the Molecule's mesh
selector.store_selection("my_selection")

# Reset pending selections
selector.reset()
```

### Usage with add_style

```python
# Direct instantiation
mol.add_style("surface", selection=mn.MoleculeSelector().is_peptide())

# Also accessible from molecule
mol.add_style("surface", selection=mol.select.is_peptide())

# Chaining for complex selections
sel = mn.MoleculeSelector().is_peptide().chain_id("A")
mol.add_style("cartoon", selection=sel)

# String shorthand (convenience, limited to single boolean attributes)
mol.add_style("cartoon", selection="is_peptide")
mol.add_style("ribbon", selection="is_nucleic")
```

### Trajectory Selections

Trajectories use **MDAnalysis selection strings** instead of `MoleculeSelector`:

```python
# MDAnalysis selection syntax
traj.add_style("cartoon", selection="resid 100:150")
traj.add_style("spheres", selection="name CA")
traj.add_style("surface", selection="protein and not resname ALA")

# AtomGroup objects
traj.add_style("spheres", selection=u.select_atoms("resid 1 129"))

# Direct slice
traj.add_style("spheres", selection=u.atoms[u.atoms.names == "CA"])
```
