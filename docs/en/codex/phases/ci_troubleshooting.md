# CI Troubleshooting

- Ensure **Settings → Actions → General → Workflow permissions** = *Read and write permissions*.
- You can manually run CI via **Actions → CI → Run workflow** (enabled by `workflow_dispatch`).
- If the button doesn't appear, push an empty commit: `git commit --allow-empty -m "ci: trigger" && git push`.
- Local simulation: `bash scripts/verify_ci_local.sh`.
