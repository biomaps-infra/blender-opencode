# Data Formats & Attributes

## Table of Contents
1. [Supported File Formats](#supported-file-formats)
2. [Data Sources](#data-sources)
3. [World Scale](#world-scale)
4. [Point Attributes (Per-Atom)](#point-attributes-per-atom)
5. [Edge Attributes (Per-Bond)](#edge-attributes-per-bond)
6. [Residue Name Lookup Table](#residue-name-lookup-table)
7. [Atom Name Lookup Table](#atom-name-lookup-table)
8. [Geometry Domains](#geometry-domains)
9. [Data Pipelines](#data-pipelines)

---

## Supported File Formats

### Static Structures (via Biotite)

| Format | Extension(s) | Notes |
|--------|-------------|-------|
| BinaryCIF | `.bcif` | Default download format from RCSB. Compact binary mmCIF encoding. |
| mmCIF / PDBx | `.cif`, `.pdbx` | Standard macromolecular CIF format |
| PDB | `.pdb` | Legacy Protein Data Bank format |
| SDF | `.sdf` | Structure-Data File for small molecules |
| MOL | `.mol` | MDL Molfile for small molecules |

### MD Trajectories (via MDAnalysis)

MDAnalysis supports ~40+ topology/trajectory format combinations. Common ones:

| Type | Formats |
|------|---------|
| Topology | PSF, PDB, GRO, TPR, PRMTOP, PDB, and more |
| Trajectory | DCD, XTC, TRR, XYZ, NetCDF, LAMMPS, and more |

Topology and trajectory files are provided separately.

### Density / Volume Data

| Format | Extension(s) | Notes |
|--------|-------------|-------|
| MRC/CCP4 Map | `.map`, `.map.gz` | CryoEM density. Converted to `.vdb` on import. |
| OpenDX | `.dx`, `.dx.gz` | APBS electrostatic maps, solvent density grids |

Uses MDAnalysis's **GridDataFormats** library.

### Other Formats

| Format | Notes |
|--------|-------|
| RELION Star | `.star` — CryoEM particle positions/orientations |
| cisTEM Star | `.star` — CryoEM particle data (different rotation convention) |
| oxDNA | Coarse-grained DNA/RNA simulation data |
| IMD Protocol | `imd://localhost:8889` — Real-time streaming from running simulations |

---

## Data Sources

| Source | Access Method | Details |
|--------|--------------|---------|
| **RCSB PDB** | `Molecule.fetch(code, database="rcsb")` | Default. Downloads `.bcif`. Cached in `~/.MolecularNodes/` |
| **AlphaFold** | `Molecule.fetch(code, database="alphafold")` | UniProt accession codes (e.g., `"Q8W3K0"`). `b_factor` = pLDDT |
| **Local Files** | `Molecule.load(path)` | Any supported format |
| **MDAnalysis** | `Trajectory(mda.Universe(top, traj))` | Any MDAnalysis-supported format pair |
| **EMDB** | Manual download + density import | EM density maps |
| **IMD Stream** | `imd://hostname:port` as trajectory path | Live-streaming from GROMACS or similar |

---

## World Scale

| Property | Value |
|----------|-------|
| Current scale | 1 Angstrom = 1 cm (factor `0.01`) |
| Blender 5.0 | Will change to 1 nm = 1 m (factor `0.1`) |
| `Trajectory.world_scale` | Default `0.01`, configurable |

All imported coordinates are multiplied by the world scale factor. VDW radii and other distance attributes are also scaled.

---

## Point Attributes (Per-Atom)

Stored on the **Point** domain (one value per vertex/atom).

| Attribute | Type | Description |
|-----------|------|-------------|
| `Position` | Vector | 3D coordinates, scaled by world_scale (0.01) |
| `b_factor` | Float | Temperature factor; **pLDDT** for AlphaFold structures |
| `vdw_radii` | Float | Van der Waals radius in world space (~0.015) |
| `sec_struct` | Int | 0=non-protein, 1=helix, 2=sheet, 3=loop |
| `mass` | Float | Atomic mass |
| `chain_id` | Int | Chain identifier (sorted alphabetically, starting at 0) |
| `entity_id` | Int | Entity identifier (same protein across chains shares entity_id) |
| `res_name` | Int | Residue name (integer lookup — see table below) |
| `res_id` | Int | Residue sequence number within chain |
| `ures_id` | Int | Unique residue ID across whole structure (starts at 0) |
| `atomic_number` | Int | Periodic table number (1=H, 6=C, 7=N, 8=O, etc.) |
| `atom_name` | Int | Atom name (integer lookup — see table below) |
| `Color` | Color | RGBA color, often set by Color nodes |
| `atom_id` | Int | Unique ascending atom ID starting at 1 |
| `is_alpha_carbon` | Bool | True for CA atoms |
| `is_side_chain` | Bool | True for side chain atoms |
| `is_backbone` | Bool | True for backbone atoms |
| `is_solvent` | Bool | True for solvent molecules |
| `is_nucleic` | Bool | True for nucleic acid atoms |
| `is_peptide` | Bool | True for peptide/protein atoms |
| `is_hetero` | Bool | True for heteroatoms (non-standard residues) |
| `is_carb` | Bool | True for carbohydrate atoms |

---

## Edge Attributes (Per-Bond)

Stored on the **Edge** domain (one value per bond).

| Attribute | Type | Values |
|-----------|------|--------|
| `bond_type` | Int | 0=ANY, 1=SINGLE, 2=DOUBLE, 3=TRIPLE, 4=QUADRUPLE, 5=AROMATIC_SINGLE, 6=AROMATIC_DOUBLE, 7=AROMATIC_TRIPLE |

---

## Residue Name Lookup Table

Strings are stored as integers because Geometry Nodes does not support string attributes.

### Standard Amino Acids (alphabetical)

| Int | Residue | Int | Residue | Int | Residue | Int | Residue |
|-----|---------|-----|---------|-----|---------|-----|---------|
| 0 | ALA | 5 | GLU | 10 | LEU | 15 | SER |
| 1 | ARG | 6 | GLY | 11 | LYS | 16 | THR |
| 2 | ASN | 7 | HIS | 12 | MET | 17 | TRP |
| 3 | ASP | 8 | ILE | 13 | PHE | 18 | TYR |
| 4 | CYS | 9 | LEU | 14 | PRO | 19 | VAL |

### Modified Residues (map to parent)

| Modified | Maps to | Int |
|----------|---------|-----|
| MSE (selenomethionine) | MET | 12 |
| SNC | SER | 15 |
| ASH (protonated ASP) | ASP | 3 |
| GLH (protonated GLU) | GLU | 5 |
| HID, HIE, HIP, HYP | HIS | 7 |

### Nucleic Acids

| Int | Name | Type |
|-----|------|------|
| 30 | DA | DNA |
| 31 | DC | DNA |
| 32 | DG | DNA |
| 33 | DT | DNA |
| 40 | A | RNA |
| 41 | C | RNA |
| 42 | G | RNA |
| 43 | U | RNA |

**Unknown residue**: `UNK` = `-1`

---

## Atom Name Lookup Table

### Backbone Atoms

| Int | Name | Description |
|-----|------|-------------|
| 1 | N | Backbone nitrogen |
| 2 | CA | Alpha carbon |
| 3 | C | Backbone carbonyl carbon |
| 4 | O | Backbone carbonyl oxygen |

### Common Side Chain Atoms

| Int | Name | Int | Name |
|-----|------|-----|------|
| 5 | CB | 11 | CE |
| 6 | CG | 12 | CE1 |
| 7 | CG1 | 13 | CE2 |
| 8 | CG2 | 14 | CZ |
| 9 | CD | 15 | NZ |
| 10 | CD1 | ... | ... |

### Nucleic Acid Atoms

Phosphate/sugar backbone atoms start at **P=50** and continue through the sugar ring and bases.

---

## Geometry Domains

How Blender Geometry Nodes domains map to molecular data:

| Domain | Usage in MolecularNodes |
|--------|------------------------|
| **Point** | Atoms (vertices), curve control points |
| **Edge** | Chemical bonds |
| **Face** | Generated geometry (surfaces, cartoon faces) |
| **Corner** | Face corners on generated geometry |
| **Curve** | Backbone ribbons, DNA helices |
| **Instance** | Instanced geometry (assemblies, sphere styles, starfile particles) |

---

## Data Pipelines

### Static Structure Pipeline

```
1. Fetch/Load file (Biotite parses .bcif/.pdb/.cif/.sdf/.mol)
2. Create AtomArray (numpy-backed)
3. Create Blender mesh: vertices=atoms, edges=bonds
4. Store all attributes on mesh (string→int conversion)
5. Create Geometry Nodes modifier
6. Apply Color → Select → Style nodes
7. Output: renderable 3D geometry
```

### MD Trajectory Pipeline

```
1. Create MDAnalysis Universe from topology + trajectory
2. Create Blender mesh from first frame
3. Store topology-derived attributes
4. On each Blender frame change:
   a. MDAnalysis reads corresponding trajectory frame
   b. Vertex positions updated on mesh
   c. Dynamic selections/DSSP recomputed if enabled
   d. Geometry Nodes pipeline re-evaluates
5. .MNSession file saved alongside .blend for persistence
```

### Density Pipeline

```
1. Load .map/.dx via GridDataFormats
2. Convert to .vdb (OpenVDB) if needed
3. Import as Blender Volume object
4. Apply Style Density Surface/Wire node
5. Isosurface mesh generated at threshold
6. Optional: Sample colors from companion atomic structure
```

### Ensemble / Assembly Pipeline

```
1. Parse assembly instructions from structure file
2. Create MN_assembly_ node with rotation/translation matrices
3. Instance chains at assembly positions
4. Supports multiple assembly IDs
```

### Starfile Pipeline

```
1. Parse .star file (RELION or cisTEM format)
2. Create point cloud with per-particle attributes
3. Apply rotation nodes (Rotation RELION or Rotation cisTEM)
4. Instance molecular structures at each particle position/orientation
```

### Import/Export Notes

- MolecularNodes is primarily an **import and visualization** tool. No molecular data export.
- Standard Blender export (OBJ, FBX, glTF, USD) applies to the generated 3D geometry.
- Rendered images/animations export through Blender's standard render pipeline.
