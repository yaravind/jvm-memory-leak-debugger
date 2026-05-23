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
import os
import platform
import re
import shutil
import subprocess
import tempfile
import time
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# ---------------------------------------------------------------------------
# MAT distribution constants
# ---------------------------------------------------------------------------

MAT_VERSION = "1.16.1.20250109"
MAT_VERSION_SHORT = "1.16.1"
MAT_DOWNLOAD_BASE = f"https://download.eclipse.org/mat/{MAT_VERSION_SHORT}/rcp"


@dataclass(frozen=True)
class MatDistribution:
    platform_key: str
    archive_name: str
    sha256: str

    @property
    def url(self) -> str:
        return f"{MAT_DOWNLOAD_BASE}/{self.archive_name}"


MAT_DISTRIBUTIONS: Dict[str, MatDistribution] = {
    "linux-aarch64": MatDistribution(
        platform_key="linux-aarch64",
        archive_name=f"MemoryAnalyzer-{MAT_VERSION}-linux.gtk.aarch64.zip",
        sha256="1dbd98be41c50a14d2a1196f0f3fe19908506a025959f60879325bde0473cd9d",
    ),
    "linux-x86_64": MatDistribution(
        platform_key="linux-x86_64",
        archive_name=f"MemoryAnalyzer-{MAT_VERSION}-linux.gtk.x86_64.zip",
        sha256="7c7bc3457e08bdcd187fdafb28573b00e8e9f56b46a872fb63dbbaf7f508f01e",
    ),
    "macos-aarch64": MatDistribution(
        platform_key="macos-aarch64",
        archive_name=f"MemoryAnalyzer-{MAT_VERSION}-macosx.cocoa.aarch64.zip",
        sha256="99368c4a4b61593555c1d101acb6785afe0b927dbf4c33246ac647a849732101",
    ),
    "macos-x86_64": MatDistribution(
        platform_key="macos-x86_64",
        archive_name=f"MemoryAnalyzer-{MAT_VERSION}-macosx.cocoa.x86_64.zip",
        sha256="7b4bff9866c6341f4d26455baef88c7eabbb424bb515e8d993026f706a66d14d",
    ),
    "windows-x86_64": MatDistribution(
        platform_key="windows-x86_64",
        archive_name=f"MemoryAnalyzer-{MAT_VERSION}-win32.win32.x86_64.zip",
        sha256="79e0b0c5c25fe718e58a3d42135b537c0dd3b2f3cb453c5e9a91d3b7a913ea7d",
    ),
}

DEFAULT_MAT_HOME = Path(tempfile.gettempdir()) / "eclipse-mat" / MAT_VERSION
EQUINOX_JAR_GLOB = "org.eclipse.equinox.launcher_*.jar"


# ---------------------------------------------------------------------------
# Java 17 discovery
# ---------------------------------------------------------------------------

def _java_bin(java_home: Path) -> Path:
    exe = "java.exe" if os.name == "nt" else "java"
    return java_home / "bin" / exe


def _java_major_version(java_bin: Path) -> Optional[int]:
    try:
        result = subprocess.run(
            [str(java_bin), "-version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None

    version_text = result.stderr or result.stdout
    m = re.search(r'version "(\d+)(?:\.(\d+))?', version_text)
    if not m:
        return None
    major = int(m.group(1))
    if major == 1 and m.group(2):
        return int(m.group(2))
    return major


def _valid_java_home(java_home: Path) -> bool:
    return _java_bin(java_home).exists() and (_java_major_version(_java_bin(java_home)) or 0) >= 17


def _java_home_from_path() -> Optional[Path]:
    java = shutil.which("java")
    if not java:
        return None
    java_bin = Path(java).resolve()
    if (_java_major_version(java_bin) or 0) < 17:
        return None
    return java_bin.parent.parent


def _find_java17() -> Path:
    """Return path to a Java 17+ JAVA_HOME or raise EnvironmentError."""
    for env_var in ("JAVA17_HOME", "JAVA_HOME"):
        if env_var in os.environ:
            p = Path(os.environ[env_var])
            if _valid_java_home(p):
                return p
            raise EnvironmentError(
                f"{env_var} is set to {p}, but it does not contain Java 17+."
            )

    # macOS native JDK discovery.
    try:
        result = subprocess.run(
            ["/usr/libexec/java_home", "-v", "17"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            p = Path(result.stdout.strip())
            if _valid_java_home(p):
                return p
    except Exception:
        pass

    path_home = _java_home_from_path()
    if path_home is not None:
        return path_home

    raise EnvironmentError(
        "Java 17+ is required to run Eclipse MAT 1.16.\n"
        "Set JAVA17_HOME or JAVA_HOME to your JDK 17+ home directory, "
        "or ensure a Java 17+ executable is available on PATH."
    )


def _curl_available() -> bool:
    return shutil.which("curl") is not None


# ---------------------------------------------------------------------------
# MAT installation
# ---------------------------------------------------------------------------

def _arch() -> str:
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        return "aarch64"
    if machine in ("amd64", "x86_64"):
        return "x86_64"
    if machine in ("ppc64le", "powerpc64le"):
        return "ppc64le"
    return machine


def _platform_key() -> str:
    system = platform.system().lower()
    arch = _arch()
    if system == "darwin":
        return f"macos-{arch}"
    if system == "linux":
        return f"linux-{arch}"
    if system == "windows":
        return f"windows-{arch}"
    return f"{system}-{arch}"


def _mat_distribution() -> MatDistribution:
    platform_key = _platform_key()
    if platform_key not in MAT_DISTRIBUTIONS:
        supported = ", ".join(sorted(MAT_DISTRIBUTIONS))
        raise RuntimeError(
            f"No Eclipse MAT {MAT_VERSION} distribution configured for "
            f"{platform_key}. Supported platforms: {supported}."
        )
    return MAT_DISTRIBUTIONS[platform_key]


def _verify_sha256(path: Path, expected: str) -> bool:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest() == expected


def _eclipse_dir(mat_home: Path) -> Optional[Path]:
    candidates = [
        mat_home,
        mat_home / "mat",
        mat_home / "MemoryAnalyzer.app" / "Contents" / "Eclipse",
        mat_home / "Contents" / "Eclipse",
    ]
    for candidate in candidates:
        if (candidate / "plugins").exists():
            return candidate
    return None


def _copy_extracted_root(extract_dir: Path, mat_home: Path) -> None:
    roots = [p for p in extract_dir.iterdir() if p.name != "__MACOSX"]
    if len(roots) != 1:
        raise RuntimeError(
            f"Expected one top-level MAT directory in archive, found: "
            f"{', '.join(p.name for p in roots)}"
        )

    if mat_home.exists():
        shutil.rmtree(mat_home)
    mat_home.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(roots[0], mat_home)


def _download_mat(mat_home: Path) -> None:
    """Download, verify, and unpack the configured MAT ZIP distribution."""
    dist = _mat_distribution()

    print(f"[mat_runner] Downloading Eclipse MAT {MAT_VERSION} for {dist.platform_key}...")
    print(f"[mat_runner]   {dist.url}")

    with tempfile.TemporaryDirectory() as td:
        archive = Path(td) / dist.archive_name
        subprocess.run(
            ["curl", "-L", "-o", str(archive), dist.url],
            check=True
        )
        if not _verify_sha256(archive, dist.sha256):
            raise RuntimeError(
                f"SHA-256 mismatch for downloaded MAT archive.\n"
                f"Expected: {dist.sha256}\n"
                f"Got:      {hashlib.sha256(archive.read_bytes()).hexdigest()}"
            )
        extract_dir = Path(td) / "extract"
        extract_dir.mkdir()
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(extract_dir)
        _copy_extracted_root(extract_dir, mat_home)
    print(f"[mat_runner] MAT installed at: {mat_home}")


def ensure_mat(mat_home: Path = DEFAULT_MAT_HOME) -> Path:
    """Return the Eclipse directory inside MAT, downloading if absent."""
    eclipse_dir = _eclipse_dir(mat_home)
    if eclipse_dir is None:
        _download_mat(mat_home)
        eclipse_dir = _eclipse_dir(mat_home)
    if eclipse_dir is None:
        raise RuntimeError(f"Eclipse MAT installation is invalid: {mat_home}")
    return eclipse_dir


def _equinox_jar(eclipse_dir: Path) -> Path:
    matches = list((eclipse_dir / "plugins").glob(EQUINOX_JAR_GLOB))
    if not matches:
        raise FileNotFoundError(
            f"Equinox launcher jar not found under {eclipse_dir}/plugins"
        )
    return sorted(matches)[-1]


def runtime_diagnostics(mat_home: Path = DEFAULT_MAT_HOME) -> Dict[str, Any]:
    """
    Return local Java/MAT readiness without downloading MAT or reading a heap.

    A host is ready for first-run analysis when the platform is supported and
    Java 17+ is discoverable. Existing MAT installation details are reported
    separately because first use may auto-download the pinned MAT archive.
    """
    status: Dict[str, Any] = {
        "platform_key": _platform_key(),
        "platform_supported": False,
        "mat_version": MAT_VERSION_SHORT,
        "mat_home": str(Path(mat_home)),
        "mat_installed": False,
        "mat_eclipse_dir": None,
        "equinox_launcher_found": False,
        "java_home": None,
        "java_major_version": None,
        "java_17_plus": False,
        "curl_available": _curl_available(),
        "can_auto_install_mat": False,
        "ready_for_analysis": False,
        "errors": [],
    }

    try:
        dist = _mat_distribution()
        status.update({
            "platform_supported": True,
            "mat_archive": dist.archive_name,
            "mat_download_url": dist.url,
            "mat_archive_sha256": dist.sha256,
        })
    except RuntimeError as exc:
        status["errors"].append(str(exc))

    try:
        java_home = _find_java17()
        java_bin = _java_bin(java_home)
        java_major = _java_major_version(java_bin)
        status.update({
            "java_home": str(java_home),
            "java_major_version": java_major,
            "java_17_plus": (java_major or 0) >= 17,
        })
    except Exception as exc:
        status["errors"].append(str(exc))

    eclipse_dir = _eclipse_dir(Path(mat_home))
    if eclipse_dir is not None:
        status["mat_installed"] = True
        status["mat_eclipse_dir"] = str(eclipse_dir)
        try:
            status["equinox_launcher_found"] = _equinox_jar(eclipse_dir).exists()
        except FileNotFoundError as exc:
            status["errors"].append(str(exc))

    status["can_auto_install_mat"] = (
        status["platform_supported"] and status["curl_available"]
    )
    mat_ready = status["equinox_launcher_found"] or status["can_auto_install_mat"]
    status["ready_for_analysis"] = (
        status["platform_supported"]
        and status["java_17_plus"]
        and mat_ready
    )
    if status["platform_supported"] and not status["mat_installed"] and not status["curl_available"]:
        status["errors"].append(
            "curl is required to download Eclipse MAT on first run. "
            "Install curl or pass mat_home pointing at an existing MAT installation."
        )
    return status


# ---------------------------------------------------------------------------
# MAT headless run
# ---------------------------------------------------------------------------

def _stop_process(proc: subprocess.Popen, grace_s: float = 5.0) -> str:
    """Stop a MAT process without leaving it running after a timeout."""
    try:
        proc.terminate()
    except ProcessLookupError:
        return "already exited"

    try:
        proc.wait(timeout=grace_s)
        return "terminated"
    except subprocess.TimeoutExpired:
        pass

    try:
        proc.kill()
    except ProcessLookupError:
        return "exited after terminate"

    try:
        proc.wait(timeout=grace_s)
        return "killed"
    except subprocess.TimeoutExpired:
        return "kill timed out"


def _last_log_lines(log_lines: List[str], limit: int = 40) -> str:
    return "\n".join(log_lines[-limit:]) if log_lines else "(no MAT output captured)"


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
    java_bin = _java_bin(java_home)
    equinox = _equinox_jar(eclipse_dir)

    # Check if already analysed (index files present)
    idx = hprof.with_suffix(".index")
    suspects_zip = hprof.parent / (hprof.stem + "_Leak_Suspects.zip")

    if suspects_zip.exists() and idx.exists():
        print(f"[mat_runner] Found existing suspects report: {suspects_zip}")
        return suspects_zip

    workspace = Path(tempfile.mkdtemp(prefix="mat-workspace-"))
    try:
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

        print("[mat_runner] Starting MAT analysis (this may take 10-30 min for large dumps)…")
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
                stop_status = _stop_process(proc)
                raise TimeoutError(
                    f"MAT analysis exceeded {timeout_s}s timeout; process stop status: "
                    f"{stop_status}. Consider increasing mat_heap_gb or timeout_s.\n"
                    f"Last log lines:\n{_last_log_lines(log_lines)}"
                )

        elapsed = round(time.time() - start, 1)
        rc = proc.wait()
        print(f"[mat_runner] MAT finished in {elapsed}s (exit={rc})")

        if not suspects_zip.exists():
            raise RuntimeError(
                f"MAT did not produce {suspects_zip}.\n"
                f"Last log lines:\n{_last_log_lines(log_lines)}"
            )

        return suspects_zip
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


# ---------------------------------------------------------------------------
# HTML report parser
# ---------------------------------------------------------------------------

class _MatReportTextExtract(HTMLParser):
    def __init__(self):
        super().__init__()
        self._skip = False
        self._problem_depth = 0
        self.problem_suspects: List[List[str]] = []
        self.texts: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True
            return

        if self._problem_depth > 0:
            self._problem_depth += 1
            return

        attr_text = " ".join(str(value or "") for _name, value in attrs).lower()
        attr_text = attr_text.replace("_", "-")
        if tag in ("article", "div", "section") and "problem-suspect" in attr_text:
            self._problem_depth = 1
            self.problem_suspects.append([])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False
            return
        if self._problem_depth > 0:
            self._problem_depth -= 1

    def handle_data(self, data):
        if not self._skip:
            s = data.strip()
            if s:
                self.texts.append(s)
                if self._problem_depth > 0 and self.problem_suspects:
                    self.problem_suspects[-1].append(s)


def _extract_text(html: str) -> List[str]:
    parser = _MatReportTextExtract()
    parser.feed(html)
    return parser.texts


def _extract_mat_text(html: str) -> Tuple[List[str], List[List[str]]]:
    parser = _MatReportTextExtract()
    parser.feed(html)
    return parser.texts, [texts for texts in parser.problem_suspects if texts]


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
            texts, problem_suspects = _extract_mat_text(html)
            if problem_suspects:
                for i, suspect_texts in enumerate(problem_suspects, start=1):
                    page_texts[f"{p.name}#problem-suspect-{i}"] = suspect_texts
            else:
                page_texts[p.name] = texts

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
_RE_CLASS_PREFIX = re.compile(r"^(?:com|java|javax|jdk|kotlin|net|org|scala|sun)\.")


def _parse_bytes(s: str) -> int:
    s = s.replace(",", "").strip()
    try:
        return int(s)
    except ValueError:
        return 0


def _structure_findings(page_texts: Dict[str, List[str]]) -> Dict[str, Any]:
    suspects: List[Dict[str, Any]] = []
    histogram: List[Dict[str, Any]] = []
    suspect_parse_failures: List[str] = []

    for page_name, texts in page_texts.items():
        joined = "\n".join(texts)

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

        has_problem_suspect_text = "Problem Suspect" in joined
        has_numbered_suspect = re.search(r"Problem Suspect \d+", joined) is not None
        page_suspect_count_before = len(suspects)

        # ---- Suspect pages ----
        if has_numbered_suspect:
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
                    in_desc = False
                    in_stack = False
                    in_graph = False

                if "All Accumulated Objects by Class" in line:
                    in_graph = True
                    in_desc = False
                    in_dom = False
                    in_stack = False

                if "Thread Stack" in line or "stacktrace" in line.lower():
                    in_stack = True
                    in_desc = False
                    in_dom = False
                    in_graph = False

                if in_desc and _RE_CLASS_PREFIX.match(line):
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

        if has_problem_suspect_text and len(suspects) == page_suspect_count_before:
            suspect_parse_failures.append(page_name)

    # Deduplicate suspects (same number may appear in multiple pages)
    seen_nums: set = set()
    deduped: List[Dict] = []
    for s in suspects:
        if s["suspect_number"] not in seen_nums:
            seen_nums.add(s["suspect_number"])
            deduped.append(s)

    if suspect_parse_failures:
        raise ValueError(
            "MAT report mentioned Problem Suspect but no structured suspect could be parsed from: "
            + ", ".join(suspect_parse_failures)
        )

    return {
        "suspects": deduped,
        "histogram": histogram,
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
