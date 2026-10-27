# Validation and evidence

From the repository root:

```sh
python3 -m unittest discover -s tests -v
node --check skills/animated-logos/scripts/rasterize.cjs
```

For a real smoke test, follow [pipeline.md](pipeline.md) in a fresh directory. Render each profile, encode its video, and run:

```sh
python3 tools/verify_render.py --project "$PROJECT" --video "$PROJECT/preview.mp4"
```

The image check requires Pillow. It verifies a complete frame sequence, resolution and final-master raster error. The optional video check uses FFprobe to verify codec, pixel format, frame rate and duration. It does not judge visual taste, timing perception or audio intelligibility.

For GIF previews, run `python3 tools/verify_gif.py PREVIEW.gif --width 640 --duration 4.5` with the actual requested width/duration. It decodes the frames, verifies looping, checks duration and confirms there are multiple distinct visual frames. Keep GIF decoding evidence separate from the high-quality PNG/master check.

Inspect timestamped sheets through the moving interval at roughly 10 fps, plus the start/end of the hold. Look for collisions, clipped extents, seams, incorrect pivots, transient glyph distortions and unplanned pauses. Preserve a reviewed sheet and notes outside the installed skill.

Move/copy the example to a fresh directory with `assets/` and `plan.json` beside its `.blend`, then open it using Blender and run `tools/verify_blend.py`. This establishes relative-path portability on the tested platform. It does not establish cross-platform support for every browser or Blender release.

For the experimental JSX path, generate the script after rasterization and syntax-check a temporary `.js` copy with Node. Successful syntax/generation establishes only that; runtime AE verification requires actually running the script in AE and checking the composition against the same timeline/master. Keep that distinction in release notes.

Store evidence as a compact JSON report with the tested versions, tests run, output properties and untested paths. Exclude local absolute paths, customer files and credential values from published reports.
