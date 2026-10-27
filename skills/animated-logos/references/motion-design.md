# Motion design recipe

Use the brief to choose numbers; the profiles are starting points, not quality scores.

| Phase | Typical range | Observable result |
| --- | --- | --- |
| Gather | 0.5–0.9 s | Parts join around a deliberate shared symbol pivot. |
| Settle | 0.1–0.2 s | The original silhouette reads clearly. |
| Position | 0.35–0.65 s | Symbol reaches the final lockup without crossing arriving letters. |
| Letters | 0.06–0.12 s stagger | The actual wordmark paths arrive in sequence. |
| Hold | 1.5–3 s | Final identity remains intact and readable. |

Choose 2–5 parts that mean something geometrically: stem/bowl/leg, petals, facets or strokes. A complex silhouette may work better as one intact mark revealed by a matte. Preserve holes and fill rules. Use a shared assembly origin; a part's own center is often the wrong pivot for a radial gather.

For a scalar travel parameter `u` clamped to `[0,1]`, `3*u*u - 2*u*u*u` provides zero endpoint velocity. A cubic ease-out `1-(1-u)**3` suits a decisive gather. For a brief letter follow-through, use a damped residual such as `exp(-d*t)*cos(w*t)` and explicitly return the identity transform after the settle window. These curves are design choices, not numerical equivalents of every After Effects Easy Ease setting.

Use local elapsed time and explicit keyframes. A deterministic frame at time `t` must not depend on a previous frame, wall clock, browser animation loop or uncontrolled random state. Bake integer-frame samples when rendering across applications. The included toolkit intentionally leaves motion blur off so the sampled transforms can be compared directly; use a renderer-specific shutter/subframe workflow when the brief calls for blur.

## Lessons demonstrated by the Reply case

- Shared transforms matter at handoff: align the partition strip's final frame and the master strip's first frame using rounded frame indices, rather than two independently rounded seconds offsets.
- Complementary clip regions can still leave a visible alpha seam. An unsplit settled master restores the original edge coverage.
- An entering `R` can visually collide with the moving symbol even when the asset files are separate. Finish the symbol's travel before the first letter occupies that space, or revise the motion paths.
- Preserve existing scene timing and narration when the task changes only an outro. A sampled pixel comparison can establish that earlier scenes remain unchanged.

The case supplies tested techniques, not reusable brand artwork or customer audio. No Reply asset is included in this package.
