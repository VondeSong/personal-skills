#!/usr/bin/env python3
"""Validate this pack's opaque color contracts; no third-party dependencies."""

import argparse
import json
import re
import sys
from pathlib import Path

HEX = re.compile(r"#[0-9a-fA-F]{6}")
KINDS = {"text", "indicator", "surface", "decorative"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def luminance(color):
    require(isinstance(color, str) and HEX.fullmatch(color),
            f"Expected opaque #RRGGBB color, got {color!r}")
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in channels]
    return sum(c * weight for c, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(foreground, background):
    a, b = luminance(foreground), luminance(background)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def validate(data):
    require(isinstance(data, dict), "Token file must be an object")
    require(data.get("format") == "apple-ui-design-tokens", "Unknown token format")
    require(data.get("version") == "3.0", "Expected token version 3.0")
    roles = data.get("colorRoles")
    require(isinstance(roles, dict) and roles, "colorRoles must be a nonempty object")
    require(all(isinstance(k, str) and isinstance(v, str) and v in KINDS
                for k, v in roles.items()), "Unknown color role kind")

    themes = {}
    overrides = data.get("highContrastOverrides")
    require(isinstance(overrides, dict) and set(overrides) == {"light", "dark"},
            "Provide light and dark highContrastOverrides")
    for mode in ("light", "dark"):
        palette = data.get(mode)
        require(isinstance(palette, dict) and set(palette) == set(roles),
                f"{mode}: palette keys must match colorRoles")
        override = overrides[mode]
        require(isinstance(override, dict) and set(override).issubset(roles),
                f"{mode}: unknown high-contrast role")
        themes[mode] = palette
        themes[f"{mode}-high-contrast"] = {**palette, **override}
    for mode, palette in themes.items():
        for role, value in palette.items():
            try:
                luminance(value)
            except ValueError as error:
                raise ValueError(f"{mode}.{role}: {error}") from error

    contracts = data.get("contrastContracts")
    require(isinstance(contracts, list) and contracts,
            "contrastContracts must be a nonempty list")
    pairs = []
    covered = set()
    seen_pairs = set()
    for contract in contracts:
        require(isinstance(contract, dict) and
                set(contract) == {"foreground", "backgrounds"},
                "Each contrast contract needs foreground and backgrounds")
        foreground = contract["foreground"]
        require(isinstance(foreground, str) and
                roles.get(foreground) in ("text", "indicator"),
                f"Contract foreground is not a text/indicator role: {foreground!r}")
        backgrounds = contract["backgrounds"]
        require(isinstance(backgrounds, list) and backgrounds,
                f"{foreground}: provide at least one background")
        for background in backgrounds:
            require(isinstance(background, str) and background in roles,
                    f"{foreground}: unknown background {background!r}")
            pair = (foreground, background)
            require(pair not in seen_pairs, f"Duplicate pair: {pair}")
            seen_pairs.add(pair)
            pairs.append(pair)
        covered.add(foreground)
    required = {role for role, kind in roles.items() if kind in ("text", "indicator")}
    require(covered == required,
            f"Missing foreground contrast coverage: {sorted(required - covered)}")

    material = data.get("webPreviewMaterial")
    require(isinstance(material, dict), "Missing webPreviewMaterial")
    for variant in ("regular", "clear"):
        spec = material.get(variant)
        require(isinstance(spec, dict), f"Missing preview material: {variant}")
        fallback = spec.get("opaqueFallbackRole")
        require(isinstance(fallback, str) and roles.get(fallback) == "surface",
                f"{variant}: opaqueFallbackRole must name a surface")
        for foreground in ("textPrimary", "textSecondary", "textTertiary"):
            require((foreground, fallback) in seen_pairs,
                    f"{variant}: fallback lacks contrast contract for {foreground}")

    results = []
    failures = []
    for mode, palette in themes.items():
        for foreground, background in pairs:
            kind = roles[foreground]
            threshold = 4.5 if kind == "text" else 3.0
            ratio = contrast(palette[foreground], palette[background])
            result = {"mode": mode, "foreground": foreground,
                      "background": background, "kind": kind,
                      "ratio": ratio, "minimum": threshold,
                      "passed": ratio >= threshold}
            results.append(result)
            if not result["passed"]:
                failures.append(result)
    return {
        "passed": not failures,
        "checks": len(results),
        "modes": list(themes),
        "failures": failures,
        "results": results,
        "limitations": "Opaque declared pairs only; translucent composition, runtime states, "
                       "input, text rendering, and native behavior require separate checks.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path,
                        default=Path(__file__).resolve().parent.parent / "TOKENS.json")
    parser.add_argument("--json", action="store_true", help="Print structured results")
    args = parser.parse_args()
    try:
        data = json.loads(args.path.read_text(encoding="utf-8-sig"),
                          object_pairs_hook=unique_object)
        result = validate(data)
    except (OSError, ValueError, TypeError) as error:
        result = {"passed": False, "error": str(error)}

    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    elif "error" in result:
        print(f"FAIL: {result['error']}")
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status}: {result['checks']} opaque contrast checks across "
              f"{len(result['modes'])} appearance modes")
        for mode in result["modes"]:
            rows = [r for r in result["results"] if r["mode"] == mode]
            minimum = min(r["ratio"] for r in rows if r["kind"] == "text")
            print(f"  {mode}: minimum ordinary-text contrast {minimum:.3f}:1")
        for failure in result["failures"]:
            print(f"  {failure['mode']}: {failure['foreground']} on "
                  f"{failure['background']} = {failure['ratio']:.3f}:1; "
                  f"requires {failure['minimum']}:1")
        print(result["limitations"])
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
