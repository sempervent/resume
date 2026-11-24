# Privacy

This repository is public. New canonical data does not include a street address, phone number, or personal email. Public résumé builds do not need `config/private.yaml`.

## What was removed from the current tree

Tracked `.tex` sources contained residential street addresses (an earlier Knoxville address in the root and 2019 files, and a later Knoxville address in 2020–2026 files). Those street lines were deleted from the tracked TeX. City and state remain. The ZIP codes that sat on those lines were removed with them.

`2024/` is an untracked local copy. The same street-line edit was applied on disk. That directory is not part of this branch.

## What is still published

Phone numbers and personal email addresses remain in the historical `.tex` files on this branch. Committed PDF résumés were not regenerated, so those binaries still contain the previous contact blocks, including street addresses.

Git history on `develop` and `master` still contains the street addresses, phone numbers, and email addresses. Deleting a line in a new commit does not remove it from history. This change does not rewrite history, force-push, or delete remote branches. A history rewrite needs an explicit decision from the owner because it rewrites commits other people may already have fetched.

The public DOTS README on GitHub also contains a personal email address. That repository was not modified.

`examples/application.example.yaml` uses Example Company. Real applications go in `private/`, which is gitignored. CI uploads only `dist/` PDFs produced without `--contact`.

## Generator rules

- `identity.yaml` carries city, region, and public profile links.
- `--contact` reads `config/private.yaml` for email and phone.
- A street-address key in that file is an error.
- `career-docs application` refuses an output directory inside the repo unless Git ignores it.
- `export-context` never receives the private contact file.

## Remaining risk

Anyone can still read historical blobs and the PDFs in this repository. Search engines and forks may already have copies. The practical follow-ups, if the owner wants them, are: remove or replace the committed PDFs on a new commit, scrub phone and email from tracked TeX the same way the street lines were scrubbed, and only then consider a history rewrite with a force-push plan.
