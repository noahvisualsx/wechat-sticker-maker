"""Zero-dependency Local Interactive Web Studio Server (`wechat-sticker-maker serve`).

Provides a local HTTP server (default `http://127.0.0.1:7860`) serving:
- Interactive Web Studio UI (`docs/index.html` + `docs/gallery/` + `output/`)
- REST JSON API:
  - `GET  /api/catalog` -> 108 styles, 220 single expressions, 168 duo presets, 40 pet presets, 60 memes, 18 themes
  - `GET  /api/jobs`    -> list generated sticker packs in `output/`
  - `POST /api/remix`   -> zero-token real-time caption/bubble/language remix (`remix_captions`)
  - `POST /api/posters` -> generate Xiaohongshu 3:4 / Story 9:16 static & animated posters + WeChat submission kit
"""

from __future__ import annotations

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import urlparse
import webbrowser

from .duo import DUO_CATEGORY_LABELS, load_duo_presets
from .memes import list_memes
from .pets import PET_CATEGORY_LABELS, load_pet_presets
from .planner import CATEGORY_LABELS, THEME_PACKS, load_all_presets
from .studio import (
    generate_animated_social_poster,
    generate_social_posters,
    generate_wechat_submission_kit,
    remix_captions,
)
from .styles import list_style_presets


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def build_catalog_payload() -> Dict[str, Any]:
    """Return full studio catalog metadata and counts."""
    styles = list_style_presets()
    expressions = load_all_presets()
    duos = load_duo_presets()
    pets = load_pet_presets()
    memes = list_memes()
    return {
        "counts": {
            "styles": len(styles),
            "expressions": len(expressions),
            "expression_categories": len(CATEGORY_LABELS),
            "duos": len(duos),
            "duo_categories": len(DUO_CATEGORY_LABELS),
            "pets": len(pets),
            "pet_categories": len(PET_CATEGORY_LABELS),
            "memes": len(memes),
            "themes": len(THEME_PACKS),
        },
        "themes": THEME_PACKS,
        "expression_categories": CATEGORY_LABELS,
        "duo_categories": DUO_CATEGORY_LABELS,
        "pet_categories": PET_CATEGORY_LABELS,
    }


def list_local_jobs(base_dir: Path | None = None) -> Dict[str, Any]:
    """Scan `output/` for generated sticker jobs (`job.json` / `manifest.json`)."""
    root = base_dir or (_repo_root() / "output")
    jobs = []
    if root.exists():
        for d in sorted(root.iterdir()):
            if not d.is_dir():
                continue
            job_p = d / "job.json"
            man_p = d / "manifest.json"
            if job_p.exists() or man_p.exists():
                info: Dict[str, Any] = {"dir": str(d), "name": d.name}
                if job_p.exists():
                    try:
                        info["job"] = json.loads(job_p.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                if man_p.exists():
                    try:
                        m = json.loads(man_p.read_text(encoding="utf-8"))
                        info["generated_count"] = m.get("generated_count", {})
                        info["language"] = m.get("language")
                    except Exception:
                        pass
                jobs.append(info)
    return {"jobs": jobs}


def handle_api_request(
    method: str,
    path: str,
    body: Dict[str, Any] | None = None,
    base_dir: Path | None = None,
) -> Tuple[int, Dict[str, Any]]:
    """Pure function router for Studio REST endpoints (easy to unit test)."""
    parsed = urlparse(path).path.rstrip("/")
    body = body or {}

    if method == "GET" and parsed == "/api/catalog":
        return int(HTTPStatus.OK), build_catalog_payload()

    if method == "GET" and parsed == "/api/jobs":
        return int(HTTPStatus.OK), list_local_jobs(base_dir)

    if method == "POST" and parsed == "/api/remix":
        job_file = body.get("job_path")
        if not job_file:
            return int(HTTPStatus.BAD_REQUEST), {"error": "Missing required field: job_path"}
        jp = Path(job_file)
        if not jp.exists():
            return int(HTTPStatus.NOT_FOUND), {"error": f"job.json not found: {jp}"}
        preview = remix_captions(
            jp,
            caption_overrides=body.get("caption_overrides"),
            bubble_overrides=body.get("bubble_overrides"),
            language=body.get("language"),
        )
        return int(HTTPStatus.OK), {"status": "ok", "preview_html": str(preview)}

    if method == "POST" and parsed == "/api/posters":
        out_str = body.get("output_dir")
        if not out_str:
            return int(HTTPStatus.BAD_REQUEST), {"error": "Missing required field: output_dir"}
        out_p = Path(out_str)
        if not out_p.exists():
            return int(HTTPStatus.NOT_FOUND), {"error": f"Output directory not found: {out_p}"}
        style = body.get("style", "real-cutout")
        lang = body.get("language", "zh-CN")
        title = body.get("title")
        subtitle = body.get("subtitle")

        res: Dict[str, str] = {}
        for k, v in generate_social_posters(out_p, title=title, subtitle=subtitle, style=style, language=lang).items():
            res[k] = str(v)
        if body.get("animated", True):
            for k, v in generate_animated_social_poster(
                out_p, title=title, subtitle=subtitle, style=style, language=lang
            ).items():
                res[k] = str(v)
        if body.get("wechat_kit", True):
            for k, v in generate_wechat_submission_kit(
                out_p, title=title, subtitle=subtitle, style=style, language=lang
            ).items():
                res[f"wechat_{k}"] = str(v)
        return int(HTTPStatus.OK), {"status": "ok", "generated": res}

    return int(HTTPStatus.NOT_FOUND), {"error": f"Unknown endpoint: {method} {parsed}"}


class StudioRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler serving `docs/` at `/` plus `/api/*` JSON endpoints."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(_repo_root() / "docs"), **kwargs)

    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/api/"):
            status, payload = handle_api_request("GET", self.path)
            self._send_json(status, payload)
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.startswith("/api/"):
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                body = json.loads(raw_body) if raw_body.strip() else {}
            except Exception as e:
                self._send_json(int(HTTPStatus.BAD_REQUEST), {"error": f"Invalid JSON: {e}"})
                return
            try:
                status, payload = handle_api_request("POST", self.path, body=body)
            except Exception as e:
                status, payload = int(HTTPStatus.INTERNAL_SERVER_ERROR), {"error": str(e)}
            self._send_json(status, payload)
            return
        self.send_error(int(HTTPStatus.METHOD_NOT_ALLOWED))


def run_studio_server(host: str = "127.0.0.1", port: int = 7860, open_browser: bool = False) -> None:
    """Launch the local interactive Web Studio server."""
    url = f"http://{host}:{port}"
    print(f"=== WeChat Sticker Maker · Local Web Studio ===")
    print(f"  Studio URL:   {url}")
    print(f"  Catalog API:  {url}/api/catalog")
    print(f"  Jobs API:     {url}/api/jobs")
    print("Press Ctrl+C to stop.")
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    with ThreadingHTTPServer((host, port), StudioRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Studio server.")
