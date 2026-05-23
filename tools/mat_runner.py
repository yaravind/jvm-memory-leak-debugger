"""
mat_runner.py
=============
Tool 2 – Download Eclipse MAT if needed, run headless heap-dump analysis on
an .hprof file, and return structured findings from the generated HTML reports.

Steps performed:
  1. Locate Java 17+ on the host (required by MAT 1.16+).
  2. If MAT is not already installed at MAT_HOME, download and unpack it.
  3. Run ParseHeapDump with:
       org.eclipse.mat.api:suspects
       org.eclipse.mat.api:top_components
  4. Locate the generated *_Leak_Suspects.zip beside the hprof file.
  5. Parse the HTML report pages → extract suspects, histogram, stack traces,
     dominator paths.
  6. Return a structured dict.

MAT version and URLs are pinned; bump MAT_VERSION / SHA256 to update.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Any

# ---------------------------------------------------------------------------
# MAT distribution constants  (aarch64 macOS)
# ---------------------------------------------------------------------------

MAT_VERSION = "1.16.1.20250109"
MAT_VERSION_SHORT = "1.16.1"
MAT_URL_TEMPLATE = (
    "https://download.eclipse.org/mat/{short}/rcp/"
    "MemoryAnalyzer-{full}-macosx.cocoa.{arch}.dmg"
)
MAT_SHA256 = {
    "aarch64": "01ac5effe6479f013c32c2f8d75ed08e7ec0f848f5ce301b5fa47de7f34c2654",
    "x86_64":  "9cd8ad2e726da6e1300bdb115cc22c929e69707de56cc2873cac5067848254ea",
}

DEFAULT_MAT_HOME = Path("/private/tmp/mat/MemoryAnalyzer.app")
EQUINOX_JAR_GLOB = "org.eclipse.equinox.launcher_*.jar"
JAVA17_KNOWN = Path("/Library/Java/JavaVirtualMachines/microsoft-17.jdk/Contents/Home")


# ---------------------------------------------------------------------------
# Java 17 discovery
# ---------------------------------------------------------------------------

def _find_java17() -> Path:
    """Return path to a Java 17+ JAVA_HOME or raise EnvironmentError."""
    # 1. Explicit env var
    if "JAVA17_HOME" in os.environ:
        return Path(os.environ["JAVA17_HOME"])
    # 2. Known macOS location (Microsoft JDK 17)
    if JAVA17_KNOWN.exists():
        return JAVA17_KNOWN
    # 3. /usr/libexec/java_home -v 17
    try:
        result = subprocess.run(
            ["/usr/libexec/java_home", "-v", "17"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            p = Path(result.stdout.strip())
            if p.exists():
                return p
    except Exception:
        pass
    # 4. JAVA_HOME env
    if "JAVA_HOME" in os.environ:
        p = Path(os.environ["JAVA_HOME"])
        if p.exists():
            out = subprocess.run(
                [str(p / "bin" / "java"), "-version"],
                capture_output=True, text=True
            ).stderr
            if re.search(r"version \"1[7-9]|version \"[2-9][0-9]", out):
                return p
    raise EnvironmentError(
        "Java 17+ is required to run Eclipse MAT 1.16.\n"
        "Set JAVA17_HOME to your JDK 17+ home directory, or install it."
    )


# ---------------------------------------------------------------------------
# MAT installation
# ---------------------------------------------------------------------------

def _arch() -> str:
    import platform
    machine = platform.machine().lower()
    return "aarch64" if machine in ("arm64", "aarch64") else "x86_64"


def _verify_sha256(path: Path, expected: str) -> bool:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest() == expected


def _download_mat(mat_home: Path) -> None:
    """Download MAT DMG, verify checksum, mount & copy into mat_home."""
    arch = _arch()
    url = MAT_URL_TEMPLATE.format(
        short=MAT_VERSION_SHORT, full=MAT_VERSION, arch=arch
    )
    expected_sha = MAT_SHA256[arch]

    print(f"[mat_runner] Downloading Eclipse MAT {MAT_VERSION} for {arch}…")
    print(f"[mat_runner]   {url}")

    with tempfile.TemporaryDirectory() as td:
        dmg = Path(td) / "MemoryAnalyzer.dmg"
        subprocess.run(
            ["curl", "-L", "-o", str(dmg), url],
            check=True
        )
        if not _verify_sha256(dmg, expected_sha):
            raise RuntimeError(
                f"SHA-256 mismatch for downloaded MAT DMG.\n"
                f"Expected: {expected_sha}\n"
                f"Got:      {hashlib.sha256(dmg.read_bytes()).hexdigest()}"
            )
        mount_pt = Path(td) / "mnt"
        mount_pt.mkdir()
        subprocess.run(
            ["hdiutil", "attach", str(dmg), "-mountpoint", str(mount_pt),
             "-nobrowse", "-quiet"],
            check=True
        )
        try:
            src = mount_pt / "MemoryAnalyzer.app"
            mat_home.parent.mkdir(parents=True, exist_ok=True)
            if mat_home.exists():
                shutil.rmtree(mat_home)
            shutil.copytree(src, mat_home)
        finally:
            subprocess.run(
                ["hdiutil", "detach", str(mount_pt), "-quiet"],
                check=False
            )
    print(f"[mat_runner] MAT installed at: {mat_home}")


def ensure_mat(mat_home: Path = DEFAULT_MAT_HOME) -> Path:
    """Return the Eclipse dir inside MAT, downloading if absent."""
    eclipse_dir = mat_home / "Contents" / "Eclipse"
    if not eclipse_dir.exists():
        _download_mat(mat_home)
    return eclipse_dir


def _equinox_jar(eclipse_dir: Path) -> Path:
    matches = list((eclipse_dir / "plugins").glob(EQUINOX_JAR_GLOB))
    if not matches:
        raise FileNotFoundError(
            f"Equinox launcher jar not found under {eclipse_dir}/plugins"
        )
    return sorted(matches)[-1]


# ---------------------------------------------------------------------------
# MAT headless run
# ---------------------------------------------------------------------------

def run_mat(
    hprof_path: str,
    mat_home: Path = DEFAULT_MAT_HOME,
    mat_heap_gb: int = 12,
    timeout_s: int = 7200,
) -> Path:
    """
    Run MAT headless analysis on hprof_path.

    Returns the path to the generated *_Leak_Suspects.zip beside the hprof.
    Raises RuntimeError if analysis fails or times out.
    """
    hprof = Path(hprof_path).resolve()
    if not hprof.exists():
        raise FileNotFoundError(f"hprof not found: {hprof}")

    eclipse_dir = ensure_mat(mat_home)
    java_home = _find_java17()
    java_bin = java_home / "bin" / "java"
    equinox = _equinox_jar(eclipse_dir)

    # Check if already analysed (index files present)
    idx = hprof.with_suffix(".index")
    suspects_zip = hprof.parent / (hprof.stem + "_Leak_Suspects.zip")

    if suspects_zip.exists() and idx.exists():
        print(f"[mat_runner] Found existing suspects report: {suspects_zip}")
        return suspects_zip

    workspace = Path(tempfile.mkdtemp(prefix="mat-workspace-"))
    cmd = [
        str(java_bin),
        f"-Xmx{mat_heap_gb}g",
        "-jar", str(equinox),
        "-consolelog", "-nosplash",
        "-application", "org.eclipse.mat.api.parse",
        "-data", str(workspace),
        str(hprof),
        "org.eclipse.mat.api:suspects",
        "org.eclipse.mat.api:top_components",
    ]

    print(f"[mat_runner] Starting MAT analysis (this may take 10-30 min for large dumps)…")
    print(f"[mat_runner]   java: {java_bin}")
    print(f"[mat_runner]   hprof: {hprof}")
    print(f"[mat_runner]   workspace: {workspace}")

    start = time.time()
    proc = subprocess.Popen(
        cmd,
        cwd=str(eclipse_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    log_lines = []
    while True:
        line = proc.stdout.readline()
        if line:
            log_lines.append(line.rstrip())
        elif proc.poll() is not None:
            break
        if time.time() - start > timeout_s:
            proc.terminate()
            raise TimeoutError(
                f"MAT analysis exceeded {timeout_s}s timeout. "
                f"Consider increasing mat_heap_gb or timeout_s."
            )

    elapsed = round(time.time() - start, 1)
    rc = proc.wait()
    print(f"[mat_runner] MAT finished in {elapsed}s (exit={rc})")

    if not suspects_zip.exists():
        shutil.rmtree(workspace, ignore_errors=True)
        raise RuntimeError(
            f"MAT did not produce {suspects_zip}.\n"
            f"Last log lines:\n" + "\n".join(log_lines[-40:])
        )

    shutil.rmtree(workspace, ignore_errors=True)
    return suspects_zip


# ---------------------------------------------------------------------------
# HTML report parser
# ---------------------------------------------------------------------------

class _TextExtract(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip = False
        self.texts: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            s = data.strip()
            if s:
                self.texts.append(s)


def _extract_text(html: str) -> List[str]:
    parser = _TextExtract()
    parser.feed(html)
    return parser.texts


# ---------------------------------------------------------------------------
# Findings extractor
# ---------------------------------------------------------------------------

def _parse_leak_suspects(suspects_zip: Path) -> Dict[str, Any]:
    """
    Unzip and parse the MAT Leak Suspects report.

    Returns a dict with:
      suspects     – list of problem-suspect dicts (description, accumulation_point,
                     dominator_path, object_graph_classes, stack_frames)
      histogram    – top classes by retained heap
      raw_text     – full extracted text per HTML page (for LLM or further analysis)
    """
    with tempfile.TemporaryDirectory() as td:
        extract_dir = Path(td)
        with zipfile.ZipFile(suspects_zip) as zf:
            zf.extractall(extract_dir)

        pages_dir = extract_dir / "pages"
        if not pages_dir.exists():
            # flat layout
            pages_dir = extract_dir

        page_texts: Dict[str, List[str]] = {}
        for p in sorted(pages_dir.glob("*.html")):
            html = p.read_text(errors="ignore")
            page_texts[p.name] = _extract_text(html)

        # Also parse index.html / toc.html
        for extra in ["index.html", "toc.html"]:
            ep = extract_dir / extra
            if ep.exists():
                page_texts[extra] = _extract_text(ep.read_text(errors="ignore"))

        return _structure_findings(page_texts)


# ---------------------------------------------------------------------------
# Structured findings builder
# ---------------------------------------------------------------------------

_RE_SUSPECT_HEADER = re.compile(
    r"Problem Suspect (\d+)"
)
_RE_BYTES = re.compile(
    r"([\d,]+)\s*\(([0-9.]+)%\)\s*bytes"
)
_RE_CLASS_ENTRY = re.compile(
    r"^([\w.$\[\]<>]+(?:\[\])?)\s+([\d,]+)\s+([\d,]+)"
)
_RE_STACK_FRAME = re.compile(
    r"at ([\w.$]+\.\w+)\("
)
_RE_RETAINED = re.compile(
    r"([\d,]+)\s*\(([\d.]+)%\)\s*bytes?"
)


def _parse_bytes(s: str) -> int:
    s = s.replace(",", "").strip()
    try:
        return int(s)
    except ValueError:
        return 0


def _structure_findings(page_texts: Dict[str, List[str]]) -> Dict[str, Any]:
    suspects: List[Dict[str, Any]] = []
    histogram: List[Dict[str, Any]] = []
    all_raw: Dict[str, str] = {}

    for page_name, texts in page_texts.items():
        joined = "\n".join(texts)
        all_raw[page_name] = joined

        # ---- Histogram page ----
        if "Class_Histogram" in page_name or "Class Histogram" in joined[:200]:
            hist_entries = []
            in_table = False
            for line in texts:
                if "Class Name" in line and "Objects" in line:
                    in_table = True
                    continue
                if in_table:
                    # e.g. "scala.collection.immutable.HashMap$HashMap1\n..."
                    parts = line.split()
                    if len(parts) >= 3:
                        # try parse: ClassName  num_objects  shallow  retained
                        # MAT text may span multiple lines; pick lines with numbers
                        nums = [p.replace(",", "") for p in parts if re.match(r"[\d,]+$", p)]
                        if nums:
                            hist_entries.append({
                                "class": parts[0],
                                "objects": _parse_bytes(nums[0]) if len(nums) > 0 else 0,
                                "shallow_bytes": _parse_bytes(nums[1]) if len(nums) > 1 else 0,
                                "retained_bytes": _parse_bytes(nums[2]) if len(nums) > 2 else 0,
                            })
            if hist_entries:
                histogram = hist_entries[:30]

        # ---- Suspect pages ----
        if re.search(r"Problem Suspect \d+", joined):
            current: Optional[Dict[str, Any]] = None
            stack_frames: List[str] = []
            dominator_path: List[str] = []
            graph_classes: List[str] = []
            accumulation_point = ""
            description_lines: List[str] = []
            in_desc = False
            in_stack = False
            in_dom = False
            in_graph = False

            for line in texts:
                sm = _RE_SUSPECT_HEADER.match(line)
                if sm:
                    if current is not None:
                        current["stack_frames"] = stack_frames
                        current["dominator_path"] = dominator_path
                        current["object_graph_classes"] = graph_classes
                        suspects.append(current)
                    current = {
                        "suspect_number": int(sm.group(1)),
                        "description": "",
                        "accumulation_point": "",
                        "retained_bytes": 0,
                        "retained_pct": 0.0,
                        "stack_frames": [],
                        "dominator_path": [],
                        "object_graph_classes": [],
                    }
                    stack_frames = []
                    dominator_path = []
                    graph_classes = []
                    description_lines = []
                    in_desc = True
                    in_stack = False
                    in_dom = False
                    in_graph = False
                    continue

                if current is None:
                    continue

                if "The memory is accumulated" in line or "keeps local variables" in line:
                    in_desc = True
                    description_lines.append(line)
                    rb = _RE_RETAINED.search(line)
                    if rb:
                        current["retained_bytes"] = _parse_bytes(rb.group(1))
                        current["retained_pct"] = float(rb.group(2))
                    continue

                if "Shortest Paths" in line or "Accumulated Objects in" in line:
                    in_dom = True
                    in_stack = False
                    in_graph = False

                if "All Accumulated Objects by Class" in line:
                    in_graph = True
                    in_dom = False
                    in_stack = False

                if "Thread Stack" in line or "stacktrace" in line.lower():
                    in_stack = True
                    in_dom = False

                if in_desc and line.startswith("com.") or line.startswith("java.") or line.startswith("scala."):
                    if "readResultSet" in line or "retains" in line or "occupies" in line:
                        accumulation_point = line
                        current["accumulation_point"] = accumulation_point
                        in_desc = False

                if in_stack and "at " in line:
                    sf = _RE_STACK_FRAME.search(line)
                    if sf:
                        stack_frames.append(line.strip())

                if in_dom and line.strip() and not line.startswith("\\") and not line.startswith("."):
                    if re.search(r"@\s*0x", line) or re.search(r"\d+,\d+", line):
                        dominator_path.append(line.strip())

                if in_graph:
                    parts = line.strip().split()
                    if parts and ("." in parts[0] or "$" in parts[0]):
                        graph_classes.append(line.strip())

                if in_desc:
                    description_lines.append(line)

            # Flush last suspect
            if current is not None:
                current["stack_frames"] = stack_frames
                current["dominator_path"] = dominator_path
                current["object_graph_classes"] = graph_classes
                if description_lines:
                    current["description"] = " ".join(description_lines[:10])
                suspects.append(current)

    # Deduplicate suspects (same number may appear in multiple pages)
    seen_nums: set = set()
    deduped: List[Dict] = []
    for s in suspects:
        if s["suspect_number"] not in seen_nums:
            seen_nums.add(s["suspect_number"])
            deduped.append(s)

    return {
        "suspects": deduped,
        "histogram": histogram,
        "raw_text_by_page": all_raw,
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def analyse_hprof(
    hprof_path: str,
    mat_home: Path = DEFAULT_MAT_HOME,
    mat_heap_gb: int = 12,
    timeout_s: int = 7200,
) -> Dict[str, Any]:
    """
    Full pipeline: ensure MAT, run analysis, parse results.

    Returns structured findings dict.
    """
    suspects_zip = run_mat(
        hprof_path=hprof_path,
        mat_home=mat_home,
        mat_heap_gb=mat_heap_gb,
        timeout_s=timeout_s,
    )
    findings = _parse_leak_suspects(suspects_zip)
    findings["suspects_zip"] = str(suspects_zip)
    return findings

