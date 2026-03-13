# Gotchas & Failure Modes

Common mistakes, silent failures, and debugging guidance for MolecularNodes. **Read this before generating MN code.**

## Table of Contents
1. [Rendering Failures](#rendering-failures)
2. [Style & Visual Issues](#style--visual-issues)
3. [Data & Import Issues](#data--import-issues)
4. [Selection Confusion](#selection-confusion)
5. [Session & File Persistence](#session--file-persistence)
6. [Version & Dependency Issues](#version--dependency-issues)
7. [Geometry Nodes Pitfalls](#geometry-nodes-pitfalls)
8. [Performance Issues](#performance-issues)

---

## Headless / Background Mode

### Annotations crash or produce nothing in headless mode

**Cause**: All MN annotations (`add_atom_info`, `add_com`, `add_label_2d/3d`, `add_universe_info`, `add_simulation_box`, `add_canonical_dihedrals`, and all custom annotation `draw()` methods) are GPU viewport overlays. They require an active 3D viewport with a GPU context, which does not exist in `blender --background` or standalone `molecularnodes[bpy]`.

**Fix**: Do not use annotations in headless scripts. The core pipeline (Molecule/Trajectory/Canvas/Style/Material) is fully headless-compatible. For headless renders, use `canvas.snapshot()` or `bpy.ops.render.render(write_still=True)`.

**Exception**: `add_com_distance(line_mode="mesh")` creates actual mesh geometry that renders in headless mode.

**Detection**:
```python
import bpy
if bpy.app.background:
    # Skip annotations — they won't work
    pass
else:
    t.annotations.add_atom_info(selection="name CA")
```

### `bpy.ops.render.opengl()` fails headless

**Cause**: `render.opengl()` captures the viewport buffer, which doesn't exist in background mode.

**Fix**: Use `canvas.snapshot()` or `bpy.ops.render.render(write_still=True)` instead. See `blender-api/references/operators-reference.md` for render operator details.

---

## Rendering Failures

### Molecule is invisible in EEVEE

**Cause**: `StyleSpheres(geometry="Point")` uses point clouds, which only render in Cycles.

**Fix**: Switch to `"Instance"` or `"Mesh"`:
```python
# WRONG — invisible in EEVEE
mol.add_style(mn.StyleSpheres())  # Default is geometry="Point"

# CORRECT — works in both engines
mol.add_style(mn.StyleSpheres(geometry="Instance"))
mol.add_style(mn.StyleSpheres(geometry="Mesh"))  # Highest quality, slowest
```

**Also check**: Are you in Rendered View? The molecule may appear as raw points in Solid view. Press Z and select Material Preview or Rendered.

### Molecule renders as a blob of dots

**Cause**: Viewing the raw atomic mesh without a style applied. The default cube may be hiding it.

**Fix**: Delete the default cube (select it, press X). Make sure a Style node is connected in the Geometry Nodes editor. In rendered view, check that the Geometry Nodes modifier is active.

### Rendered image is all black

**Cause**: No lights in scene, or camera is not framing the molecule.

**Fix**:
```python
canvas.frame_object(mol)  # Auto-frames camera
```
For GUI: check that lights exist (the MN startup template includes lights). Use `canvas.frame_view(mol, viewpoint="front")` for explicit framing.

### Cartoon style shows no secondary structure

**Cause**: The `sec_struct` attribute is not set on the mesh. This happens when:
- The file doesn't contain DSSP/secondary structure annotations
- The structure was imported without DSSP computation

**Fix**: In the node graph, set `Peptide DSSP = True` on the Style Cartoon node, or use the `Topology DSSP` node to compute it from geometry. In Python:
```python
mol.add_style(mn.StyleCartoon(peptide_dssp=True))
```

---

## Style & Visual Issues

### Ball-and-stick shows atoms but no bonds

**Cause**: Bond information is missing from the file (common with small molecules, ligands, non-standard residues).

**Fix**:
```python
mol.add_style(mn.StyleBallAndStick(bond_find=True))
# Or after creation:
mol.styles[-1].bond_find = True
```
In the Geometry Nodes editor, check the `Bond Find` toggle on the Style Ball and Stick node.

### Surface style produces spiky/broken geometry

**Cause**: `quality` too low, or `probe_size` inappropriate for the molecule size.

**Fix**: Increase quality and adjust probe size:
```python
mol.add_style(mn.StyleSurface(quality=4, probe_size=1.4))
```

### Colors look wrong / washed out

**Cause**: Blender's color management. The default "Filmic" view transform desaturates colors.

**Fix**:
```python
canvas.view_transform = "Standard"  # Sharper, more saturated colors
```

### Materials look different between EEVEE and Cycles

**Cause**: EEVEE is a raster engine; Cycles is path-traced. Some MN materials (especially `AmbientOcclusion` and `Squishy`) rely on ray-traced effects.

**Fix**: This is expected behavior. Test in the target engine before final render. Use `mn.material.Default()` for the most consistent cross-engine results.

---

## Data & Import Issues

### Density .vdb files — "File not found" after moving .blend

**Cause**: When importing `.map` files, MN converts them to `.vdb` (OpenVDB) intermediate files. Blender stores an absolute path to these. Moving the `.blend` breaks the reference.

**Fix**: Keep `.vdb` files alongside the `.blend`. If you must move, re-import the density.

### Fetched structure is centered at the wrong position

**Cause**: Default behavior doesn't center the molecule.

**Fix**:
```python
mol = mn.Molecule.fetch("4ozs", centre="centroid")  # Center on centroid
mol = mn.Molecule.fetch("4ozs", centre="mass")       # Center on center of mass
```

### AlphaFold fetch fails or returns wrong structure

**Cause**: Using a PDB code instead of UniProt accession code, or the accession code is invalid.

**Fix**: AlphaFold requires **UniProt accession codes** (e.g., `"Q8W3K0"`), not PDB codes:
```python
# WRONG
mol = mn.Molecule.fetch("4ozs", database="alphafold")  # PDB code won't work

# CORRECT
mol = mn.Molecule.fetch("Q8W3K0", database="alphafold")
```

### World scale mismatch when mixing MN and custom geometry

**Cause**: MN uses 1 Angstrom = 1 cm (0.01 scale). Custom Blender objects default to meter scale.

**Fix**: Scale custom objects by 0.01, or use the `Angstrom to World` / `World to Angstrom` utility nodes.
```python
# A 10 Angstrom sphere in MN world scale:
radius_world = 10 * 0.01  # = 0.1 Blender units
```

---

## Selection Confusion

### MoleculeSelector vs MDAnalysis selection strings

This is the #1 confusion source. The two systems are NOT interchangeable:

| Entity | Selection System | Example |
|--------|-----------------|---------|
| `mn.Molecule` | `MoleculeSelector` or string shorthand | `mn.MoleculeSelector().is_peptide()` or `"is_peptide"` |
| `mn.Trajectory` | MDAnalysis selection strings or `AtomGroup` | `"resid 1 129 and name CA"` or `u.select_atoms(...)` |

```python
# WRONG — MDAnalysis syntax on a Molecule
mol.add_style("cartoon", selection="resid 100:150")  # Will fail or silently select nothing

# CORRECT — MoleculeSelector for Molecule
mol.add_style("cartoon", selection=mn.MoleculeSelector().res_id(100))

# CORRECT — MDAnalysis string for Trajectory
traj.add_style("cartoon", selection="resid 100:150")
```

### Selection string shorthand limitations

String shorthands like `"is_peptide"` work for both `Molecule` and `Trajectory`, but they only support single boolean attribute names. You cannot express complex logic (AND/OR) with strings — use `MoleculeSelector` chaining or MDAnalysis syntax instead.

### Trajectory selection selects nothing

**Cause**: MDAnalysis selection syntax error (fails silently).

**Debug**: Test the selection in MDAnalysis first:
```python
atoms = u.select_atoms("your selection string")
print(len(atoms))  # Should be > 0
```

Common syntax mistakes:
- `"resid 100-150"` — WRONG, use `"resid 100:150"`
- `"chain A"` — WRONG, use `"segid A"` or check your topology's chain representation
- `"resname ALA AND resname GLY"` — WRONG, use `"resname ALA or resname GLY"` (AND = impossible, no atom is both)

---

## Session & File Persistence

### Trajectory doesn't play after reopening .blend file

**Cause**: Missing `.MNSession` file.

**Fix**: The `.MNSession` file must stay alongside the `.blend` file. Both are needed to reconstruct the MDAnalysis Universe. If lost, re-import the trajectory.

### Styles disappear after undo/redo

**Cause**: Blender's undo system can invalidate MN's internal state. This is a known limitation.

**Fix**: Re-add styles or save before experimenting. The API does not support undo tracking.

---

## Version & Dependency Issues

### `pip install molecularnodes[bpy]` fails

**Cause**: Wrong Python version or numpy version.

**Fix**: MolecularNodes standalone requires **exactly Python 3.11** and **numpy 1.26**:
```bash
python3.11 -m pip install molecularnodes[bpy] numpy==1.26
```

### `ModuleNotFoundError: No module named 'biotite'` (Linux)

**Cause**: Python version mismatch on some Linux distributions.

**Fix**: Install Blender via Flatpak or Snap:
```bash
sudo snap install blender --classic
```

### ImportError inside Blender

**Cause**: Trying to `import molecularnodes` in a regular Python script (not inside Blender).

**Fix**: The `molecularnodes` package inside Blender is the addon itself. For standalone scripting, use `pip install molecularnodes[bpy]`. Inside Blender, the addon is already available after installation via Extensions.

---

## Geometry Nodes Pitfalls

### Style nodes cannot be chained

**Cause**: Each Style node consumes the input geometry and outputs new renderable geometry. Connecting one Style's output to another Style's input will not work as expected.

**Fix**: Use `Join Geometry` to combine multiple styles:
```
[Atoms] → [Style Cartoon] → [Join Geometry] → [Group Output]
[Atoms] → [Style Spheres]  →
```

### String attributes are integers

All molecular string data (chain IDs, residue names, atom names) is stored as integers because Geometry Nodes does not support string attributes. Use the Select/Attribute nodes or lookup tables in `references/data-formats-attributes.md` to interpret them.

### Modifying the node tree doesn't update the viewport

**Cause**: Blender's depsgraph hasn't been triggered.

**Fix**: In Python, call `bpy.context.view_layer.update()` after modifying nodes. In the GUI, just move a node or change any value to trigger a refresh. See `blender-api/references/gotchas-and-pitfalls.md` ("Stale Data & Deferred Updates" section) for the depsgraph update pattern.

---

## Performance Issues

### Viewport is extremely slow with large proteins

**Cause**: High `quality` values or `geometry="Mesh"` on large structures (>10k atoms).

**Fix**:
- Reduce `quality` parameter (2-3 is fine for viewport, increase for final render)
- Use `geometry="Point"` (Cycles) or `geometry="Instance"` (EEVEE) for spheres
- Reduce `subdivisions` on sphere styles
- Hide objects not being worked on

### Trajectory playback is slow

**Cause**: Large trajectory files, subframes, or expensive style computation per frame.

**Fix**:
- Reduce `subframes` (0 = no interpolation, fastest)
- Use simpler styles during preview (ribbon instead of cartoon)
- Disable `correct_periodic` if not needed
- Consider subsampling the trajectory in MDAnalysis before import:
```python
u = mda.Universe(top, traj)
# Only every 10th frame:
for ts in u.trajectory[::10]:
    pass
```
