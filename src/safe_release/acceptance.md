# Release assessment record

Complete expectations before collecting results. This worksheet is review evidence, not an
automated permission to release. Keep hook URLs and other secrets out of the record.

## Experiment identity

- Baseline application commit:
- Candidate application commit:
- Training-material commit:
- Sample SHA-256 (from both reports):
- Comparable environment label, hardware, and Docker version:
- Baseline and candidate solver library versions:
- SOLVER_NAME override absent locally and on Render:
- Observed selected providers in local logs:
- Both report deadlines: 30 seconds per warmed request:

## Expectations declared before running

- Intended change: the default web MIP provider changes from SCIP to HiGHS.
- Validity: all returned quantities are whole, all products come from the input, both capacities
  hold, and reported attributes and totals match the inputs.
- Quality: each instance retains its published optimal calories: 6400, 6400, and 7900 respectively.
- Ties: selected products may differ; identical product selections are not required.
- Cost and weight: retain capacity compliance; inspect any differences in the paired report.
- Deadline: every warmed request completes within 30 seconds. This is a training acceptance
  threshold, not a production solver time limit. A client timeout does not stop server computation.
- Timing differences: investigate unexpected variation; make no speedup claim from one sample run.

## Assessment before merge

- Report files and paired comparison:
- Valid pairs / total pairs:
- Unexpected differences and investigation:
- Decision: accept / reject / more evidence required:
- Reviewer and reason:
- Date:

## Deployment and recovery

- Baseline Render deployment identifier and commit:
- Candidate automated-check results and checked commit:
- Candidate Render deployment identifier and commit:
- Candidate health and known-instance verification:
- Recovery target and restored deployment identifier:
- Restored health and known-instance verification:
- GitHub deployment workflow disabled while recovering:
- Source and configuration reconciled before resuming releases:
- Remaining uncertainties:
