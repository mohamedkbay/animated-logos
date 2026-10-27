# After Effects mapping

Adobe's Graph Editor exposes value and speed changes; handle influence shapes acceleration. Translate the intended velocity into the chosen renderer and judge the resulting motion. Merely adding many eased keys does not establish a good speed graph.

| Design operation | After Effects approach | Included toolkit |
| --- | --- | --- |
| Gather a symbol | Shape groups or separate layers with deliberate anchor points | Full-canvas PNG layers, shared pixel pivot |
| Position the lockup | Position/Scale keys and speed graph | Sampled smooth travel |
| Stagger letters | Independent outlined glyph layers or suitable text animators | Separate original letter assets |
| Settle | Carefully shaped keys or a bounded damped expression | Bounded damped transform samples |
| Reveal a stroke | Shape paths with Trim Paths; mattes where appropriate | Use an external vector workflow |
| Restore master | Precomp/master layer at the matching transform | Exact whole-symbol handoff |

For Arabic, retain joining and shaping. Splitting a string into independent Unicode characters is not a reliable way to reconstruct the supplied wordmark. Use outlined brand paths or already shaped groups when matching a master.

`animated_logos.py ae-script --project PROJECT` emits `PROJECT/import-motion.jsx`. It imports PNG layers and applies the same per-frame position, anchor, scale, rotation and alpha samples as the Blender project. It creates a composition in the current AE project inside an undo group; it does not clear the project, save an `.aep`, publish or render. Run it in AE through File → Scripts → Run Script File when requested. The generated JSX is an experimental raster-layer interoperability route: it has passed generation/syntax checks but has not been executed in AE on the development machine. It does not create editable native shape paths or an `.aep` file by itself.

## Sources

Primary documentation consulted 2026-10-27:

- [Adobe: Speed and Graph Editor](https://helpx.adobe.com/after-effects/desktop/animate-in-after-effects/speed-between-keyframes/speed.html) — speed, timing and handle influence.
- [Adobe: Create dynamic movement with the Graph Editor](https://www.adobe.com/learn/after-effects/web/adjusting-keyframes-dynamic-movement) — Easy Ease and speed-graph workflow.
- [Adobe: Scripts](https://helpx.adobe.com/after-effects/desktop/automate-in-after-effects/automate-animation/scripts.html) — script execution and ExtendScript context.
- [Blender: Sequencer data storage](https://developer.blender.org/docs/features/sequencer/data_storage/) — transforms and image source storage.

The tutorial linked in the original conversation was studied as a movement reference. Its footage, artwork and audio are not distributed here. These notes are an original synthesis and tested implementation, not copied course material or a claim of model training.
