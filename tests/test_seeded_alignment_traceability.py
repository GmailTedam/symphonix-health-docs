from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENT_IDS = [
    "DS-001",
    "DS-002",
    "DS-003",
    "DS-101",
    "DS-102",
    "DS-103",
    "DS-104",
    "DS-105",
    "DS-106",
    "DS-107",
    "DS-108",
    "DS-109",
    "DS-110",
    "DS-111",
    "DS-112",
    "DS-113",
    "DS-114",
    "DS-115",
    "DS-116",
    "DS-117",
    "DS-118",
    "DS-119",
    "DS-120",
    "DS-121",
    "DS-122",
    "DS-123",
    "DS-124",
    "DS-125",
    "DS-126",
    "DS-127",
    "DS-128",
    "DS-129",
    "DS-130",
    "DS-131",
    "DS-132",
    "DS-133",
    "DS-134",
    "DS-135",
    "DS-136",
    "DS-137",
    "DS-138",
    "DS-139",
    "DS-140",
    "DS-141",
    "DS-142",
    "DS-143",
    "DS-144",
    "DS-145",
    "DS-146",
    "DS-147",
    "DS-148",
    "DS-149",
    "DS-150",
    "DS-151",
    "DS-152",
    "DS-153",
    "DS-154",
    "DS-155",
    "DS-156",
    "DS-157",
    "DS-158",
    "DS-159",
    "DS-160",
    "DS-161",
    "DS-162",
    "DS-163",
    "DS-164",
    "DS-165",
    "DS-166",
    "DS-167",
    "DS-168",
    "DS-169",
    "DS-170",
    "DS-171",
    "DS-172",
    "DS-173",
    "DS-174",
    "DS-175",
    "DS-176",
    "DS-177",
    "DS-178",
    "DS-179",
    "DS-180",
    "DS-181",
    "DS-182",
    "DS-183",
    "DS-184",
    "DS-185",
    "DS-186",
    "DS-187",
    "DS-188",
    "DS-189",
    "DS-190",
    "DS-191",
    "DS-192",
    "DS-193",
    "DS-194",
    "DS-195",
    "DS-196",
    "FR-SHD-001",
    "FR-SHD-002",
    "FR-SHD-003",
    "NFR-CO-001",
    "NFR-CO-002",
    "NFR-FL-001",
    "NFR-FL-002",
    "NFR-IC-001",
    "NFR-MA-001",
    "NFR-MA-002",
    "NFR-MA-003",
    "NFR-MA-004",
    "NFR-PE-001",
    "NFR-RE-001",
    "NFR-RE-002",
    "NFR-RE-003",
    "NFR-SA-001",
    "NFR-SA-002",
    "NFR-SE-001",
    "NFR-SE-002",
    "NFR-SE-003",
    "NFR-SE-004",
    "NFR-SHD-001",
    "NFR-SHD-002"
]


def _load_traceability() -> dict:
    module_path = ROOT / "seeded_alignment_trace.py"
    spec = importlib.util.spec_from_file_location("seeded_alignment_trace", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TRACEABILITY


def _load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_seeded_alignment_traceability_paths_exist() -> None:
    traceability = _load_traceability()
    assert traceability, "seeded alignment traceability map is empty"
    assert set(REQUIREMENT_IDS) == set(traceability)

    for requirement_id, evidence in traceability.items():
        assert requirement_id
        for key in (
            "specification_paths",
            "use_case_paths",
            "implementation_paths",
            "test_paths",
            "seed_paths",
            "documentation_paths",
        ):
            paths = evidence.get(key)
            assert paths, f"{requirement_id} has no {key}"
            for rel_path in paths:
                path = ROOT / rel_path
                message = f"{requirement_id} missing {key}: {rel_path}"
                assert path.exists(), message


def test_seeded_alignment_matrix_and_seed_cover_every_requirement() -> None:
    requirement_ids = set(REQUIREMENT_IDS)

    matrix = _load_json(
        "tests/harness/reduced_json_matrices/seeded_alignment_trace.14col.json"
    )
    cases = matrix["test_cases"]
    matrix_ids = {
        tag
        for case in cases
        for tag in case.get("tags", [])
        if tag in requirement_ids
    }
    assert matrix_ids == requirement_ids

    seed_data = _load_json("seed_data/seeded_requirement_traceability.json")
    seed_ids = {row["requirement_id"] for row in seed_data["requirements"]}
    assert seed_ids == requirement_ids

    spec_text = (
        ROOT / "docs/specifications/seeded-requirement-traceability.md"
    ).read_text(encoding="utf-8")
    missing_from_spec = [rid for rid in requirement_ids if rid not in spec_text]
    assert not missing_from_spec
