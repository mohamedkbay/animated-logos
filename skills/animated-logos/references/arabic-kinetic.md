# Arabic kinetic typography and graphic idents

Use this recipe for Arabic word-led motion, numbered visual lessons, bold highlight blocks, shape transformations or a graphic logo reveal. Keep ordinary logo assembly on the existing Blender pipeline. This optional renderer adds a Canvas2D path; it does not replace that pipeline or make the existing PNG-layer tool support arbitrary path deformation.

## Read the visual argument

The studied vertical explainer presents six devices: a focus hook, a word match cut, connected Arabic extension, a shape morph, a camera travelling through layers, and a rolling counter. Its terminal shot shows a command-line rendering workflow. That is evidence of the presented method, not proof of a particular framework, source project, font or editor. Separate visible behavior from implementation choices inferred from the finished clip.

Build a short sequence around one idea at a time. A large word/object owns the center; the smaller explanation stays above it. A restrained progress marker ties the sections together. Use warm paper, near-black and one strong accent; invert the field at meaningful section boundaries. The included demonstration uses original words, shapes and layout with Cairo under OFL. Adapt its palette and geometry to the user's identity rather than treating the study's colors as permanent brand rules.

## Six executable devices

### 1. Focus hook

Place a short shaped word group on a fitted accent rectangle. Bring the pair into the focal area together over roughly 10–18 frames at 30 fps; let it settle before the next sentence. Introduce secondary cards in a short stagger. Preserve a readable hold after travel. For a logo, the rectangle is a reveal/accent device; finish on the unaltered logo master.

In AE, derive the backing rectangle from the shaped text bounds plus padding and parent it to the same transform. In Canvas, measure/render the whole word group and animate its shared position. Background and foreground use the same absolute clock.

### 2. Word match cut

Replace the large word at a precise frame while keeping its baseline, scale and visual center consistent. The continuity comes from the common composition, rather than a dissolve between two readable words. The demo cuts among three original verbs and moves a matching timeline marker. Use masks for an intentional partial-word wipe; keep masks separate from the cut itself.

AE can use held opacity/source-text keys on separately shaped word layers. A code renderer chooses the active word from absolute time. Evaluate the cut frame and both neighbors so a word is neither doubled nor blank.

### 3. Arabic extension at the connector

Shape the Arabic word as a whole before separating anything. Locate a thin, nonempty baseline connector with no dots, counters or decorative strokes in its column. Keep the left and right glyph artwork at its original size; translate one side and extend only that connector. Return extension to zero for the exact settled word. Whole-word horizontal scaling changes letter widths and stroke weight and is a different effect.

The example uses a pre-shaped Cairo word containing a static tatweel. It rasterizes that word at four times the logical size, selects a thin baseline column, and extends its opaque baseline core as a matching filled bridge. Faint neighboring glyph pixels are excluded from the bridge so they do not turn into a pale horizontal band. It supports this simple horizontal connector construction, not arbitrary Arabic calligraphy. If automatic selection fails, choose a suitable word and pass a measured logical `joinX`; inspect the column first. A connector crossing a curve, dot or counter needs different partitioning.

For an editable vector/AE version, shape and outline the supplied word, separate it at a legitimate join, and extend the baseline segment through path anchors or a matching filled bridge. Preserve surrounding control handles, diacritics, stroke weight and the zero-extension master. The demo's browser check verifies restoration after an excursion; visual inspection still determines whether the chosen join is attractive.

### 4. Shape morph

Use one continuous closed contour whose vertices correspond throughout the transition. Resample the source and target by arc length to equal point counts, normalize winding, then align their start indices to reduce travel. Interpolate positions with eased time. A crossfade between unrelated silhouettes is a different treatment.

The original demo transforms circle → rounded device → triangle → heart. Inspect intermediate contours for crossings and pinching, not only their endpoints. AE path interpolation likewise needs compatible vertex order/winding; it is not made reliable merely by adding more keyframes. The bundled polygonal implementation uses 80 samples; use native Bézier paths when a larger or editable deliverable needs them.

### 5. Camera through layers

Place foreground apertures and the final identity on separate depth planes. Project with `scale = focalLength / (cameraZ - layerZ)` and draw far-to-near. As the camera moves forward, the nearer opening expands faster than the background identity. Cull layers at/beyond the near plane so projection never explodes or reverses. A foreground aperture large enough to leave the frame gives a clean handoff as that plane is crossed.

The example calculates actual depth projection in Canvas; its panels are geometric cutouts, not a video compositing effect. AE can use 3D layers and one camera with the same depth relationships. Re-layout text for the final framing and give the settled identity a hold. Keep decorative camera marks small enough to remain secondary.

### 6. Rolling counter

Derive the value and bar fill from one eased, clamped progress value. Draw English digits in fixed-width columns under a common clipping window; roll each old digit out while the next rolls in. Reserve room for every digit and separator before the count begins. Clamp the terminal value exactly and hold it; random per-frame values lose the demonstrated cause/effect.

The demo target is configurable from 1 to 9999. AE may use source-text expressions or separate digit-column layers with masks. The checked implementation is the Canvas digit-column version. It does not include a tested AE preset or `.aep`.

## Run the original demonstration

Use existing Node, Playwright, Chromium and FFmpeg; the tool installs and downloads nothing. Choose a local licensed Arabic font and its full notice. `SKILL` points to the installed `animated-logos` folder, `PROJECT` to a fresh output directory.

```sh
node "$SKILL/scripts/kinetic_demo.cjs" init --project "$PROJECT" \
  --font "$FONT" --font-license "$FONT_LICENSE"
node "$SKILL/scripts/kinetic_demo.cjs" check --project "$PROJECT" \
  --browser "$CHROME"
node "$SKILL/scripts/kinetic_demo.cjs" render --project "$PROJECT" \
  --browser "$CHROME" --width 540 --fps 30 --output "$PROJECT/preview.mp4"
python3 "$SKILL/scripts/animated_logos.py" gif --input "$PROJECT/preview.mp4" \
  --output "$PROJECT/preview.gif" --width 360 --fps 15 --duration 18
```

For a shared dependency location, pass `--playwright-module /absolute/path/to/playwright`. Pass `--ffmpeg PATH` when FFmpeg is not on PATH. The browser defaults to Playwright's already-installed Chromium if `--browser` is omitted; that does not download a browser.

`plan.js` contains optional overrides such as `paper`, `ink`, `accent`, `hook`, `cutWords`, `stretchWord`, `joinX`, `maxExtension`, `target` and `brand`. A JSON file passed to `init --plan FILE` becomes those overrides. This study is intentionally six three-second scenes; longer narration or a different story requires editing the scene design, not stretching the movie. Open `index.html` for a local play/seek preview. `renderAt(t)` and the renderer depend on explicit time; the interactive playback clock is only a viewer.

Rendering produces a silent 18-second MP4, sampled PNGs in `review/`, and a compact report. The encoded example is a motion study with demonstration wording, not a finished customer advertisement. Keep reference recordings/audio outside the public package and use requested/licensed sound only in a separate project mix.

## Verify the useful invariants

Run the Node geometry tests as well as the existing suite. Run `check` against the actual chosen font: it checks random-seek determinism, Arabic master restoration, a nonempty join, and the exact counter endpoint. Review the moving intervals for clipping, unplanned glyph changes, seams and unreadable holds. Inspect 30 fps output around cuts and the layer crossings, then the final counter hold. The included AE mappings are implementation guidance; runtime AE verification remains outstanding.
