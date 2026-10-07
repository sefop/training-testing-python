# Release a new model safely (Python)

The theory is [6. Release a new model safely](https://github.com/sefop/sefop-training-hub/blob/main/book/06-deployment/README.md#ch-safe-release).
For packaging, read [4. Package the model with its solver](https://github.com/sefop/sefop-training-hub/blob/main/book/06-deployment/README.md#ch-packaging).

Deploy a working decision-support system, assess a supplied solver change, release it after checks
pass, and restore the baseline. The application maximizes calories within budget and weight limits.
You use its existing Dockerfile; writing a Dockerfile is not part of this exercise.

All training material lives here. The application is
[sefop-python-advanced](https://github.com/sefop/sefop-python-advanced); make changes only in your
own fork. Neither your reports nor your deploy hook belong in its upstream repository.

## What you need

- Git, Python 3.12, and Docker with a running engine. Docker Desktop is a way to run Docker on
  Windows or macOS. Its [installation guide](https://docs.docker.com/desktop/) covers setup.
- Your own GitHub account and fork of the application. GitHub Actions runs the supplied checks.
- Your own Render account. Render is an application hosting service that can build a Dockerfile
  from a connected repository. Use a **Free web service** for this exercise.

Read [Render's free-service limits](https://render.com/docs/free): the service can sleep while idle,
startup can take about a minute, compute is limited, local files are temporary, and rollback history
is limited. This is a training deployment, not a production capacity recommendation. Use the
supplied inputs; no business data, database, custom domain, or commercial solver license is needed.

The application uses SCIP through Google's OR-Tools optimization library and HiGHS through its
Python library. Both are open-source mixed-integer solvers included by the supplied Dockerfile.
The comparison helper uses only Python's standard library.

## 1. Prepare an identified baseline

Clone the training repository and your application fork into sibling directories. Replace YOUR_USER
with your GitHub username:

```text
git clone https://github.com/sefop/training-testing-python.git
git clone https://github.com/YOUR_USER/sefop-python-advanced.git
cd sefop-python-advanced
git status --short
```

This exercise targets application revision **4a1a8946b726e174f0c27ac33b9f7d41810c106a**. Use a fresh
fork clone with no local edits. If its main branch has moved since that revision, restore the
documented tracked files into your fork and commit them before continuing:

```text
git restore --source=4a1a8946b726e174f0c27ac33b9f7d41810c106a --staged --worktree .
git diff --cached --stat
```

If that shows changes, commit them with a message such as "Use documented training baseline".
If Git cannot find the revision, fetch it from the upstream repository before restoring:

```text
git fetch https://github.com/sefop/sefop-python-advanced.git 4a1a8946b726e174f0c27ac33b9f7d41810c106a
```

Copy [cd-deploy.yml](cd-deploy.yml) into your fork's `.github/workflows/cd-deploy.yml`, replacing
the existing file. Use your file manager or editor. Commit this setup change. It retains the
application's four reusable checks but sends Render the exact checked commit. It does not add a
workflow to the training repository.

Record the output of the following command as BASELINE_COMMIT in a copy of
[acceptance.md](acceptance.md):

```text
git rev-parse HEAD
```

Every command below containing BASELINE_COMMIT or CANDIDATE_COMMIT requires replacing that word
with the full recorded identifier. Replace YOUR_SERVICE with your assigned Render hostname.

## 2. Build, run, and verify locally

From your application fork:

```text
docker build --label training.revision=BASELINE_COMMIT -t sefop-baseline .
docker run -d --name sefop-baseline -p 8000:8000 sefop-baseline
docker image inspect sefop-baseline
docker logs sefop-baseline
```

The build creates an image; the run creates a container. Confirm the image label contains your
baseline commit. Open `http://localhost:8000/health`, then the application at `http://localhost:8000`.
Wait for startup before collecting results. Running the image does not reinstall dependencies or
include later edits to source files.

Do not pass a SOLVER_NAME environment variable. The baseline web configuration defaults to
`google_scip`; the supplied candidate changes that default to `highs`. An override would mask the
change. The command-line interface has its own settings and is not the interface compared here.

Collect the baseline on your local Docker host:

```text
python ../training-testing-python/src/safe_release/compare.py collect --url http://localhost:8000 --revision BASELINE_COMMIT --solver google_scip --environment local-docker --output ../baseline.json
```

The helper checks health before timing warmed requests. Save reports outside the application fork
so they do not enter the Docker build or a commit. Record the sample hash in your worksheet.

### Know what the sample exercises

| Instance | Known optimal calories | Example optimal selection | Cost / weight | Search-space count |
| --- | --- | --- | --- | --- |
| unique-optimum | 6400 | 64 apples | 64 / 64 | 2145 |
| tied-optimum | 6400 | Any mix of 64 apples and pears | 64 / 64 | 4225 |
| capacity-sensitive | 7900 | 22 apples and 20 pears | 62 / 64 | 1089 |

[instances.json](instances.json) supplies the exact requests. The application uses enumeration
when its calculated search space is at most 1000 combinations, a mixed-integer solver for larger
spaces with at most 50 feasible products, and a heuristic above that product threshold. Each sample
instance has two feasible products and more than 1000 combinations, so it exercises the configured
MIP solver. Smaller examples could appear to validate the solver change while never invoking it.

The unique instance's apple has the highest calories per unit of either capacity. The tied instance
has identical product coefficients. For the capacity-sensitive instance, enumerate the bounded
integer pairs to check the published optimum; 8000 is a relaxation bound, not an attainable integer
answer. Logs should show solver progress; retain enough local output to confirm the solver used.

## 3. Deploy the baseline on Render

1. Push your setup commit to **main in your fork**. If workflows are initially disabled on the fork,
   leave them disabled until the service and secret are configured. If a deployment job fails
   because the secret is missing, it has not deployed anything; configure it and rerun afterward.
2. In Render, create a **Web Service**, connect your fork, and choose branch **main** and language
   **Docker**. Use the root Dockerfile and its supplied startup command. Select the **Free** instance.
3. Set the health-check path to `/health`. The supplied process listens on port 8000; set `PORT` to
   `8000` to make that expectation explicit. Leave SOLVER_NAME absent and use no environment group
   that overrides it. Set **Auto-Deploy to Off** for subsequent releases.
4. Create the service and let the initial deployment finish. Record the deployment identifier and
   commit in the Render dashboard. They must identify your baseline. A requested deployment is not
   yet a completed deployment.
5. Copy the service's deploy hook into your fork's GitHub **Settings → Secrets and variables →
   Actions** as `RENDER_DEPLOY_HOOK_URL`. A deploy hook is a credential: never put it in the worksheet,
   source, screenshots, or reports.
6. Enable GitHub Actions in the fork and rerun the baseline's deployment workflow if necessary.
   Confirm the four prerequisite checks pass. Record the resulting baseline deployment.

Render builds and retains an image from the supplied source. The local, GitHub, and Render builds
are separate artifacts: the Dockerfile's base-image tag can move. Record the deployment identity
and inspect build logs; do not claim that identical source guarantees identical image bytes.

Open the hosted health endpoint and application, then collect a hosted baseline:

```text
python ../training-testing-python/src/safe_release/compare.py collect --url https://YOUR_SERVICE.onrender.com --revision BASELINE_COMMIT --solver google_scip --environment render-training --output ../hosted-baseline.json
```

Allow an idle service to wake up first. If the helper cannot establish health within its startup
wait, open the application, wait until it responds, and rerun. Hosted results verify deployment;
do not compare their timings with local results to assess the solver change.

## 4. Apply and assess the candidate

Complete your expectations in the worksheet **before** collecting the candidate. For this sample,
require valid selections, the same known optimal calories, and each warmed response within
30 seconds. Costs and weights must respect their limits and match the returned quantities. Inspect
differences, but accept alternative optimal selections. A single run is not evidence of a speedup.

Create a feature branch and apply the supplied change:

```text
git switch -c assess-highs
git apply --check ../training-testing-python/src/safe_release/candidate.patch
git apply ../training-testing-python/src/safe_release/candidate.patch
git diff
git add src/startup.py
git commit -m "Assess HiGHS as the default web solver"
git rev-parse HEAD
```

Record that commit as CANDIDATE_COMMIT. The patch changes the web default and its documentation;
it leaves the formulation, input sample, and command-line default unchanged. Rebuild, stop the
baseline container, and run the candidate on the same host and port:

```text
docker build --label training.revision=CANDIDATE_COMMIT -t sefop-candidate .
docker stop sefop-baseline
docker run -d --name sefop-candidate -p 8000:8000 sefop-candidate
docker image inspect sefop-candidate
docker logs sefop-candidate
python ../training-testing-python/src/safe_release/compare.py collect --url http://localhost:8000 --revision CANDIDATE_COMMIT --solver highs --environment local-docker --output ../candidate.json
python ../training-testing-python/src/safe_release/compare.py compare ../baseline.json ../candidate.json
```

Both collections use the same sample file, input hashes, environment label, and request deadline.
The labels are your declarations, not proof of the installed software: confirm them against image
labels, source, configuration, and solver output. Do not edit the sample between collections.

The report recomputes totals from the original inputs, validates quantities and capacities, checks
known calories, and retains per-instance failures. It also reports paired costs, weights, and warmed
request times. Those durations include networking and application work, not just solving. The
client timeout does not cancel computation on the server; no solver time-limit implementation is
added by this exercise.

Investigate unexpected differences before release. A report returning exit status 0 means the
declared decision criteria passed, not that a human approved release. Complete the assessment and
record your accept/reject decision before merging.

### Check that unexpected differences are visible

Copy `candidate.json` to `candidate-broken.json`. Change the unique-optimum quantity from 64 to 63,
and change its reported totals to 6300 calories, 63 cost, and 63 weight. Compare it with the baseline.
The report must say **INVESTIGATE**, show only two valid pairs, and return a nonzero exit status.
Use this copied report only to test the reviewer tool; leave the application and actual report intact.

## 5. Release through the controlled path

Push `assess-highs` to your fork and open a pull request **against your fork's main**, not upstream.
Record the comparison and review decision in its description without secrets. If main has changed
since your baseline, update the feature branch and repeat assessment against the current main
before merging. Check the automated results and merge only after acceptance.

The supplied deployment workflow runs the four existing checks for the merged commit before
calling the hook with `ref` set to that exact commit. A failed prerequisite prevents the hook job
from running. Render's independent Auto-Deploy must remain off. A failing check can be demonstrated
in an unmerged throwaway branch; do not deliberately ship an invalid application.

Record the merge commit as DEPLOYED_CANDIDATE_COMMIT. It can differ from CANDIDATE_COMMIT; confirm
the merged source contains the change you assessed. Avoid concurrent merges during this drill.

Watch Render until deployment succeeds; match its commit with the checks. Check health, confirm
SOLVER_NAME remains absent, and solve the known instance. Collect a hosted candidate using the
deployed commit and compare it with `hosted-baseline.json` using environment `render-training`.
Account for idle wake-up and resource variation; this hosted check establishes usable results, not
a statistically established performance improvement.

## 6. Recover and reconcile

Recovery is a deliberate drill even when the candidate is acceptable:

1. Wait for current deployments to complete. In your fork's Actions page, disable the deployment
   workflow and cancel any queued run so another hook cannot undo the recovery.
2. In Render's Deploys page, choose the successful baseline and **Rollback to this deploy**.
   Verify the retained baseline artifact is available before attempting recovery.
3. Wait for success. Record the recovery deployment and restored commit. Check health and solve
   the same known instance again; collect a recovery report with the restored commit and
   `google_scip` label. Inspect it against the baseline expectations.
4. Reconcile the fork: on main, use `git revert` on the commit that introduced the solver change
   (for a merge commit, Git requires the appropriate mainline parent). Review the diff to ensure
   the web default is restored to `google_scip`, then push while deployment remains disabled.
   Use the GitHub pull request's Revert action if you prefer its guided workflow.
5. Confirm host settings, including absent SOLVER_NAME, agree with the restored source. Reenable
   the GitHub deployment workflow and let checks gate the reconciled release. Keep Render
   Auto-Deploy off: GitHub is still the controlled deployment path.

Render's rollback reuses a retained build artifact and some deployment settings; it does not reverse
executed decisions or restore persistent-disk contents. Environment groups and current service
settings have separate behavior. Review the [rollback documentation](https://render.com/docs/rollbacks)
before relying on recovery in another application.

Stop the local candidate container when finished. Suspend or delete your example Render service if
you no longer need it. Leave the completed worksheet and reports in your own training records.

## Completion evidence

You are finished when the worksheet identifies the baseline, candidate, sample, and deployments;
both local reports contain all three identical inputs; the paired report meets the declared
criteria; the copied degraded report is rejected; the checked candidate is verified on Render;
and baseline recovery is verified with source and configuration reconciled afterward.

## Troubleshooting and references

- **Docker cannot connect:** start the engine and check `docker version`. Do not continue with only
  an installed command-line client.
- **Local port already occupied:** stop your earlier exercise container before starting the next.
- **Solver change appears absent:** check the rebuilt image, SOLVER_NAME overrides, and the sample's
  solver-selection thresholds. Restarting an old image cannot include a new source default.
- **Wrong revision deployed:** confirm Auto-Deploy is off and the supplied checked-commit workflow
  is installed; match the dashboard commit with the automated checks.
- **Rollback unavailable:** free services retain only a small recent history. Perform the drill
  promptly. Rebuilding old source is not the same as restoring its retained artifact.
- [Docker images](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/)
  and [containers](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
  explain the package and execution lifecycle.
- [Docker deployments on Render](https://render.com/docs/docker) explains repository builds.
- [Render deploy hooks](https://render.com/docs/deploy-hooks) explains secrets and commit references.
