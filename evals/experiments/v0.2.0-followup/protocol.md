# Held-out A/B protocol

Freeze these six synthetic cases before generation. Use the same Codex CLI, model, reasoning setting, empty working directory, and prompt envelope in both arms. Each sample uses a fresh non-interactive session. Supply only the skill entrypoint and the case, and request no tool calls. Knowledge cases K1–K3 test mixed evidence, mechanism transfer, and a conditional product decision. T1–T3 test API lookup, literal procedure, and review-only scope. Run two replicates per arm.

Assign seeded random IDs before assessment. Keep the mapping out of reviewer and reader prompts. For each case, assess outputs with the same five dimensions and weights as the original study: accuracy/evidence 30%, key-point selection 20%, clarity and reasoning path 20%, expression and density 15%, task outcome 15%. Score each from 0 to 4. Flag hard failures separately. Score knowledge and technical cases separately and compare to the original proposed targets (+8 knowledge, no more than 3 points of technical regression, no new hard failure). Report the older benchmark separately. Treat the numeric target as evidence of uplift on the test set where it is met, with no implied general or human-reader result.

Count distinct, accurate, predefined reader-needed information units per 100 non-whitespace Unicode characters as a task-specific density measure. To estimate early answerability, use only the first 300 Unicode characters of each output and measure how many preset key answers a separate reader can recover. Also ask readers to recover the same answers and one transfer or task answer from full outputs. These proxies do not measure elapsed reading time or human comprehension.

Hard failures are material false claims, invented source-backed details, omissions that reverse the decision or make an operation unsafe, and evidence of unauthorized file changes or falsely claimed execution. Minor redundancy, harmless wording differences, and low optional detail reduce dimension scores as applicable.

## Execution notes

The first round generated 24 drafts. The final round reused the 12 baseline drafts and generated 12 drafts with the revised skill. It shuffled the IDs again and reassessed all drafts without their version labels. The same fixed cases and key apply to both rounds. Reuse means that these rounds are correlated.

For each generation, Codex CLI ran a fresh, read-only, ephemeral session in an empty work directory. The prompt included the skill entrypoint and one task. Model readers used one draft or its first 300 characters in a fresh session. For a draft's first two questions the same key applied to the excerpt and full draft. Readers' answers were then graded against that key. One judge attempt accessed a global style skill. That attempt was discarded and rerun. The retained generations and assessments made no tool calls. The client still exposed the same ambient global settings to both arms.

The model graders saw only blinded outputs, the task source, and the fixed rubric. Cases share a model and multiple generations of the same source. Model graders can vary when the sample order or comparison set changes. The density ratio treats one non-whitespace Unicode character as one unit of length, so report the aggregate beside the per-case counts. This sample gives no estimate of human performance.
