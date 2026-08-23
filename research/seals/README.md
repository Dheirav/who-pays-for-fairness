# External timestamp receipts for sealed protocols

Each `<name>-<shorthash>.txt` holds a seal commit's full hash; the `.ots` beside it is
an OpenTimestamps receipt anchoring that hash via public calendar servers into the
Bitcoin blockchain, so the seal's existence at stamping time no longer rests on this
repository's own clock. Verify with `ots verify <file>.ots` (needs the client from
`requirements.txt`); receipts start as pending calendar attestations and are upgraded
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
