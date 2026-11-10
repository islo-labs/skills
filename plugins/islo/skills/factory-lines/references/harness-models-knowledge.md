# Agent harnesses, models, and Knowledge

Prompt Agents own `harness`, `model`, `model_provider`, `effort`, `skills`, and `mcp`. Script and Decision Agents have different fields. Confirm supported combinations with `islo schema agent --short`; confirm optional stage overrides with `islo schema factory --short`.

## Pair harness and provider

The harness determines the model protocol. The installed Agent schema exposes these provider combinations:

| Harness | Provider choices | Model discovery |
|---|---|---|
| `codex` | `islo`, `islo_inference`, `subscription` | Native provider ids or the Islo catalog with the matching Responses protocol |
| `claude` | `islo_inference`, `subscription`; omit for default routing | Anthropic ids or Islo catalog ids with `anthropic_messages` |
| `grok` | `islo`, `subscription` | Models supported by the connected Grok provider and harness |
| `cursor` | Omit `model_provider` | `agent --list-models` in an authenticated Machine-backed sandbox |
| `opencode` | Omit `model_provider` | Islo's OpenAI-compatible catalog, using aliases where required by the adapter |

Discover the live Islo catalog:

```bash
islo api /inference/models
```

Check each model's `client_apis`, supported effort, and provider connection before choosing it. Cursor's catalog is separate. A model name alone does not establish protocol support. Do not assume that a personal provider connection is available to tenant-context automation; check the intended execution identity and provider status locally.

For Codex, omitting `model_provider` uses default OpenAI routing. Set `islo_inference` for an Islo catalog id. This fragment illustrates only provider selection:

```toml
model_provider = "islo_inference"
```

For Claude with Islo inference, choose a model advertising `anthropic_messages`. Subscription routing requires a member deployer for the Line version, including when selected through a stage param. API-key deployment cannot supply a member subscription identity. Confirm current requirements in the live Factory schema before deployment.

OpenCode uses the injected OpenAI-compatible configuration. Use a supported catalog id or alias. Do not add provider credentials to the Agent TOML or sandbox environment. Provider URLs and gateway rules are in the platform gateway reference.

## Keep settings in their owner

Reusable prompts and execution settings belong in Agents. Optional Prompt Agent stage overrides belong in the Line. Fixed overrides and supported whole-param templates are described by `islo schema factory --short`; do not template fields unless the schema supports them. A param-selected Machine must be published in the selected Factory. Shared-workspace stages must resolve to the same Machine.

Skills carry repository procedures. MCP declarations carry server keys and URLs, while the Machine gateway profile controls allowed hosts and authentication. See [agent-manifest.md](agent-manifest.md).

## Knowledge and Manager instructions

Knowledge contains declarative conventions, policies, and rules. Procedural playbooks belong in repository Skills. Reusable Agent configuration does not expose a Knowledge binding field; do not invent one. Use supported tools to read required Knowledge or put a concise policy in the Agent prompt.

The built-in Manager's `[agent.instructions]` can bind a literal or Knowledge item when `[manager]` is absent. A custom Prompt Agent Manager instead uses its Agent prompt, optionally replaced by `manager.prompt` for one Line. Agentic transition instructions apply to individual routing decisions. Knowledge discovery and CRUD are in the platform skill.
