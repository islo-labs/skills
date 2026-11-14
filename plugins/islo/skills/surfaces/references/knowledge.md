# Knowledge surfaces

Use knowledge for a stored report or media item in the run canvas. Markdown can embed other knowledge media. HTML is an alternative when the document needs its own layout, styles, or scripts.

Inspect `islo surface knowledge --help`, `islo knowledge create --help`, and `islo knowledge update --help` before use. If the CLI lacks `html` or `--discoverable`, update it before following the corresponding examples.

## Publish a Markdown document

Write the report to `report.md`, then create and open it from the stage sandbox:

```bash
islo knowledge create design-report --type memory --body @report.md
islo surface knowledge design-report --label "Design report"
```

These commands use the current `ISLO_FACTORY`. Outside that context, pass `--factory FACTORY_KEY` to knowledge commands. Opening a Surface requires the stage agent's line-run Surface environment.

To revise the open document, update the same slug:

```bash
islo knowledge update design-report --body @report.md
```

The canvas follows the latest version. Check that the report renders, then update it and confirm that the open Surface shows the new content. Use `islo surface ls` to inspect published surfaces.

## Place images, video, and audio in Markdown

Upload the media as knowledge items in the same Factory as the document. For images used only as part of a Markdown file, use `--discoverable false`:

```bash
islo knowledge create report-diagram --type image --file diagram.png --discoverable false
islo knowledge create report-demo --type video --file demo.mp4 --discoverable false
islo knowledge create report-narration --type audio --file narration.mp3 --discoverable false
```

This keeps supporting media out of lists and search while allowing access by identifier and rendering inside the document. It is not an access-control setting. The same setting is useful for supporting video and audio. To hide an existing supporting image from discovery:

```bash
islo knowledge update report-diagram --discoverable false
```

Put these embeds in `report.md`. Replace `FACTORY_KEY` with the current Factory's key:

```markdown
![Architecture diagram](https://app.islo.dev/factories/FACTORY_KEY/knowledge/report-diagram/content)

![Demo movie](https://app.islo.dev/factories/FACTORY_KEY/knowledge/report-demo/content)

![Audio narration](https://app.islo.dev/factories/FACTORY_KEY/knowledge/report-narration/content)
```

Use Markdown image syntax for all three media types. Islo resolves the knowledge content and renders an image, a video player, or an audio player based on its media type. Place each embed in its own paragraph. Reference the content route, not a sandbox file path or a temporary download URL. Keep the document and media in the same Factory because references to another Factory render as links rather than inline media.

Without a version, the reference resolves the latest content when loaded. To keep a report tied to a particular media version, include the version number in the content path:

```markdown
![Architecture diagram, version 2](https://app.islo.dev/factories/FACTORY_KEY/knowledge/report-diagram/versions/2/content)
```

After publishing, check that images load and video and audio have usable playback controls.

## Publish self-contained HTML instead

Create an HTML knowledge item with `--type html --file report.html`. HTML renders in a sandboxed iframe with an opaque origin. It cannot reference other media knowledge items or rely on authenticated Islo requests. Markdown knowledge embeds are not interpreted inside HTML.

Keep the whole document self-contained. Inline styles and scripts, and put every image's bytes in a data URL such as `<img src="data:image/png;base64,..." alt="Diagram">`. Use the actual `src` attribute, not `data-src`. For video and audio, use `src="data:video/mp4;base64,..."` and `src="data:audio/mpeg;base64,..."` with `controls`. Match the MIME type to the file. Do not reference relative asset files, external assets, or knowledge content URLs from HTML.

For example, generate a complete HTML file with a local PNG embedded:

```bash
python3 - <<'PY'
import base64
from pathlib import Path

image = base64.b64encode(Path("diagram.png").read_bytes()).decode("ascii")
Path("report.html").write_text(
	'<!doctype html><html lang="en"><head><meta charset="utf-8">'
	'<meta name="viewport" content="width=device-width, initial-scale=1">'
	'<title>Design report</title><style>body{font-family:sans-serif}'
	'img{max-width:100%}</style></head><body><h1>Design report</h1>'
	f'<img src="data:image/png;base64,{image}" alt="Architecture diagram">'
	'</body></html>',
	encoding="utf-8",
)
PY
islo knowledge create design-report-html --type html --file report.html
islo surface knowledge design-report-html --label "HTML design report"
```

To revise it, regenerate the self-contained file and run `islo knowledge update design-report-html --file report.html`. Confirm that the open Surface renders the layout and embedded media after the update.
