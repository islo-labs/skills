# Use connected providers

Check the provider with the [connection status check](../SKILL.md#check-connection-status) before calling it. Islo sandboxes have gateway-managed credentials injected as environment variables. Phantom tokens are exchanged for real credentials on allowed outbound requests.

Never look for credentials on disk, including `~/.config/`, CLI token files, or provider configuration directories. Never run login flows such as `gh auth login`. Use the injected credentials directly and keep token values out of logs and files.

## GitHub

The `gh` CLI is pre-authenticated when GitHub is connected. Use it directly:

```bash
gh pr view 123 --repo owner/repo
gh api repos/owner/repo/pulls/123/comments
```

For authorized comments or reviews, follow the agent's GitHub identity and signing instructions:

```bash
gh pr comment 123 --repo owner/repo --body-file /tmp/pr-comment.md
gh pr review 123 --repo owner/repo --approve --body-file /tmp/pr-review.md
```

## Linear

Use `$LINEAR_API_KEY` with GraphQL at `https://api.linear.app/graphql`. There is no `linear` CLI. Always build request variables with `jq`; never interpolate comment text into a shell `-d` string. Do not use `issueSearch` or `IssueFilter.identifier`.

`issue(id:)` accepts an identifier or UUID:

```bash
ISSUE_KEY="ISL-123"
jq -n --arg id "$ISSUE_KEY" '{query:"query($id:String!){ issue(id:$id){ id identifier title description url state { name } comments { nodes { body user { name } } } } }",variables:{id:$id}}' | curl -s https://api.linear.app/graphql -H "Content-Type: application/json" -H "Authorization: Bearer $LINEAR_API_KEY" --data @- | jq .
```

For an authorized comment, fetch the issue first. `commentCreate.issueId` requires the UUID from `.data.issue.id`:

```bash
ISSUE_UUID="<uuid from fetch>"
jq -n --arg id "$ISSUE_UUID" --arg body "Your comment here." '{query:"mutation($id:String!,$body:String!){ commentCreate(input:{issueId:$id,body:$body}){ success } }",variables:{id:$id,body:$body}}' | curl -s https://api.linear.app/graphql -H "Content-Type: application/json" -H "Authorization: Bearer $LINEAR_API_KEY" --data @- | jq .
```

For a multi-paragraph comment, write the Markdown to a file and use `--rawfile body /tmp/linear-comment.md` instead of `--arg body`.

## Other providers

To find available environment variable names without printing their values:

```bash
compgen -e | grep -iE '(api_key|token|secret)' | grep -v '^_'
```

Use the appropriate variable in the provider's HTTP client or SDK. Variable presence is not connection evidence; use the [status check](../SKILL.md#check-connection-status). Gateway host allow rules and authentication profiles are covered in [gateway-integrations.md](../../platform/references/gateway-integrations.md).
