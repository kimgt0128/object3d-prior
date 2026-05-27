---
title: Scope CV Final Projects To Coarse Room Object Priors
date: 2026-05-27
category: docs/solutions/workflow-issues
module: project-planning
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - Planning a short computer vision final project from a broad 3D reconstruction idea
  - Converting SAM2 or VGGT experiments into a graded deliverable
  - Deciding whether to target full room reconstruction or object-level 3D priors
tags: [computer-vision, final-project, scope-control, sam2, vggt, object-prior]
---

# Scope CV Final Projects To Coarse Room Object Priors

## Context

The project can easily drift toward "reconstruct the whole room as a clean textured 3D mesh." That sounds impressive, but it creates too many coupled risks for a two-week computer vision final project: video capture quality, camera pose stability, dense reconstruction quality, mesh generation, metric scale, privacy handling, and visualization.

The safer and stronger framing is:

```text
small static room video
  -> coarse 3D room point cloud
  -> rough floor/wall/table plane candidates
  -> selected objects as fused 3D object priors
  -> measurement and failure analysis
```

This preserves the interesting computer vision story while keeping the deliverable feasible on local Mac MPS and school RTX 30/40 hardware.

## Guidance

Frame the final project as **object-centered 3D scene understanding**, not full scene reconstruction.

Use this scope boundary:

- In scope: sparse/dense-ish room point cloud from selected keyframes.
- In scope: rough dominant planes for room/table context.
- In scope: 2-3 object-level 3D point clouds and oriented bboxes.
- In scope: mask cleanup, point cloud cleanup, measurement error, and failure analysis.
- Out of scope: complete textured mesh, learned 3D completion, automatic whole-room semantic parsing.

When planning T-units, keep each PR independently demonstrable:

1. Video keyframe extraction.
2. VGGT batch geometry.
3. Keyframe object segmentation.
4. Object-aware multi-view fusion.
5. Coarse room cloud and plane summary.
6. Measurement evaluation and final report.

Keep the user-facing explanation consistent:

```text
We are not claiming to fully reconstruct the room.
We are using a static room video to build enough 3D context
to estimate selected object locations, dimensions, and orientation.
```

## Why This Matters

Full room mesh reconstruction is a trap for this timeline. It makes the project dependent on the hardest and least controllable parts of the stack. A coarse room plus object priors still demonstrates segmentation, depth/pose estimation, masked back-projection, multi-view fusion, bbox fitting, cleanup, and quantitative evaluation.

This scope also creates a better final report. Instead of showing one fragile "it kind of reconstructed my room" output, the report can compare:

- frame-level masks vs fused object priors
- cleanup before vs after
- predicted dimensions vs measured dimensions
- easy objects vs transparent/reflective/thin failure cases

That gives the project a clear computer vision argument and a defensible failure analysis.

## When to Apply

- A user asks whether a small room can be reconstructed in 3D within a short course-project timeline.
- The implementation already has segmentation and geometry pieces but lacks robust scene-level fusion.
- Hardware is limited to local Apple Silicon/MPS or consumer RTX 30/40 GPUs.
- The deadline rewards a coherent, evaluated demo more than an over-scoped raw reconstruction.

## Examples

Avoid this project claim:

```text
This project reconstructs a complete 3D model of a room from a phone video.
```

Use this claim instead:

```text
This project reconstructs a coarse room point cloud from selected video keyframes
and estimates object-level 3D priors for user-selected objects using SAM2 masks
and VGGT geometry.
```

Avoid this acceptance criterion:

```text
The room mesh should look clean and complete.
```

Use these acceptance criteria instead:

```text
- A coarse room point cloud is generated from selected keyframes.
- At least one floor/wall/table plane candidate is summarized.
- At least two selected objects have fused point clouds and oriented bboxes.
- At least two objects have measured dimension error tables.
- At least one failure case is explained with visual evidence.
```

## Related

- Issue #58
- `docs/superpowers/plans/2026-05-27-room-object-3d-prior-final-project.md`
- `docs/PLAN.md`
- `docs/runbooks/20260526-general-sam2-3d-cleanup.md`
- `docs/validation/20260526-real-laptop-multiview-vggt-validation.md`
