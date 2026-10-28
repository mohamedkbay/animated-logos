# Agent execution guide

Use this guide to turn a motion request into an actual checked artifact. Resolve `SKILL` from the location of the loaded `SKILL.md`, and select a project folder from the user's context. The public repository is `animated-logos-skill`; the installed folder and skill invocation remain `animated-logos`.

## Choose one pipeline

| Request | Implementation | Read next | Concrete output |
| --- | --- | --- | --- |
| Existing logo, symbol assembly, wordmark arrival | Blender logo pipeline | [pipeline.md](pipeline.md) and the relevant [motion family](motion-library.md) | Exact master assets, timeline, rendered frames, checked preview; `.blend` when requested |
| Arabic connector extension, word-led graphics, shape morph, camera depth, rolling counter | Optional Canvas motion study | [arabic-kinetic.md](arabic-kinetic.md) | Portable HTML/JS/font project, MP4, sampled PNGs, browser/media reports |
| After Effects import requested | Experimental sampled JSX export | [after-effects.md](after-effects.md) | Generated JSX; only report an executed composition or `.aep` after actually running AE |

The built-in Canvas study is six three-second scenes in portrait. It is a reproducible example, not a general scene editor. For another duration, aspect ratio or story, adapt the project/renderer deliberately instead of passing unsupported flags or treating the study as a completed customer video. Preserve a supplied logo's final geometry and the user's requested wording.

## Resolve the inputs

Use context for destination, dimensions, frame rate, duration, background and approved motion. Obtain only material inputs that are actually missing: the logo master for a logo-specific request, or a suitable licensed font for connected Arabic. An optional reference guides timing/geometry; it is not automatically an output asset. The default examples are silent. Use a supplied/requested soundtrack in the project-specific mix.

Keep code/artwork examples and explanations in the user's requested language. The distributed study has English explanations; the Arabic word is a shaping/connector specimen, not an Arabic instruction.

## Check existing tools

Run the installed helper with explicit paths when tools are outside PATH:

```sh
python3 "$SKILL/scripts/preflight.py" --pipeline canvas \
  --node "$NODE" --playwright-module "$PLAYWRIGHT_MODULE" \
  --browser "$CHROME" --ffmpeg "$FFMPEG" --ffprobe "$FFPROBE"
```

Choose `--pipeline blender --blender "$BLENDER"` for the logo pipeline. The JSON has `ready`, `missing`, individual `checks` and `nextAction`. Exit 0 means the checked environment is ready; exit 2 means a required tool was unavailable. This checks tools, not the validity of a customer's logo/font or the quality of a render. It installs/downloads nothing. Resolve missing tools from actual local installations; if unavailable, report the named blocker rather than inventing a successful render.

## Execute the selected path

Follow the selected reference's commands rather than mixing flags between tools. For the Canvas path:

1. `kinetic_demo.cjs --help` lists the supported commands and options.
2. `init` needs a fresh project directory, a local font and its license. A JSON `--plan` can customize documented fields. Unsupported fields and invalid values fail before project creation.
3. `check` exercises the actual browser/font and writes `browser-check.json`. A rejected connector requires another suitable word or a measured `joinX`, not an unshaped Arabic letter split.
4. `render` samples explicit time and checks the encoded width, height, frame count and duration with FFprobe before writing `render-report.json`. `--fps` overrides the plan's frame rate. Existing output versions are preserved; choose a new filename for a revision.
5. Inspect sampled PNGs over the moving interval and the final hold. Encoding and invariant checks establish technical behavior, not creative approval. Use the shared GIF helper only after a checked preview exists.

For Blender, preserve the full-canvas asset/pivot contract and master handoff described in its pipeline. Use `tools/verify_render.py` when working from the source repository; installed copies can run the stated endpoint/media checks with available local tools.

## Finish with evidence

Deliver the requested artifact and editable source when requested. Report the actual output path, measured dimensions/frame rate/duration, checks run and any material limit. Distinguish generated source, executed renderer, encoded media and tested host compatibility. A missing executable, failed process or missing output is unfinished work; report its concrete cause and keep reusable source files. Keep customer assets, narration, credentials, reference recordings and local tool paths outside public contributions.
