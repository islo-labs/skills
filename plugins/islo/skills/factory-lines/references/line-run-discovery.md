# Find related Line runs within a bounded search

Use the selected Factory for every read. Without an explicit Factory, tenant-wide discovery returns only authorized active Factories. Use the owning row's `factory_id` for status reads and actions. Never fan out over Factories or infer the owner from recency.

Use a known run ID or direct Islo run link for a scoped `line-run status RUN_ID`
read before any list search, regardless of age. Use the link's owning Factory.
Known JobRun IDs use their direct JobRun read; resolve a LineRun only through
an authoritative parent relation. Never treat a JobRun ID as a LineRun ID.

For discovery, make at most three targeted page requests per task, including continuation.
Use a specific `--line` when known and distinctive `--q` terms from the request.
For example:
```bash
islo factory line-run list --line feature-delivery --q ISL-2416 --q "shared initialization" --paged --limit 20 --sort -created_at -o json
```
Each `--q` is one case-insensitive substring; repeated values require every
phrase. Search covers names, run IDs, selected trigger fields, and artifact
titles and identifiers. It does not search arbitrary run params or artifact URLs
or repository fields. Use only terms likely to occur in the searchable fields.
Keep failed and stopped runs in scope. Reuse results within the task.

Only when another targeted page can resolve the request, pass the returned
opaque cursor as `--cursor CURSOR --limit 20`, retaining the
same Factory, --line, --q terms, and --sort. Continuation consumes the same
three-request budget. Stop on a match, a null cursor, or the budget limit.
Do not scan the entire history or follow every cursor by default.

If targeted searches find no verified match, use at most one recent fallback:
```bash
islo factory line-run list --paged --limit 100 --sort -created_at -o json
```
Retain the selected Factory and any known `--line` on this fallback.
Inspect its returned params, origins, and artifacts. Do not continue the fallback page.
A substring match is only a candidate. Verify exact artifact identity first,
then run params, using scoped status and stage reads as needed. For GitHub,
verify owner/repo and number together. List artifacts can be truncated; a
missing summary artifact is not proof of absence. Topic, recency, or Line
name alone never proves ownership or authorizes an action.

A bounded miss is not proof that no historical run exists. If ownership or a
prior start outcome remains uncertain, report the lookup incomplete and request
an exact run link or identifier rather than starting a replacement. Apply this
same bounded lookup after a lost start response; never restart uncertain work.

Paged JSON is `{items, cursor, total?}`. Omit exact counts during discovery.
If a count is explicitly needed, use `--total` on the first page only, never
with a continuation cursor. It is a point-in-time count. Supported sort fields
are `created_at`, `started_at`, `completed_at`, `stopped_at`, and `asked_at`;
prefix `-` for descending. The default is `-created_at`.
Legacy offset flags and JSON arrays remain supported for older callers;
new discovery uses native pages. Check CLI help or schema before lookup.
If the installed CLI lacks these flags, report the missing capability instead
of falling back to an exhaustive scan.
