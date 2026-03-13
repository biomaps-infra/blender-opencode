# Essential Nodes — The 20 Nodes That Solve 90% of Tasks

This file covers the most-used MolecularNodes Geometry Nodes with practical examples and common patterns. For the complete 160+ node reference, see `nodes-catalog.md`.

## Table of Contents
1. [Style Nodes (The Big 6)](#style-nodes)
2. [Selection Nodes (Top 5)](#selection-nodes)
3. [Color Nodes (Top 4)](#color-nodes)
4. [Animation Nodes (Top 3)](#animation-nodes)
5. [Density Nodes (Top 2)](#density-nodes)
6. [Common Node Graph Patterns](#common-node-graph-patterns)

---

## Style Nodes

These are the output nodes — they convert atomic data into visible 3D geometry.

### Style Cartoon — The Default Choice

Best for proteins. Shows helices, beta sheets, and loops.

| Key Input | Default | What to change |
|-----------|---------|----------------|
| Quality | 2 | Increase for final render (3-5), decrease for speed |
| Peptide DSSP | False | Set True if `sec_struct` not in file (computes from geometry) |
| Peptide Arrows | True | Arrow tips on beta sheets |
| Peptide Cylinders | False | Cylinder helices (David Goodsell style) |
| Peptide Loop Radius | 0.3 | Thicken/thin the loop tubes |
| Color Blur | True | Smooth color transitions between residues |

### Style Spheres — Space-Filling

VDW spheres. **Critical**: choose the right geometry type.

| Geometry | Engine | Performance | When to use |
|----------|--------|-------------|-------------|
| `Point` | Cycles only | Fastest | Quick Cycles preview |
| `Instance` | Both | Good | Default safe choice |
| `Mesh` | Both | Slowest | Maximum quality |

### Style Ball and Stick — Small Molecules

| Key Input | Default | What to change |
|-----------|---------|----------------|
| Bond Find | False | **Set True for ligands/small molecules** without bond data |
| Bond Split | False | True = two-tone bonds colored by each atom |
| Sphere Radius | 0.3 | Atom size |
| Bond Radius | 0.3 | Bond cylinder thickness |

### Style Ribbon — Quick Overview

Tube through alpha carbons. Simpler than Cartoon, no secondary structure differentiation.

| Key Input | Default | What to change |
|-----------|---------|----------------|
| Backbone Radius | 1.6 | Tube thickness |
| Backbone Threshold | 4.5 | Max CA-CA distance before chain break |

### Style Surface — Molecular Envelope

Solvent-accessible surface approximation.

| Key Input | Default | What to change |
|-----------|---------|----------------|
| Probe Size | 1.0 | Solvent probe radius (Angstroms). 1.4 = water |
| Scale Radius | 1.5 | VDW radius multiplier |
| Quality | 3 | Mesh resolution |
| Separate By | chain_id | Separate surface per chain vs single surface |

### Style Sticks — Minimalist

Clean stick representation. No configurable geometry type — always mesh.

| Key Input | Default |
|-----------|---------|
| Radius | 0.2 |

---

## Selection Nodes

### Select Chain_ (structure-specific)

Generated per-import. One Boolean toggle per chain. Connect output to any Style node's Selection input.

**Pattern**: Apply different styles to different chains:
```
[Select Chain (A=True, B=False)] → [Style Cartoon]    → [Join Geometry] → [Output]
[Select Chain (A=False, B=True)] → [Style Spheres]     →
```

### Is Backbone / Is Side Chain

Boolean fields for backbone vs side chain atoms.

**Pattern**: Ribbon backbone + Ball-and-stick side chains:
```
[Is Backbone]   → [Style Ribbon]           → [Join Geometry] → [Output]
[Is Side Chain] → [Style Ball and Stick]    →
```

### Select Res Name

Boolean toggles per amino acid (20) and nucleic acid (8). Use to highlight specific residue types.

### Boolean Math (built-in Blender node)

Combine selections with AND, OR, NOT:
```
[Select Chain (A only)] → [Boolean Math: AND] → [Style: Selection input]
[Select Res Name (ALA)] →
```

This creates a selection for "ALA residues on chain A only."

### Select Cube / Select Sphere

Dynamic spatial selections using Empty objects in the 3D viewport. The Empty can be animated to create time-varying selections.

---

## Color Nodes

### Color Common

Quick element coloring for H (white), C (gray), N (blue), O (red), P (orange), S (yellow). This is the default coloring.

### Color Chain_

Per-chain coloring. Structure-specific — generated per import with one color per chain.

### Color Attribute Map

Map any named attribute (default: `b_factor`) to a 2-3 color gradient. Essential for heatmaps.

| Input | Description |
|-------|-------------|
| Name | Attribute to map (e.g., "b_factor", "chain_id") |
| Min/Max | Value range for gradient |
| A / B | Start and end colors |
| Intermediate | Optional midpoint color |

### Color pLDDT

AlphaFold confidence coloring. Pre-configured with 4 tiers:
- Very Confident (>90): Blue
- Confident (70-90): Cyan
- Low (50-70): Yellow
- Very Low (<50): Orange

---

## Animation Nodes

### Animate Frames

The core node for MD trajectory playback. Connects to a Frames collection and interpolates atom positions.

| Key Input | Description |
|-----------|-------------|
| Frames | Collection containing frame data |
| Interpolate | Linear interpolation between frames |
| Smoother Step | Use smoother (non-linear) interpolation |

### Animate Wiggle

Procedural side-chain wiggle. Amplitude scales with `b_factor` (temperature factor). Loops seamlessly every 1.0 of the Animate input.

### Falloff Object

Distance-based falloff from an object in the scene. Animating the object creates a "wave" effect across the molecule.

---

## Density Nodes

### Style Density Surface

Isosurface from electron density volume data.

| Key Input | Description |
|-----------|-------------|
| Volume | Volume object (from density import) |
| Threshold | Density cutoff for surface generation |
| Hide Dust | Remove small disconnected surface fragments |

### Sample Nearest Atoms

Transfer attributes (Color, b_factor, chain_id, etc.) from a nearby atomic structure onto a density surface mesh. This is how you color a CryoEM surface by chain or element.

---

## Common Node Graph Patterns

### Pattern 1: Basic Protein Visualization

```
[Group Input] → [Color Common] → [Style Cartoon] → [Group Output]
```

### Pattern 2: Multi-Style with Selections

```
[Group Input] → [Select Chain (A)] → [Style Cartoon]      → [Join Geometry] → [Group Output]
[Group Input] → [Select Chain (B)] → [Style Spheres]       →
[Group Input] → [Is Side Chain]    → [Style Ball+Stick]    →
```

### Pattern 3: Colored by Attribute Gradient

```
[Group Input] → [Color Attribute Map (b_factor)] → [Set Color] → [Style Cartoon] → [Group Output]
```

### Pattern 4: Density + Atomic Structure

```
Density Object:
[Volume Input] → [Style Density Surface] → [Sample Nearest Atoms (from structure)] → [Group Output]

Structure Object:
[Group Input] → [Style Ribbon] → [Group Output]
```

### Pattern 5: Animated Trajectory with Wiggle

```
[Group Input] → [Animate Frames] → [Animate Wiggle] → [Style Cartoon] → [Group Output]
```

### Pattern 6: Spatial Selection with Animated Empty

```
[Group Input] → [Select Cube (Empty_Cube)] → [Style Ball+Stick]  → [Join Geometry] → [Group Output]
               → (no selection)             → [Style Cartoon]     →
```

Animate the Empty_Cube object to reveal different parts of the molecule over time.

### Anti-Pattern: Chaining Styles (WRONG)

```
[Group Input] → [Style Cartoon] → [Style Spheres] → [Group Output]
                                   ↑ This does NOT work as expected
```

Style nodes consume geometry. The Spheres node would try to create spheres from the Cartoon mesh, not from the original atoms. Always branch from the atomic data and use Join Geometry.

### Cross-Reference: General Geometry Nodes

For how to create node trees, add modifiers, link node sockets, and manage node groups in Python, see `blender-api/references/geometry-nodes.md`. MolecularNodes custom nodes appear in the Shift+A menu under the "Molecular Nodes" submenu.
