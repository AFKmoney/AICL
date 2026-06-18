#!/usr/bin/env python3
"""
AICL Dataset Generator
Converts all .aicl example files into structured JSONL training datasets
for AI model fine-tuning on AICL syntax and patterns.

Usage:
    python tools/generate_dataset.py [--examples-dir DIR] [--output-dir DIR]

Defaults resolve relative to this script so it works from any checkout.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


# Resolve defaults relative to this script so the tool is portable.
_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXAMPLES_DIR = _REPO_ROOT / "examples"
DEFAULT_DATASETS_DIR = _REPO_ROOT / "datasets"
DEFAULT_OUTPUT_JSONL = DEFAULT_DATASETS_DIR / "aicl_mega_dataset.jsonl"
DEFAULT_OUTPUT_MANIFEST = DEFAULT_DATASETS_DIR / "dataset_manifest.json"


DOMAIN_MAP = {
    "01": ("graphics", "Basic Graphics Application"),
    "02": ("gaming", "Game Application - Pong"),
    "03": ("communication", "Chat Application"),
    "04": ("gaming", "Game Application - Chess"),
    "05": ("fintech", "Banking System"),
    "06": ("blockchain", "Blockchain Core Protocol"),
    "07": ("crypto", "Cryptocurrency Wallet"),
    "08": ("defi", "DeFi Platform"),
    "09": ("nft", "NFT Marketplace"),
    "10": ("blockchain", "Smart Contract Engine"),
    "11": ("security", "PKI Certificate Authority"),
    "12": ("security", "Zero-Knowledge Proof System"),
    "13": ("security", "Key Management System"),
    "14": ("security", "End-to-End Secure Messaging"),
    "15": ("security", "Homomorphic Encryption Service"),
    "16": ("patterns", "Microservices Architecture"),
    "17": ("patterns", "CQRS + Event Sourcing"),
    "18": ("patterns", "MVC Web Application"),
    "19": ("patterns", "Observer Pattern Event Bus"),
    "20": ("patterns", "Repository Pattern Data Layer"),
    "21": ("patterns", "Strategy Pattern Engine"),
    "22": ("patterns", "Factory Pattern System"),
    "23": ("patterns", "Decorator Pattern Pipeline"),
    "24": ("patterns", "Plugin Architecture"),
    "25": ("patterns", "Hexagonal Architecture"),
    "26": ("distributed", "Distributed Consensus System"),
    "27": ("distributed", "Service Mesh"),
    "28": ("distributed", "Message Broker"),
    "29": ("distributed", "Distributed Cache"),
    "30": ("distributed", "CDN System"),
    "31": ("distributed", "Load Balancer"),
    "32": ("distributed", "Service Registry & Discovery"),
    "33": ("distributed", "Container Orchestrator"),
    "34": ("distributed", "Serverless Platform"),
    "35": ("distributed", "Multi-Cloud Manager"),
    "36": ("enterprise", "ERP System"),
    "37": ("enterprise", "CRM Platform"),
    "38": ("enterprise", "HR Management"),
    "39": ("enterprise", "Supply Chain Management"),
    "40": ("enterprise", "Fleet Management"),
    "41": ("enterprise", "Warehouse Management"),
    "42": ("enterprise", "Insurance Claims"),
    "43": ("enterprise", "Tax Processing"),
    "44": ("fintech", "Portfolio Management"),
    "45": ("fintech", "Algorithmic Trading"),
    "46": ("aiml", "ML Training Pipeline"),
    "47": ("aiml", "Recommendation Engine"),
    "48": ("aiml", "NLP Processing System"),
    "49": ("aiml", "Computer Vision Pipeline"),
    "50": ("aiml", "Reinforcement Learning Agent"),
    "51": ("aiml", "LLM API Gateway"),
    "52": ("aiml", "Data Lakehouse"),
    "53": ("aiml", "Feature Store"),
    "54": ("aiml", "MLOps Platform"),
    "55": ("aiml", "Autonomous AI Agent"),
    "56": ("iot", "IoT Sensor Network"),
    "57": ("iot", "Smart Home Hub"),
    "58": ("iot", "Real-time Analytics"),
    "59": ("iot", "Streaming Data Pipeline"),
    "60": ("iot", "Telemetry System"),
    "61": ("iot", "Edge Computing Platform"),
    "62": ("iot", "Industrial IoT"),
    "63": ("iot", "Autonomous Vehicle"),
    "64": ("iot", "Drone Fleet Management"),
    "65": ("iot", "Robotics Controller"),
    "66": ("gaming", "MMO Game Server"),
    "67": ("gaming", "Matchmaking System"),
    "68": ("gaming", "Game Economy Engine"),
    "69": ("gaming", "Leaderboard & Ranking"),
    "70": ("media", "Video Streaming Platform"),
    "71": ("media", "Music Streaming Service"),
    "72": ("social", "Social Media Platform"),
    "73": ("media", "Content Management System"),
    "74": ("media", "Live Auction Platform"),
    "75": ("media", "Podcast Platform"),
    "76": ("healthcare", "Hospital Management"),
    "77": ("healthcare", "Electronic Health Records"),
    "78": ("healthcare", "Telemedicine Platform"),
    "79": ("healthcare", "Clinical Trial Management"),
    "80": ("education", "Learning Management System"),
    "81": ("education", "Online Examination System"),
    "82": ("energy", "Smart Grid Management"),
    "83": ("energy", "Energy Trading Platform"),
    "84": ("transport", "Ride-Sharing Platform"),
    "85": ("transport", "Flight Booking System"),
}

# Category groupings for dataset splits
CATEGORY_GROUPS = {
    "crypto_blockchain": list(range(6, 16)),
    "design_patterns": list(range(16, 26)),
    "distributed_systems": list(range(26, 36)),
    "enterprise_business": list(range(36, 46)),
    "ai_ml": list(range(46, 56)),
    "iot_embedded": list(range(56, 66)),
    "gaming_media": list(range(66, 76)),
    "healthcare_education": list(range(76, 82)),
    "energy_transport": list(range(82, 86)),
}


def detect_levels(code: str) -> list:
    """Detect which AICL language levels are used in the code."""
    levels = []
    keywords_by_level = {
        1: ["Goal:", "Constraint:", "Risk:", "Recovery:", "Layer:", "SubLayer:", "Validation:"],
        2: ["Entity "],
        3: ["Behavior ", "Input:", "Output:", "Action:"],
        4: ["Condition:", "When ", "Then "],
        5: ["Event:", "On "],
        6: ["Parallel:"],
        7: ["Optimize:", "Priority:"],
        8: ["Learn:", "Adapt:", "Based:"],
        9: ["Security:", "Encrypt:", "Protect:"],
        10: ["Native:"],
    }
    for level, keywords in keywords_by_level.items():
        for kw in keywords:
            if kw in code:
                levels.append(level)
                break
    return sorted(levels)


def count_constructs(code: str) -> dict:
    """Count various AICL constructs in the code."""
    return {
        "goals": len(re.findall(r"^Goal:", code, re.MULTILINE)),
        "constraints": len(re.findall(r"^Constraint:", code, re.MULTILINE)),
        "risks": len(re.findall(r"^Risk:", code, re.MULTILINE)),
        "recoveries": len(re.findall(r"^Recovery:", code, re.MULTILINE)),
        "layers": len(re.findall(r"^Layer:", code, re.MULTILINE)),
        "sublayers": len(re.findall(r"^SubLayer:", code, re.MULTILINE)),
        "validations": len(re.findall(r"^Validation:", code, re.MULTILINE)),
        "entities": len(re.findall(r"^Entity ", code, re.MULTILINE)),
        "behaviors": len(re.findall(r"^Behavior ", code, re.MULTILINE)),
        "conditions": len(re.findall(r"^Condition:", code, re.MULTILINE)),
        "events": len(re.findall(r"^Event:", code, re.MULTILINE)),
        "parallels": len(re.findall(r"^Parallel:", code, re.MULTILINE)),
        "optimizes": len(re.findall(r"^Optimize:", code, re.MULTILINE)),
        "learns": len(re.findall(r"^Learn:", code, re.MULTILINE)),
        "adapts": len(re.findall(r"^Adapt:", code, re.MULTILINE)),
        "securities": len(re.findall(r"^Security:", code, re.MULTILINE)),
        "encrypts": len(re.findall(r"^Encrypt:", code, re.MULTILINE)),
        "protects": len(re.findall(r"^Protect:", code, re.MULTILINE)),
        "natives": len(re.findall(r"^Native:", code, re.MULTILINE)),
    }


def extract_native_language(code: str) -> str:
    """Extract the native code language if present."""
    match = re.search(r"^Native:\s*(\w+)", code, re.MULTILINE)
    return match.group(1) if match else ""


def extract_description(code: str) -> str:
    """Extract the description from comments at the top."""
    lines = code.strip().split("\n")
    comments = []
    for line in lines:
        if line.startswith("# "):
            comments.append(line[2:])
        elif line.startswith("#"):
            comments.append(line[1:].strip())
        else:
            break
    return " ".join(comments).strip()


def generate_task_prompt(domain: str, title: str) -> str:
    """Generate a natural language task prompt for the AICL code."""
    return f"Create an AICL specification for a {title.lower()}. Include all 10 language levels: architecture (goals, constraints, risks with recovery, layers), entities, behaviors, conditions, events, concurrency, optimization, learning, security, and native code."


def process_aicl_file(filepath: Path) -> dict:
    """Process a single .aicl file into a dataset entry."""
    code = filepath.read_text(encoding="utf-8")
    filename = filepath.name
    num_prefix = filename.split("_")[0]

    domain, title = DOMAIN_MAP.get(num_prefix, ("unknown", filename))
    levels = detect_levels(code)
    counts = count_constructs(code)
    native_lang = extract_native_language(code)
    description = extract_description(code)

    # Create instruction/completion pair for fine-tuning
    instruction = generate_task_prompt(domain, title)

    # Calculate complexity score
    complexity = (
        counts["entities"] * 3
        + counts["behaviors"] * 2
        + counts["conditions"] * 2
        + counts["events"] * 2
        + counts["risks"] * 2
        + counts["layers"] * 1
        + counts["validations"] * 1
        + len(levels) * 2
    )

    return {
        "id": f"aicl_{num_prefix.zfill(3)}",
        "filename": filename,
        "domain": domain,
        "title": title,
        "description": description,
        "instruction": instruction,
        "completion": code.strip(),
        "levels_used": levels,
        "native_language": native_lang,
        "complexity_score": complexity,
        "line_count": len(code.strip().split("\n")),
        "construct_counts": counts,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def generate_snippets(code: str, filename: str, domain: str) -> list:
    """Generate smaller training snippets from a full AICL program."""
    snippets = []

    # Extract individual level sections
    level_patterns = [
        ("architecture", r"((?:Goal:|Constraint:|Risk:|Recovery:|Layer:|SubLayer:|Validation:)[^\n]*(?:\n    [^\n]*)*)+"),
        ("entity", r"Entity \w+(?:\n    [^\n]+)+"),
        ("behavior", r"Behavior \w+(?:\n(?:    Input:|    Output:|    Action:)[^\n]*)+"),
        ("condition", r"Condition:\s*\n\nWhen [^\n]+\n\nThen [^\n]+"),
        ("event", r"Event:\s*\n\nOn [^\n]+\n\nAction:\s*[^\n]+"),
        ("concurrency", r"Parallel:\s*\n(?:[^\n]+\n)+"),
        ("optimization", r"Optimize: [^\n]+"),
        ("learning", r"Learn:\s*[^\n]+\n\nGoal:\s*[^\n]+"),
        ("security", r"Security:\s*\n(?:    (?:Encrypt:|Protect:)[^\n]+\n)+"),
        ("native", r"Native: \w+\s*\{[^}]+\}"),
    ]

    for section_type, pattern in level_patterns:
        matches = re.findall(pattern, code, re.MULTILINE)
        for i, match in enumerate(matches):
            if len(match.strip()) > 30:  # Skip very short matches
                snippets.append({
                    "id": f"snippet_{filename}_{section_type}_{i}",
                    "type": "snippet",
                    "section_type": section_type,
                    "domain": domain,
                    "instruction": f"Write the AICL {section_type} section for a {domain} system",
                    "completion": match.strip(),
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                })

    return snippets


def main():
    parser = argparse.ArgumentParser(description="Generate AICL training datasets from examples.")
    parser.add_argument("--examples-dir", type=Path, default=DEFAULT_EXAMPLES_DIR,
                        help="Directory containing .aicl example files (recursive)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DATASETS_DIR,
                        help="Directory to write JSONL datasets and manifest")
    args = parser.parse_args()

    examples_dir: Path = args.examples_dir
    datasets_dir: Path = args.output_dir
    output_jsonl: Path = datasets_dir / "aicl_mega_dataset.jsonl"
    output_manifest: Path = datasets_dir / "dataset_manifest.json"

    print("=" * 70)
    print("AICL Mega Dataset Generator v2.0")
    print("=" * 70)
    print(f"Examples dir: {examples_dir}")
    print(f"Output dir:   {datasets_dir}")

    # Ensure output directory exists
    datasets_dir.mkdir(parents=True, exist_ok=True)

    # Collect all .aicl files (recursive to include showcase/ and archive/)
    aicl_files = sorted(examples_dir.rglob("*.aicl"))
    print(f"\nFound {len(aicl_files)} AICL example files")

    all_entries = []
    all_snippets = []
    stats = {
        "total_files": 0,
        "total_entries": 0,
        "total_snippets": 0,
        "domains": {},
        "levels_coverage": {},
        "native_languages": {},
        "total_lines": 0,
        "avg_complexity": 0,
    }

    for filepath in aicl_files:
        print(f"  Processing: {filepath.name}")
        entry = process_aicl_file(filepath)
        all_entries.append(entry)
        stats["total_files"] += 1
        stats["total_lines"] += entry["line_count"]

        # Track domain stats
        domain = entry["domain"]
        stats["domains"][domain] = stats["domains"].get(domain, 0) + 1

        # Track level coverage
        for level in entry["levels_used"]:
            stats["levels_coverage"][str(level)] = stats["levels_coverage"].get(str(level), 0) + 1

        # Track native languages
        if entry["native_language"]:
            lang = entry["native_language"]
            stats["native_languages"][lang] = stats["native_languages"].get(lang, 0) + 1

        # Generate snippets
        snippets = generate_snippets(entry["completion"], filepath.name, domain)
        all_snippets.extend(snippets)

    stats["total_entries"] = len(all_entries)
    stats["total_snippets"] = len(all_snippets)
    if all_entries:
        stats["avg_complexity"] = sum(e["complexity_score"] for e in all_entries) / len(all_entries)

    # Write main dataset (full programs)
    print(f"\nWriting {len(all_entries)} full program entries to {output_jsonl}")
    with open(output_jsonl, "w", encoding="utf-8") as f:
        # First: full programs
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Then: snippets
        print(f"Writing {len(all_snippets)} snippet entries to {output_jsonl}")
        for snippet in all_snippets:
            f.write(json.dumps(snippet, ensure_ascii=False) + "\n")

    total_lines_written = len(all_entries) + len(all_snippets)
    print(f"Total JSONL entries: {total_lines_written}")

    # Write domain-specific splits
    for category, file_range in CATEGORY_GROUPS.items():
        category_file = datasets_dir / f"aicl_{category}.jsonl"
        count = 0
        with open(category_file, "w", encoding="utf-8") as f:
            for entry in all_entries:
                num_prefix = int(entry["filename"].split("_")[0])
                if num_prefix in file_range:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    count += 1
            # Also include relevant snippets
            for snippet in all_snippets:
                if snippet["domain"] in [DOMAIN_MAP.get(str(n).zfill(2), ("unknown", ""))[0] for n in file_range]:
                    f.write(json.dumps(snippet, ensure_ascii=False) + "\n")
                    count += 1
        print(f"  Category {category}: {count} entries -> {category_file}")

    # Write manifest
    manifest = {
        "name": "AICL Mega Training Dataset",
        "version": "2.0.0",
        "description": "Comprehensive AICL code dataset for AI training covering 85 programs across 16 domains with all 10 language levels",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "format": "JSONL",
        "files": {
            "main": str(output_jsonl.name),
            "categories": [f"aicl_{cat}.jsonl" for cat in CATEGORY_GROUPS.keys()],
        },
        "stats": stats,
        "domains": list(stats["domains"].keys()),
        "native_languages": list(stats["native_languages"].keys()),
        "category_splits": {k: f"aicl_{k}.jsonl" for k in CATEGORY_GROUPS.keys()},
        "schema": {
            "full_program": {
                "id": "string - unique identifier",
                "filename": "string - source .aicl file",
                "domain": "string - business domain category",
                "title": "string - program title",
                "description": "string - program description",
                "instruction": "string - task prompt for fine-tuning",
                "completion": "string - full AICL code",
                "levels_used": "list[int] - AICL levels present",
                "native_language": "string - native code language",
                "complexity_score": "int - weighted complexity metric",
                "line_count": "int - number of lines",
                "construct_counts": "dict - counts of each AICL construct",
                "generated_at": "string - ISO timestamp",
            },
            "snippet": {
                "id": "string - unique snippet identifier",
                "type": "string - always 'snippet'",
                "section_type": "string - AICL section type",
                "domain": "string - business domain",
                "instruction": "string - task prompt",
                "completion": "string - AICL code snippet",
                "generated_at": "string - ISO timestamp",
            },
        },
    }

    with open(output_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nManifest written to {output_manifest}")

    # Print summary
    print("\n" + "=" * 70)
    print("DATASET GENERATION COMPLETE")
    print("=" * 70)
    print(f"  Total AICL files:        {stats['total_files']}")
    print(f"  Full program entries:    {stats['total_entries']}")
    print(f"  Code snippet entries:    {stats['total_snippets']}")
    print(f"  Total JSONL entries:     {total_lines_written}")
    print(f"  Total lines of AICL:     {stats['total_lines']}")
    print(f"  Avg complexity score:    {stats['avg_complexity']:.1f}")
    print(f"  Domains covered:         {len(stats['domains'])}")
    print(f"  Native languages:        {list(stats['native_languages'].keys())}")
    print(f"  Level 1 coverage:        {stats['levels_coverage'].get('1', 0)} files")
    print(f"  Level 10 coverage:       {stats['levels_coverage'].get('10', 0)} files")
    print("=" * 70)


if __name__ == "__main__":
    main()
