# GitHub Copilot — pull request review

We use Copilot mainly to **review pull requests**, not to author large changes. Prioritize **security, correctness, and consistency** with existing patterns.

## Supply chain and dependency pinning

Flag changes that could weaken reproducibility or **increase supply-chain risk** (unexpected upgrades, mutable references, or installs that skip lockfiles).

### Python

- Prefer **pinned versions** in `requirements.txt` / `pyproject.toml` / constraints files. Call out new or loosened **unbounded** specs (`package`, `package>=x` without upper bound when the repo uses strict pins elsewhere, `package==*`).
- If the project uses **`requirements.lock.txt`** (or another lockfile) and **`scripts/deps.sh`** / `uv pip compile`, flag PRs that change `requirements.txt` **without** updating the lockfile, or that install with `pip install -r requirements.txt` **without** the lock in Docker/CI when installs are expected to be locked.
- **VCS dependencies**: flag `git+https://...` / SSH URLs that use **branch or moving tags** instead of **immutable refs** (commit SHA, or for trusted org repos a **version tag** if that matches team policy). Treat `@main`, `@master`, `@develop`, and unqualified refs as high risk for production paths.
- Watch for **`--extra-index-url`**, ad-hoc `pip install` in CI/Docker, or disabling hash/verify options.

### JavaScript / TypeScript

- Flag **new** loose ranges in `package.json` (`*`, `latest`, or broad `^`/`~`) when the repo otherwise pins or relies on **lockfiles** (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`). Ensure lockfiles are updated when dependencies change.
- Call out scripts that use **`npm install`** instead of **`npm ci`** (or pnpm/yarn equivalents) in CI when determinism matters.

### Docker and images

- Prefer **digest-pinned** or **immutable tag** `FROM` images. Flag `FROM image:latest` or tags that look like rolling releases when the rest of the stack pins.
- Flag **`curl | sh`**, **`wget | bash`**, or fetching unpackaged artifacts without checksum verification.

### GitHub Actions

- Prefer **pinned action versions** (commit SHA, or at least a major version tag). Flag new uses of `@main` / `@master` on third-party actions.
- Flag workflows that **stop running** dependency checks (lockfile checks, audit steps, `npm ci`, etc.) without a clear reason.

### General

- When dependency changes are intentional, reviewers should still see **what** resolved versions changed and **why** (changelog, CVE, feature need).
- Distinguish **internal org** packages from **third-party** sources; third-party and transitive risk deserves stricter immutability.

If a PR only touches application logic, a short note that **no dependency surface changed** is enough. If it touches manifests, lockfiles, Docker, or CI install paths, **explicitly review pinning and install commands**.
