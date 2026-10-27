---
name: animated-logos
description: Animate existing logos into precise reveals, idents, and product-video outros. Use for symbol assembly, staggered wordmarks, reference-led logo motion, Blender delivery, or After Effects motion planning and JSX export.
license: MIT
---

# animated logos

Create a recognizable identity through motion, with the supplied logo restored exactly at the end. Use this skill in a coding agent with local file and terminal access, including Codex, Claude Code, Antigravity, or Gemini CLI. Resolve helper paths relative to this SKILL.md file, independently of the host agent. Preserve the user's existing renderer and approved project. The included renderer is a tested Blender sequencer workflow; the optional After Effects JSX exporter is a separate, explicitly experimental delivery path.

## Choose and shape the motion

Read the current project brief and approved assets before changing them. Resolve the logo master, desired duration/aspect ratio, background or transparency, and destination. Infer routine choices from context. Use an existing narration master to time an outro when one is supplied.

Study a supplied reference before selecting a recipe: identify what assembles first, pivot locations, velocity changes, overlap, letter order and final hold. Inspect the moving interval densely, plus the settled master. If the source cannot be played or downloaded, state that limitation and use an accessible preview or ask for the actual clip. Reference footage and audio remain study material unless reuse is authorized.

Select motion from the logo's geometry:

- **Assemble → position → wordmark:** a few meaningful symbol parts join, the complete symbol settles into its lockup, then letters arrive. Read [motion-design.md](references/motion-design.md) for timing and pivot choices.
- **Quiet reveal:** use restrained translation, alpha or a matte when the identity calls for minimal motion. Keep intact glyphs and counters readable.
- **Stroke or path reveal:** use actual vector paths and masks/trim tools in the chosen renderer. The bundled PNG-layer renderer handles transforms and alpha; choose an appropriate vector workflow for changing paths.

Shape the acceleration deliberately. Use a smooth travel curve for the lockup move and a short, damped follow-through for playful letters. Make the next focal point legible before introducing another. Arabic lettering follows its actual shaping and joining; use pre-shaped word groups or outlined text as needed, with a licensed font selected by the user.

## Build and verify

For code-driven Blender production, read [pipeline.md](references/pipeline.md). The toolkit can generate an original demo, sample a shared motion timeline, rasterize SVG layers, build an editable `.blend`, render frames and encode a preview. Reuse these helpers where they fit; adapt real brand assets rather than redrawing them as a similar-looking substitute.

The settled identity is an exact master asset. Switch from animated symbol partitions to that unsplit master on a shared sampled transform after assembly. This avoids accumulated clip-edge alpha seams. Give letters enough clearance from the symbol's travel; inspect the actual overlap frames rather than relying only on entrance times.

Render a short preview and inspect dense contact sheets through assembly, travel, letter arrival and the final hold. Compare the final render against the master at the intended transform. Check dimensions, duration, alpha/background and missing assets. Test audio only when requested or already part of the brief; retain supplied voice masters and use original or licensed effects.

Deliver the requested media and an editable source when requested. Keep the prior approved version. Ask for review when a meaningful creative decision remains; an already approved direction or an explicit final-render request permits the corresponding export. Routine rendering and local fixes do not need another approval cycle.

For After Effects, read [after-effects.md](references/after-effects.md). Describe the distinction between a generated JSX script, an executed AE composition, and a saved `.aep` accurately. This skill stores reusable instructions and tools; it does not retrain model weights or establish experience with an application that was not actually run.

## Extend the skill from use

Record a demonstrated failure, its correction, and an observable check in the project's review notes. Promote only recurring, general lessons into this skill. Put brand assets, private narration, local paths, account details and project-specific taste in that project's own directory. For versioned releases, run the unit checks and real render smoke test described in [validation.md](references/validation.md).
