# Arabic kinetic study — 2026-10-28

A user-supplied vertical explainer was inspected at 360×640, 30 fps, approximately 40 seconds. The visible creator credit is `@KHAAM.HQ`. The original reference, frames, audio and its brand artwork remain outside this public repository. This document records observed motion concepts and an independently implemented example, not the original project/source code or an audio transcript.

## What the lesson demonstrates

| Approximate reference interval | Observed lesson | Reusable mechanism |
| --- | --- | --- |
| 0–4.6 s | Focus/attention hook with highlighted Arabic word and small numbered cards | Shared word/backing transform; sentence beats; card stagger; readable hold |
| 4.6–8 s | Word cut between a large centered word and the next shot/word | Match baseline and focal scale; replace at the cut frame; timeline cue |
| 8–13.7 s | Connected Arabic word extends while glyphs retain their weight | Partition at a real baseline connector; extend the join and move the sides |
| 13.7–17.2 s | Circle transforms into a device, triangle and heart | Compatible continuous paths; eased vertex interpolation |
| 17.2–21.7 s | Camera moves through nested foreground/background identity layers | Depth planes, perspective scale, apertures, near-plane culling |
| 21.7–25.6 s | The numeral rolls up, accompanied by a segmented progress bar | Time-driven integer/digit columns and synchronized progress |
| 25.6–28.8 s | Graphic recap and a terminal showing a `node src/render.js` command | The presentation advocates rendering from code; the exact engine is not established |
| 28.8–33.7 s | A phone mockup demonstrates a comment/reply call to action | Sequential UI states in one framed composition |
| 33.7–40 s | Creator identity and social outro | Centered lockup, hold, small accent motion |

Times are visual estimates from sampled frames, not a word-aligned transcript. The reference contains visible narration captions, but its voice/music is not included in the demonstration. Editor/framework, exact typeface, original easing curves and source paths cannot be recovered with certainty from the finished movie alone.

## Implementation added here

The [portable recipe](../skills/animated-logos/references/arabic-kinetic.md) explains the six techniques and their AE equivalents. The optional [Canvas renderer](../skills/animated-logos/assets/kinetic-type/engine.js) implements all six with original wording/artwork. It samples absolute time, shapes Arabic in a licensed font, extends a suitable existing connector, morphs compatible contours, projects depth planes, and rolls a bounded counter.

The [18-second example](../examples/arabic-kinetic/) is a compact demonstration of the techniques. It uses Cairo 700 (OFL), original NOVA demonstration identity, no source footage and no audio. Its purpose is to make the skill reproducible. It is not represented as an After Effects composition or a reconstruction of the creator's exact source project.
