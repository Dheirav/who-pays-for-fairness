# External timestamp receipts for sealed protocols

Each `<name>-<shorthash>.txt` holds a seal commit's full hash; the `.ots` beside it is
an OpenTimestamps receipt anchoring that hash via public calendar servers into the
Bitcoin blockchain, so the seal's existence at stamping time no longer rests on this
repository's own clock. Verify with `ots verify <file>.ots` — full independent verification needs a local
Bitcoin node; without one, `ots info` shows the attested block height for checking
against any block explorer. The client is in `requirements.txt`. receipts start as pending calendar attestations and are upgraded
to full Bitcoin attestations with `ots upgrade <file>.ots` once the anchoring
transaction confirms (hours). The upgraded receipt is committed over the pending one
when that happens.

The anchor proves the hash existed *no later than* the attestation time. It cannot
prove the commit was not backdated relative to earlier local history — which is why
the practice, per the paper's Reproducibility section, is to stamp each seal commit
immediately after it is pushed.

| seal | commit | stamped |
|---|---|---|
| IPUMS third cohort, stage A (protocol) | `50d467f` | Bitcoin-attested |
| Cross-task shape seal (employment/coverage race arms) | `d8bfae8` | Bitcoin-attested; scored in `aa8d43a` (doc 60) |
| Regime deconfounding cell (attribute-aware in-processing) | `66bc4d5` | stamped 25 Aug, pending upgrade |
| Six-market lending seal (M1 crossover elevation, M2 protocol) | `08b27fa` | scored in `5870b9c` (doc 65): M2 fails 2/6, M1 underpowered |
| IPUMS third cohort, stage B (thresholds, op points, 60k subsample) | `a624cf5` | scored in `5870b9c` (doc 66): underpowered on all components |
| Race-arm cohort (screen-gated, Brazil White vs Black-or-Brown) | `2f16cda` | stamped 25 Aug, pending upgrade |
