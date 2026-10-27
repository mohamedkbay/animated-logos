# Motion library and combinations

Run `animated_logos.py catalog` to inspect the maintained family/profile registry. These are original implementations of general motion techniques, not imported marketplace presets.

| Symbol family | Treatment | Matching wordmark |
| --- | --- | --- |
| `assembly` | Radial parts join and hand off to an exact whole master | Damped vertical `drop` |
| `orbit` | Parts travel around a shared center before joining | Curved side arrival |
| `pop` | A bounded scale overshoot resolves to the original shape | Short scale pop |
| `fold` | Parts open through planar scale/rotation offsets | Horizontal unfolding |
| `glitch` | Short deterministic position/rotation jitter settles completely | Brief position jitter |
| `wipe` | A horizontal crop/matte exposes the source progressively | Sequential matte reveals |

`fold` is a flat transform effect, not a 3D extrusion. `glitch` uses transform jitter, not a simulation of a particular commercial RGB effect. The matte operates in the full-canvas asset coordinates before transformation. `bounds_x` supplies the visible left/right reveal range; use measured artwork bounds rather than a glyph's advance width when matching a real logo.

Mix symbol and wordmark motions independently:

```sh
python3 "$SKILL/scripts/animated_logos.py" demo --project "$PROJECT" --family orbit --wordmark wipe --profile clean
```

`--wordmark` choices are `drop`, `orbit`, `pop`, `fold`, `glitch`, and `wipe`. Omitting it uses the matching default above. Profiles `clean`, `restrained`, and `elastic` adjust the assembly/drop parameters; they are not six additional families. The default `assembly`/`drop` behavior remains compatible with the initial release. Native Blender projects retain per-frame transforms and crop keyframes. Experimental JSX uses the same sampled transforms plus animated rectangle masks for wipes; runtime AE validation is still outstanding.

For GIFs, start from an encoded preview. The helper creates a palette-optimized looping GIF, preserving the requested aspect ratio:

```sh
python3 "$SKILL/scripts/animated_logos.py" gif --input "$PROJECT/preview.mp4" --output "$PROJECT/preview.gif" --width 640 --fps 15 --duration 4.5
```

A GIF is a lightweight visual preview. Retain the MP4/native source for full quality and editable timing. Looping deliberately restarts the reveal after the final hold. GIF export does not carry audio or promise partial alpha.
