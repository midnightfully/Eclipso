# Revival development agreement

kindmops owns the repository and release decisions. The intended developers are Codex and Claude Opus 5.5. Keep changes reviewable on separate branches; use a pull request and recorded test results. Do not add other collaborators or trigger paid automation without the owner's instruction.

The baseline is the supplied 2017 Roblox signup reference. Preserve the Roblox system identity at user ID 1 and its exact biography in docs/roblox-profile.json. Human administrative access belongs to a separate account. Currency and accounts belong to this revival.

Read START-HERE.md, TEST-REPORT.md and docs/BUILD-PLAN-2017.md before changing services. The code is currently a Windows local development environment, not a production deployment. .NET 10 backend: Roblox/Roblox.Website; Next frontend: 2016-roblox-main; admin UI: admin; operational tools: local; private data: .local.

Never commit .local, runtime configuration, account credentials, signing keys, database contents or uploaded user data. Example config must contain no shared secret. Preserve upstream license and attribution. Do not upload the entire working folder blindly.

Tests involving balances, limiteds, roles and permissions must verify database outcomes and rejection paths. Record API tests separately from browser tests. Do not call a workflow complete because its UI exists. Do not replace failures with invented values or successful-looking responses.

Keep the local service bound to loopback. Public release requires resolving the upstream RCE report and dependency advisories, explicit production configuration, removal of development grants, and deployment/restore tests. Do not weaken checks to get a green build. Development and production service flags must be separate from client/server enablement.

Build: local/build-backend.cmd. Runtime: Start Website.cmd and Stop Website.cmd. Account integration tests: python local/test-signup-2017.py. Read test scripts before running; they create synthetic data. Additional test evidence is documented in TEST-REPORT.md.

Use codex/<task> and claude/<task> branches. Avoid simultaneous edits to the same files. Reviews should cover behavior, tests, migrations, deployment impact and remaining limitations. Never merge a change to production solely because another model said it works.
