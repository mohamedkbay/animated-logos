# Portable pipeline

The toolkit uses existing Python 3.10+, Blender, Node/Playwright with an installed Chromium browser, and FFmpeg. Pillow is optional for contact sheets and image QA. It installs nothing and makes no external requests. Resolve available executables and libraries from the current environment; pass paths with spaces as quoted arguments. `NODE_PATH` can point to an existing shared Node package directory.

Let `SKILL` point to this installed skill directory and choose a fresh `PROJECT` output directory. Commands below are examples for a POSIX shell; equivalent argument lists work on other systems.

```sh
python3 "$SKILL/scripts/animated_logos.py" demo --project "$PROJECT" --profile clean
node "$SKILL/scripts/rasterize.cjs" "$PROJECT" --browser-executable "$CHROME"
python3 "$SKILL/scripts/animated_logos.py" sample --project "$PROJECT"
"$BLENDER" --background --python "$SKILL/scripts/blender_build.py" -- --project "$PROJECT" --render
python3 "$SKILL/scripts/animated_logos.py" encode --project "$PROJECT" --output "$PROJECT/preview.mp4"
python3 "$SKILL/scripts/animated_logos.py" contact-sheet --project "$PROJECT" --output "$PROJECT/review"
```

The original NOVA demonstration requires no font, customer asset, voice service, browser download or network connection. Profiles `clean`, `restrained`, and `elastic` use the same master geometry and different measured motion parameters. Keep this distinction in examples rather than using it as a fixed brand preference.

## Real-logo projects

Create full-canvas SVG or PNG layers from the supplied vector master. Keep original paths, counters and fill rules. Use a `part` layer for each meaningful partition, one `whole` master, and one `letter` layer for each independently shaped glyph/group. The demo plan is an editable example of the schema. The included motion code implements the assembly recipe, not arbitrary morphing or a general-purpose timeline editor.

`pivot` is measured from the top-left of the full canvas. Samples contain frame, alpha, x offset, y offset, scale x/y, clockwise rotation in degrees. Positive y points down. Blender reverses y/rotation signs; AE uses these image coordinates directly. Use `frame_range` to round timing consistently. The final master handoff and all part ends share the same frame index.

`rasterize.cjs` renders local SVGs with page JavaScript and network requests disabled. Embed licensed fonts/images in the SVG when needed. It refuses active or directly external SVG content; it is a local rendering helper, not a comprehensive SVG security validator. Treat third-party files as source material, inspect them and avoid executing bundled scripts.

Output files:

- `plan.json`: geometry paths, pivots and phase timing.
- `timeline.json`: optional shared frame samples for inspection/export.
- `assets/`: full-canvas PNG/SVG layers plus exact `final-master` artwork.
- `logo-motion.blend`: editable image strips with relative asset paths.
- `frames/`: deterministic render cache. `--scale 50` can make a quick review; build a fresh project at scale 100 for final delivery.
- `import-motion.jsx`: optional experimental After Effects import; see [after-effects.md](after-effects.md).

Keep `assets/` beside the `.blend`. The build and encoder refuse to overwrite existing project/video versions. PNG frames preserve alpha when the plan is transparent. The MP4 helper refuses transparent plans because H.264/yuv420p loses alpha; deliver RGBA PNGs or choose an alpha-capable codec explicitly. It produces a silent MP4; add a licensed/requested soundtrack in a project-specific mix rather than silently inventing narration or music.
