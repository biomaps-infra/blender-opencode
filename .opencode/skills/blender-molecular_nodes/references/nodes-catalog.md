# Full Node Catalog

Complete reference for all ~160 MolecularNodes custom Geometry Nodes. For the most commonly used nodes with examples, see `nodes-essential.md` first.

## Table of Contents
1. [Style Nodes (7)](#style-nodes)
2. [Color Nodes (25)](#color-nodes)
3. [Select Nodes (30)](#select-nodes)
4. [Attribute Nodes (18)](#attribute-nodes)
5. [Animate Nodes (12)](#animate-nodes)
6. [Simulation Nodes (17)](#simulation-nodes)
7. [Topology Nodes (30)](#topology-nodes)
8. [Field Nodes (37)](#field-nodes)
9. [Density Nodes (3)](#density-nodes)
10. [DNA Nodes (6)](#dna-nodes)
11. [Ensemble Nodes (10)](#ensemble-nodes)
12. [Curves Nodes (10)](#curves-nodes)
13. [Geometry Nodes (12)](#geometry-nodes)
14. [Utility Nodes (30)](#utility-nodes)

---

## Style Nodes

| Node | Key Inputs | Output |
|------|-----------|--------|
| **Style Spheres** | Geometry (Point/Instance/Mesh), Radius (0.8), Subdivisions (2), Material | Geometry |
| **Style Cartoon** | Quality (2), Peptide DSSP/Cylinders/Arrows/Rounded/Thickness/Width, Nucleic params, Color Blur, Material | Geometry |
| **Style Ribbon** | Quality (3), Backbone Smoothing/Threshold/Radius, Nucleic params, UV Map, Material | Geometry |
| **Style Surface** | Quality (3), Scale Radius (1.5), Probe Size (1.0), Relaxation Steps, Separate By, Material | Geometry |
| **Style Ball and Stick** | Quality (2), Sphere Geometry/Radius, Bond Split/Radius/Find/Find Scale, Material | Geometry |
| **Style Sticks** | Quality (3), Radius (0.2), Material | Geometry |
| **Style Presets 1-4** | Quality, Color Blur, Shade Smooth, Material | Geometry |

---

## Color Nodes

### Atom/Element Coloring
| Node | Description |
|------|-------------|
| **Set Color** | Set Color attribute on selected atoms |
| **Color Element** | Full periodic table (80 elements) |
| **Color Atomic Number** | Color single atomic_number |
| **Color Common** | Quick: H, C, N, O, P, S |

### Structure-Based Coloring (generated per import)
| Node | Colors by |
|------|----------|
| **Color Chain_** | chain_id |
| **Color Entity_** | entity_id |
| **Color Segment_** | segment_id |
| **Color Ligand_** | ligand |

### Property-Based Coloring
| Node | Description |
|------|-------------|
| **Color Res Name** | 20 amino acids + 8 nucleic acids |
| **Color Sec Struct** | Alpha Helix / Beta Sheet / Loop |
| **Color Backbone** | Backbone vs Side Chain |
| **Color Goodsell** | Darken non-carbon atoms |
| **Color pLDDT** | AlphaFold confidence (4 tiers) |

### Gradient/Mapped Coloring
| Node | Description |
|------|-------------|
| **Color Rainbow** | Rainbow spectrum along chain |
| **Color Attribute Map** | Map named attribute to color gradient |
| **Color Attribute Random** | Random color per attribute value |

### Color Space Utilities
| Node | Description |
|------|-------------|
| **Color Mix Intermediate** | Mix two colors with optional midpoint |
| **Color OKLab Mix** | Perceptually uniform mixing |
| **Color OKLab Offset** | Offset luminance/hue |
| **Color to OKLab** | RGB to OKLab |
| **OKLab to Color** | OKLab to RGB |
| **OKLab to LCh** | OKLab to LCh |
| **LCh to OKLab** | LCh to OKLab |
| **OKLab Offset LCh** | Offset via LCh |

---

## Select Nodes

### Identity Selections (structure-specific, generated per import)
| Node | Selects by |
|------|-----------|
| **Select Chain_** | chain_id toggles |
| **Select Entity_** | entity_id toggles |
| **Select Ligand_** | ligand toggles |
| **Select Segment_** | segment_id toggles |

### Attribute Selections
| Node | Key Inputs |
|------|-----------|
| **Select Atomic Number** | And, Or, atomic_number |
| **Select Element** | 80 element toggles |
| **Select Res Name** | 20 AA + 8 nucleic toggles |
| **Select Res ID** | Single res_id |
| **Select Res ID Range** | Min, Max |
| **Select Res ID_** | Multi-range (generated) |
| **Select Nucleic Type** | Purines vs pyrimidines |
| **Select Attribute** | Named boolean attribute |

### Molecular Property Selections
| Node | Tests |
|------|-------|
| **Is Peptide** | is_peptide |
| **Is Nucleic** | is_nucleic |
| **Is Lipid** | lipid atoms |
| **Is Solvent** | is_solvent |
| **Is Hydrogen** | atomic_number == 1 |
| **Is Alpha Carbon** | is_alpha_carbon |
| **Is Backbone** | is_backbone |
| **Is Side Chain** | is_side_chain (has Include CA toggle) |
| **Is Helix** | sec_struct == 1 |
| **Is Sheet** | sec_struct == 2 |
| **Is Loop** | sec_struct == 3 |

### Spatial/Topological Selections
| Node | Description |
|------|-------------|
| **Select Bonded** | Expand selection along bonds by depth |
| **Select Res Whole** | Expand to whole residue |
| **Select Cube** | Box selection from Empty_Cube |
| **Select Sphere** | Sphere selection from Empty_Sphere |
| **Select Proximity** | Distance-based from target geometry |

### Separation
| Node | Outputs |
|------|---------|
| **Separate Atoms** | Atoms, Inverted, Index |
| **Separate Polymers** | Peptide, Nucleic, Other |

---

## Attribute Nodes

### Identity
| Node | Output | Type |
|------|--------|------|
| **Chain ID** | chain_id | Int |
| **Atom ID** | atom_id | Int |
| **Entity ID** | entity_id | Int |
| **Residue ID** | res_id | Int |
| **Atomic Number** | atomic_number | Int |
| **Atom Name** | atom_name | Int |
| **Residue Name** | res_name | Int |

### Physical
| Node | Output | Type |
|------|--------|------|
| **Secondary Structure** | sec_struct | Int |
| **VDW Radii** | vdw_radii | Float |
| **Mass** | mass | Float |
| **B Factor** | b_factor | Float |
| **Color** | Color | Color |

### Computed
| Node | Outputs |
|------|---------|
| **URes ID** | ures_id, Size |
| **Residue Parameter** | Factor, Atom Count/Index, First/Last Atom Name/Index |
| **Chain Parameter** | Factor, Residue Count/Index, First/Last Res ID/Index |
| **Structure Parameter** | Atom/Residue Factor/Index/Count |
| **Unique Residue ID** | Group ID |
| **Unique Chain ID** | Group ID (with Threshold input) |

---

## Animate Nodes

| Node | Purpose | Key Inputs |
|------|---------|-----------|
| **Animate Frames** | Trajectory playback | Frames (Collection), Interpolate, Frame |
| **Animate Value** | Float interpolation | Frame Start/End, Value Min/Max |
| **Animate Trails** | Motion trails | Trail Frames/Radius/Cutoff |
| **Animate Wiggle** | Side-chain wiggle | b_factor, Amplitude, Speed, Animate |
| **Animate Peptide to Curve** | Align to curve | Curve, Offset, Start, End, Rotate, Twist |
| **Falloff Object** | Distance falloff from object | Object, From Min/Max |
| **Falloff Geometry** | Distance falloff from geometry | Target Geometry, From Min/Max |
| **Noise Vector** | 3D noise from position | Animate, Scale, Detail |
| **Noise Repeat** | Looping noise | Animate, Amplitude, Speed |
| **MN_animate_noise_position** | Positional noise | Amplitude, Scale |
| **MN_animate_noise_field** | Per-group noise | Field, Amplitude |
| **MN_animate_noise_repeat** | Looping field noise | Animate 0..1, Speed |

---

## Simulation Nodes

### High-Level
| Node | Purpose | Key Inputs |
|------|---------|-----------|
| **Simulate Elastic Network** | Mass-spring network | Mesh, Substeps, Force, Drag, Alpha, Hook/Pin |
| **Simulate Curve** | Curve physics | Geometry, Straightness, Segment Length |
| **Simulate on Faces** | Surface-constrained | Points, Faces, Alpha |

### Building Blocks
| Node | Purpose |
|------|---------|
| **Build Elastic Network** | Create spring edges (Alpha Carbon or All Atom) |
| **Is Backbone Edge** | Boolean for backbone edges |

### Forces
| Node | Inputs |
|------|--------|
| **Force Brownian** | Small, Large |
| **Force Mesh Collide** | Geometry, Collision Distance |
| **Force Gravity** | Gravity vector (default 0,0,-9.8) |

### XPBD Solver (low-level)
| Node | Purpose |
|------|---------|
| **XPBD Init** | Initialize solver |
| **XPBD Finalise** | Finalize step |
| **XPBD Solve Edges/Points/Curve/on Faces/Hook** | Constraint solvers |
| **Constraint Distance** | Distance computation |

---

## Topology Nodes

### Secondary Structure
| Node | Purpose |
|------|---------|
| **Topology DSSP** | Compute sec_struct from geometry |

### Dihedral Angles
| Node | Description |
|------|-------------|
| **Dihedral Phi / Psi** | Backbone angles |
| **Dihedral Chi Angle** (x2) | Side-chain angles |
| **Dihedral Nucleic Angle** | Nucleic acid dihedrals |

### Residue/Atom Masks
| Node | Description |
|------|-------------|
| **Residue Mask** | Pick atom by atom_name per residue |
| **Menu Residue Mask / Name** | Dropdown selection |
| **Menu Atom Name** | Dropdown atom name |

### Backbone Positions
| Node | Outputs |
|------|---------|
| **Backbone Positions** | O, C, CA, N, NH per residue |
| **Backbone N / CA / C / O / NH** | Individual atoms |

### Dihedral Manipulation
| Node | Purpose |
|------|---------|
| **Peptide Dihedral** | Rotate by phi/psi |
| **Peptide Chi** | Rotate chi X1-X5 |
| **Nucleic Dihedral / Chi** | Rotate nucleic angles |
| **Set Phi Psi / Nucleic Dihedral / Chi Angle** | Set absolute values |

### Utilities
| Node | Purpose |
|------|---------|
| **Set URes ID** | Assign unique residue IDs |
| **Backbone Vectors** | Normal, Tangent, Bitangent |
| **Edge Group ID** | Check shared Group ID |
| **Is Backbone Edge** | CA-CA edge in same chain |
| **Sample Atomic Attributes** | Transfer between atom sets |
| **Find Bonded Atom** | Find bonded by name/distance |

### Bond Operations
| Node | Purpose |
|------|---------|
| **Topology Find Bonds** | Distance-based bond finding |
| **Topology Break Bonds** | Remove bonds by distance/selection |
| **Bond Count** | Is Bonded, Bonds count |
| **Edge Info** | Full edge analysis |
| **Point Edge Angle** | Angle between edges |
| **Points of Edge** | Connected points |

---

## Field Nodes

### Index Mixing (5)
| Node | Type |
|------|------|
| **Index Mixed / Mix Float / Mix Vector / Mix Rotation / Mix Color** | Interpolate at fractional index |

### Sampling (5)
| Node | Type |
|------|------|
| **Sample Position / Mixed Float / Mixed Vector / Mixed Rotation / Mixed Color** | Sample from geometry |

### Offsetting (8)
| Node | Type |
|------|------|
| **Offset Index / Integer / Float / Color / Vector / Boolean / Rotation / Matrix** | Evaluate at offset index |

### Fallbacks (7)
| Node | Type |
|------|------|
| **Fallback Float / Vector / Integer / Boolean / Color / Rotation / Matrix** | Use named attribute or default |

### Group Operations (5)
| Node | Purpose |
|------|---------|
| **Group Info** | Size, Index, First/Last per Group ID |
| **Sub Group Info** | Sub-group decomposition |
| **Group Pick / Pick First** | Index of True per group |
| **Group Pick Vector** | Position of picked point |

### Other Fields (8)
| Node | Purpose |
|------|---------|
| **Relative Index** | Position within Group ID |
| **Attribute Run** | Increment on attribute change |
| **Boolean First / Last / Any** | Group-level boolean ops |
| **Integer Run** | New Group ID on value change |
| **Boolean Run Fill / Trim** | Fill gaps / trim runs |

---

## Density Nodes

| Node | Purpose | Key Inputs |
|------|---------|-----------|
| **Style Density Surface** | Isosurface from volume | Volume, Threshold, Hide Dust, Material |
| **Style Density Wire** | Wireframe isosurface | Volume, Threshold, Wire Radius |
| **Sample Nearest Atoms** | Transfer attributes from atoms | Atoms → Color, b_factor, chain_id, etc. |

---

## DNA Nodes

| Node | Purpose |
|------|---------|
| **MN_dna_double_helix** | Generate double helix from curve + bases |
| **MN_dna_bases** | DNA base instances with colors |
| **MN_dna_style_spheres_cycles** | Sphere style (Cycles only) |
| **MN_dna_style_spheres_eevee** | Sphere style (both engines) |
| **MN_dna_style_surface** | Surface representation |
| **MN_dna_style_ball_and_stick** | Ball and stick with double bonds |

---

## Ensemble Nodes

| Node | Purpose |
|------|---------|
| **MN_assembly_** | Build biological assembly from rotation/translation |
| **MN_assembly_center** | Center assembly on world origin |
| **Ensemble Instance** | Instance items onto points |
| **Periodic Array** | Replicate across periodic boundaries |
| **Periodic Box** | Get box vectors |
| **Periodic Image** | Single lattice point |
| **Lattice Grid** | Grid of lattice points |
| **Starfile Instances** | Instance at starfile positions |
| **Rotation RELION** | RELION star file rotation |
| **Rotation cisTEM** | cisTEM star file rotation |

---

## Curves Nodes

| Node | Purpose |
|------|---------|
| **Curve Vectors** | Normal, Tangent, Bitangent |
| **Curve Offset Dihedral** | Dihedral between offset points |
| **Curve Transform** | 4x4 matrix per point |
| **Curve Rotation** | Rotation from Normal+Tangent |
| **Cumulative Length** | Running length along splines |
| **Curve Offset Dot** | Dot product between offset normals |
| **Offset Point Along Curve** | Factor/Length at offset |
| **Curve Endpoint Values** | Different ints for start/end/middle |
| **Curve Visualize** | Debug gimbals |
| **Curve Custom Profile** | Curve to Mesh with profile |

---

## Geometry Nodes

| Node | Purpose |
|------|---------|
| **Split to Centred Instances** | Split by Group ID, origin at centroid |
| **Centre on Selection** | Move centroid to origin |
| **Separate First Point** | First point per Group ID |
| **Selected Instances** | Check instance selection state |
| **Slice Edge Instances** | Realize at selection boundary |
| **Primitive Arrow / Gimbal** | Debug primitives |
| **Contains / Fallback Geometry** | Empty geometry checks |
| **Plexus** | Edges between points within distance |
| **Visualize Points / Angle** | Debug visualization |

---

## Utility Nodes

### Unit Conversion
| Node | Direction |
|------|-----------|
| **Angstrom to World / World to Angstrom** | Angstrom ↔ Blender |
| **Nanometre to World / World to Nanometre** | nm ↔ Blender |

### Range Tests
| Node | Type |
|------|------|
| **Between Integer / Float / Vector** | Bounds check |

### Remapping
| Node | Purpose |
|------|---------|
| **Attribute Remap** | Remap named attribute (auto min/max) |
| **Field Remap** | Remap field values |

### Vector/Position
| Node | Purpose |
|------|---------|
| **Vector from Point** | Vector, Direction, Length to target |
| **Mix Position** | Position mixer |
| **Vector Direction** | Normalized direction |
| **Centroid** | Average position per Group ID |

### Math
| Node | Purpose |
|------|---------|
| **Fractionate Float** | Floor, Ceiling, Fraction |
| **Fraction Smoother** | Smoothstep easing |

### Rotation
| Node | Purpose |
|------|---------|
| **Rotation from ZYZ** | ZYZ Euler (electron tomography) |

### Transforms (11)
| Node | Purpose |
|------|---------|
| **Transform Scale** | Scale components independently |
| **Transform Relative / Mix / Local / Local Axis** | Relative transforms |
| **Transform Accumulate / Accumulate Point** | Per-group accumulation |
| **Accumulate Axis Rotation** | Accumulated rotations |
| **Transform from Object** | Object-based transform |

### Angles
| Node | Purpose |
|------|---------|
| **Vector Angle** | Angle between vectors |
| **Dihedral Angle** | ABCD dihedral |
| **3 Point Angle / 2 Point Angle** | Vertex angles |
| **Point Distance** | Vector, direction, distance |

### Other
| Node | Purpose |
|------|---------|
| **MN_utils_curve_resample** | Resample with field transfer |
