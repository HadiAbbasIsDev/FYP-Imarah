"""Create editable draw.io diagrams and matching SVGs for the project documentation.
Use: python scripts/build_diagrams.py. Coordinates are deliberately straightforward.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "diagrams"
COLORS = {
    "green": ("#eaf2e3", "#517248"),
    "blue": ("#eaf0f3", "#526c7a"),
    "amber": ("#fbf1df", "#987844"),
    "plain": ("#ffffff", "#7e8975"),
}


def diagram(relative, title, subtitle, nodes, edges, width=1120, height=740):
    """A node is (id, text, x, y, width, height, colour); an edge uses node IDs."""
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="Imarah.tech", version="24.7.17")
    page = ET.SubElement(mxfile, "diagram", id=relative.replace("/", "-"), name=title)
    model = ET.SubElement(
        page,
        "mxGraphModel",
        dx=str(width),
        dy=str(height),
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth=str(width),
        pageHeight=str(height),
        math="0",
        shadow="0",
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    for ident, value, x, y, w, h, size in [
        ("title", title, 35, 18, width - 70, 36, 24),
        ("subtitle", subtitle, 35, 58, width - 70, 35, 12),
    ]:
        cell = ET.SubElement(
            root,
            "mxCell",
            id=ident,
            value=value,
            style=f"text;html=0;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize={size};fontColor=#294837;",
            vertex="1",
            parent="1",
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(x),
            y=str(y),
            width=str(w),
            height=str(h),
            attrib={"as": "geometry"},
        )
    node_map = {node[0]: node for node in nodes}
    for ident, label, x, y, w, h, tone in nodes:
        fill, stroke = COLORS[tone]
        cell = ET.SubElement(
            root,
            "mxCell",
            id=ident,
            value=label,
            style=f"rounded=1;whiteSpace=wrap;html=0;fillColor={fill};strokeColor={stroke};fontColor=#294837;fontSize=13;spacing=12;",
            vertex="1",
            parent="1",
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(x),
            y=str(y),
            width=str(w),
            height=str(h),
            attrib={"as": "geometry"},
        )
    for index, (source, dest, label) in enumerate(edges):
        cell = ET.SubElement(
            root,
            "mxCell",
            id=f"edge-{index}",
            value=label,
            style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=0;endArrow=block;endFill=1;strokeColor=#85947c;fontColor=#66785c;fontSize=11;labelBackgroundColor=#f8faf5;",
            edge="1",
            parent="1",
            source=source,
            target=dest,
        )
        ET.SubElement(cell, "mxGeometry", relative="1", attrib={"as": "geometry"})
    ET.indent(mxfile)
    ET.ElementTree(mxfile).write(
        target.with_suffix(".drawio"), encoding="utf-8", xml_declaration=True
    )

    svg = ET.Element(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        viewBox=f"0 0 {width} {height}",
        role="img",
    )
    svg.append(
        ET.Comment(
            "Use: project flow preview. Copyright (c) 2026 Imarah.tech. All rights reserved."
        )
    )
    ET.SubElement(svg, "title").text = title
    ET.SubElement(svg, "rect", width=str(width), height=str(height), fill="#f8faf5")
    defs = ET.SubElement(svg, "defs")
    marker = ET.SubElement(
        defs,
        "marker",
        id="arrow",
        viewBox="0 0 10 10",
        refX="9",
        refY="5",
        markerWidth="6",
        markerHeight="6",
        orient="auto-start-reverse",
    )
    ET.SubElement(marker, "path", d="M 0 0 L 10 5 L 0 10 z", fill="#85947c")

    def text(x, y, value, size=13, fill="#294837", anchor="start", weight="normal"):
        ET.SubElement(
            svg,
            "text",
            x=str(x),
            y=str(y),
            fill=fill,
            attrib={
                "font-family": "Arial, sans-serif",
                "font-size": str(size),
                "text-anchor": anchor,
                "font-weight": weight,
            },
        ).text = value

    text(35, 47, title, 24, weight="bold")
    text(35, 77, subtitle, 12, fill="#6c7f60")
    for source, dest, label in edges:
        _, _, ax, ay, aw, ah, _ = node_map[source]
        _, _, bx, by, bw, bh, _ = node_map[dest]
        if abs((ax + aw / 2) - (bx + bw / 2)) < 30:
            x1, y1 = ax + aw / 2, ay + ah if by > ay else ay
            x2, y2 = bx + bw / 2, by if by > ay else by + bh
        elif abs((ay + ah / 2) - (by + bh / 2)) < 30:
            x1, y1 = ax + aw if bx > ax else ax, ay + ah / 2
            x2, y2 = bx if bx > ax else bx + bw, by + bh / 2
        else:
            x1, y1 = ax + aw / 2, ay + ah if by > ay else ay
            x2, y2 = bx + bw / 2, by if by > ay else by + bh
        ET.SubElement(
            svg,
            "path",
            d=f"M{x1} {y1} L{x2} {y2}",
            fill="none",
            stroke="#85947c",
            attrib={"stroke-width": "1.5", "marker-end": "url(#arrow)"},
        )
        if label:
            tx, ty = (x1 + x2) / 2, (y1 + y2) / 2 - 7
            ET.SubElement(
                svg,
                "rect",
                x=str(tx - len(label) * 3.2 - 4),
                y=str(ty - 12),
                width=str(len(label) * 6.4 + 8),
                height="18",
                fill="#f8faf5",
            )
            text(tx, ty, label, 10, fill="#6c7f60", anchor="middle")
    for ident, label, x, y, w, h, tone in nodes:
        fill, stroke = COLORS[tone]
        ET.SubElement(
            svg,
            "rect",
            x=str(x),
            y=str(y),
            width=str(w),
            height=str(h),
            rx="8",
            fill=fill,
            stroke=stroke,
        )
        lines = []
        for paragraph in label.split("\n"):
            lines.extend(textwrap.wrap(paragraph, width=max(15, int(w / 7.3))) or [""])
        for i, line in enumerate(lines):
            text(
                x + w / 2,
                y + h / 2 - (len(lines) - 1) * 9 + i * 18 + 4,
                line,
                12,
                anchor="middle",
                weight="bold" if i == 0 else "normal",
            )
    text(
        35,
        height - 21,
        "Imarah.tech · Phase 1 · September 2026 · Edit the paired .drawio file in diagrams.net",
        10,
        fill="#87947b",
    )
    ET.indent(svg)
    ET.ElementTree(svg).write(target.with_suffix(".svg"), encoding="utf-8", xml_declaration=True)


diagram(
    "architecture/system-overview",
    "Imarah.tech — the connected system",
    "Green: working September components. Amber: optional connections or planned modules.",
    [
        (
            "user",
            "Student / reviewer\nDesktop or mobile browser",
            40,
            140,
            220,
            85,
            "plain",
        ),
        ("pwa", "Progressive Web App\nReact + TypeScript", 360, 140, 235, 85, "green"),
        ("api", "Local API\nFastAPI · single process", 730, 140, 260, 85, "green"),
        (
            "db",
            "SQLite + upload files\nInspection history and jobs",
            730,
            340,
            260,
            90,
            "green",
        ),
        ("vlm", "Selected VLM route\nLocal workers / Qwen VPS", 365, 340, 230, 90, "green"),
        (
            "yolo",
            "Hosted YOLO segmentation\nCrack outlines + boxes",
            40,
            340,
            235,
            90,
            "green",
        ),
        (
            "future",
            "Future modules\nConstruction site management · IoT monitoring · urban analysis\nCurrent pages use simulated data",
            250,
            555,
            640,
            90,
            "amber",
        ),
    ],
    [
        ("user", "pwa", "HTTP / PWA"),
        ("pwa", "api", "JSON + photo"),
        ("api", "db", "save"),
        ("api", "vlm", "background task"),
        ("api", "yolo", "optional detector call"),
        ("pwa", "future", "shared navigation"),
    ],
)

diagram(
    "architecture/local-deployment",
    "Phase 1 — local deployment",
    "One job at a time. Local workers load fresh; the separate Qwen VPS choice uses the SSH tunnel.",
    [
        ("browser", "Browser / installed PWA\nhttp://127.0.0.1:8000", 40, 140, 260, 95, "plain"),
        ("server", "Python API server\nfrontend/dist and /api", 400, 140, 300, 95, "green"),
        ("queue", "One background thread\nInspections and benchmarks", 780, 140, 295, 95, "green"),
        (
            "cache",
            "Browser service worker\nApp shell only\nNo API or photograph cache",
            40,
            345,
            260,
            105,
            "blue",
        ),
        (
            "worker",
            "Local Python worker\nRead image; return raw output\n300-second default timeout",
            745,
            345,
            330,
            105,
            "green",
        ),
        (
            "remote",
            "Qwen 4B · VPS option\nImage API through SSH\n127.0.0.1:18084\nNo local fallback",
            400,
            340,
            290,
            115,
            "green",
        ),
        (
            "smol",
            "SmolVLM / Transformers\nCPU · float32 · 4 threads\nLoads inside the worker",
            430,
            545,
            290,
            110,
            "green",
        ),
        (
            "ollama",
            "Project-local Ollama\n127.0.0.1:11435\nQwen · CPU · quantized\nUnload after every request",
            775,
            545,
            300,
            115,
            "green",
        ),
        (
            "disk",
            "Project disk\nmodels/ · data/ · benchmarks/results/\nNo downloads during inference",
            390,
            765,
            410,
            100,
            "blue",
        ),
    ],
    [
        ("browser", "server", "same origin"),
        ("server", "queue", "submit job"),
        ("queue", "worker", "Local option"),
        ("queue", "remote", "VPS option"),
        ("worker", "smol", "local adapter"),
        ("worker", "ollama", "streaming HTTP"),
        ("smol", "disk", "read weights"),
        ("ollama", "disk", "read GGUF weights"),
        ("browser", "cache", "offline shell"),
    ],
    height=940,
)

diagram(
    "flows/inspection-flow",
    "From a surface photo to a reviewable report",
    "The demo never substitutes a failed live detector. A VLM failure preserves detector evidence.",
    [
        (
            "photo",
            "Choose or capture image\nAdd name and location",
            40,
            125,
            235,
            80,
            "plain",
        ),
        (
            "validate",
            "Validate & re-encode\n10 MB · 20 MP · JPEG/PNG/WebP",
            380,
            125,
            265,
            80,
            "green",
        ),
        (
            "reject",
            "Invalid input\nShow an actionable error",
            770,
            125,
            260,
            80,
            "amber",
        ),
        (
            "demo",
            "Demo mode\nSelected VLM only\nNo detector overlay",
            40,
            320,
            250,
            90,
            "amber",
        ),
        (
            "mode",
            "Select detector mode\nSave image + queue job",
            390,
            320,
            255,
            90,
            "green",
        ),
        (
            "live",
            "Live YOLO segmentation\nValidate boxes + crack outlines\nFailure → failed job",
            770,
            320,
            270,
            90,
            "green",
        ),
        (
            "vlm",
            "Local or VPS VLM observation\nRead actual image\nLive detections add context",
            380,
            500,
            265,
            95,
            "green",
        ),
        (
            "report",
            "Save draft + crack outlines\nIf VLM fails: partial report\nNo generated safety rating",
            765,
            500,
            280,
            95,
            "green",
        ),
        (
            "review",
            "Human reviews the evidence\nRecord notes · export / print",
            380,
            685,
            265,
            85,
            "plain",
        ),
    ],
    [
        ("photo", "validate", "upload"),
        ("validate", "reject", "invalid"),
        ("validate", "mode", "valid"),
        ("mode", "demo", "demo"),
        ("mode", "live", "live"),
        ("demo", "vlm", "image only"),
        ("live", "vlm", "image + detections"),
        ("vlm", "report", "raw text / error"),
        ("report", "review", "review"),
    ],
    height=830,
)

diagram(
    "flows/benchmark-flow",
    "Comparing models without hiding their mistakes",
    "Exploratory smoke tests; expert quality labels and a building-specific holdout set are still needed.",
    [
        (
            "inputs",
            "Fixed images + fixed prompt\nTwo road photos + two synthetic controls",
            50,
            130,
            290,
            95,
            "blue",
        ),
        (
            "settings",
            "Select available Local / VPS models\nPin revisions · seed 42\n140 tokens · record execution settings",
            650,
            130,
            300,
            95,
            "blue",
        ),
        (
            "loop",
            "For each model × image × repetition\nLocal worker or VPS request\nVPS can retain a warm model",
            350,
            340,
            350,
            100,
            "green",
        ),
        (
            "save",
            "Save each row immediately\nImage SHA-256 · prompt · raw text\nTime · tokens · peak worker RAM",
            60,
            565,
            340,
            105,
            "green",
        ),
        (
            "compare",
            "Compare observations and latency\nHuman rubric review follows\nDo not label speed as accuracy",
            660,
            565,
            340,
            105,
            "plain",
        ),
    ],
    [
        ("inputs", "loop", "same inputs"),
        ("settings", "loop", "record conditions"),
        ("loop", "save", "success or failure"),
        ("save", "compare", "inspect results"),
    ],
)

diagram(
    "data/phase1-data-model",
    "Phase 1 — what we store",
    "The first schema stays small. Future worker and sensor tables will be designed when those modules start.",
    [
        (
            "inspection",
            "inspections (SQLite)\nid · primary key\ncreated_at\npayload JSON: context, dimensions, boxes + polygons, VLM, report, review",
            65,
            150,
            345,
            205,
            "green",
        ),
        (
            "job",
            "jobs (SQLite)\nid · primary key\nkind: inspection / benchmark\nstatus: queued, running, complete, partial, failed\nmessage · created_at",
            640,
            150,
            365,
            205,
            "green",
        ),
        (
            "image",
            "data/uploads/<inspection-id>.jpg\nRe-encoded image\nEXIF metadata removed",
            65,
            515,
            345,
            110,
            "blue",
        ),
        (
            "benchmark",
            "benchmarks/results/<job-id>.json\nSettings and model/image rows\nInput hashes · raw outputs · runtime",
            640,
            515,
            365,
            110,
            "blue",
        ),
    ],
    [
        ("inspection", "job", "same ID for an inspection"),
        ("inspection", "image", "one image per inspection"),
        ("job", "benchmark", "benchmark job result"),
    ],
)

diagram(
    "roadmap/project-stages",
    "Imarah.tech — staged delivery",
    "Dates follow the proposal; September adds an early demo. FYP-II dates remain tentative.",
    [
        (
            "s1",
            "01 · September 2026\nFoundation and evaluation demo\nPWA · small VLMs · documentation",
            60,
            125,
            440,
            95,
            "green",
        ),
        (
            "s2",
            "02 · October–December 2026\nBuilding health assessment\nYOLO + validated VLM reports",
            620,
            125,
            440,
            95,
            "blue",
        ),
        (
            "s3",
            "03 · January–February 2027\nConstruction site management\nWorkers · attendance · PPE · materials",
            620,
            340,
            440,
            95,
            "amber",
        ),
        (
            "s4",
            "04 · March–April 2027\nBuilding monitoring\nSensor prototype · weather context",
            60,
            340,
            440,
            95,
            "amber",
        ),
        (
            "s5",
            "05 · April–May 2027\nUrban analysis and final evaluation\nGeospatial processing · integration · defense",
            335,
            555,
            460,
            105,
            "amber",
        ),
    ],
    [
        ("s1", "s2", "develop + evaluate"),
        ("s2", "s3", "integrate first"),
        ("s3", "s4", "next module"),
        ("s4", "s5", "integrate + evaluate"),
    ],
)
diagram(
    "architecture/vps-qwen",
    "Qwen on the shared VPS",
    "The PC reaches a private image API through SSH. Model files and logs stay on the data disk.",
    [
        (
            "pc",
            "Project PC\nImarah VPS option / image client\n127.0.0.1:18084",
            40,
            140,
            275,
            105,
            "plain",
        ),
        (
            "ssh",
            "Authenticated SSH tunnel\nEncrypted connection to VPS\nKeep the PC terminal open",
            400,
            140,
            290,
            105,
            "blue",
        ),
        (
            "api",
            "Qwen image API\nVPS 127.0.0.1:18084\nValidate image; return raw text",
            790,
            140,
            285,
            105,
            "green",
        ),
        (
            "client",
            "Response JSON\nRaw observation + model identity\nActual settings and timings",
            40,
            365,
            275,
            115,
            "green",
        ),
        (
            "engine",
            "Dedicated Ollama engine\nVPS 127.0.0.1:11440\nOne Qwen request at a time",
            790,
            365,
            285,
            115,
            "green",
        ),
        (
            "runtime",
            "Root filesystem: /opt/aiml\nVersioned Ollama executable\nSeparate Python environment",
            400,
            565,
            290,
            115,
            "blue",
        ),
        (
            "weights",
            "Data disk: /sdb-disk/AIML-Models\nVLM-models / named Qwen folder\nWeights, scripts, logs, README",
            755,
            565,
            345,
            115,
            "blue",
        ),
        (
            "projects",
            "Separate project data\n/sdb-disk/projects/<name>\nSLMs folder reserved for later",
            40,
            565,
            275,
            115,
            "amber",
        ),
    ],
    [
        ("pc", "ssh", "photo + prompt"),
        ("ssh", "api", "forward privately"),
        ("api", "engine", "vision request"),
        ("engine", "weights", "read pinned model"),
        ("engine", "runtime", "run engine"),
        ("api", "client", "through the same tunnel"),
        ("client", "projects", "future project integration"),
    ],
    height=770,
)
print("Created seven editable draw.io diagrams and seven SVG previews.")
