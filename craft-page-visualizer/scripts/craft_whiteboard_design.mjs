/**
 * Deterministic Craft Whiteboard / Excalidraw design helpers.
 *
 * This module only renders elements in memory. Submit its output with
 * craft_whiteboard_write.mjs so creation, ordering and verification remain
 * separate from visual composition.
 */

export const APPLE_EDITORIAL_TOKENS = Object.freeze({
  grid: 8,
  color: Object.freeze({
    ink: "#1C1C1E",
    text: "#34343A",
    muted: "#636366",
    subtle: "#8E8E93",
    border: "#C7C7CC",
    borderSoft: "#D9D9DE",
    surface: "#FFFFFF",
    surfaceSoft: "#F2F2F5",
    primary: "#0A66FF",
    primaryDark: "#0048B5",
    primarySoft: "#EAF2FF",
    primaryBorder: "#96BFFF",
    success: "#2EAD4A",
    successDark: "#176B2C",
    successSoft: "#ECF9EF",
    successBorder: "#9DDBAA",
    warning: "#F59E0B",
    warningDark: "#8A4B00",
    warningSoft: "#FFF3D6",
    warningBorder: "#F3C66D",
    danger: "#FF3B30",
    dangerDark: "#A6221A",
    dangerSoft: "#FFF0EE",
    dangerBorder: "#FFB4AE",
    purple: "#9B51E0",
    purpleDark: "#6427A6",
    purpleSoft: "#F3EAFE",
    purpleBorder: "#CDB2EA",
  }),
  type: Object.freeze({
    boardTitle: 42,
    boardSubtitle: 20,
    section: 22,
    heroTitle: 28,
    cardTitle: 24,
    cardSummary: 18,
    chip: 16,
  }),
  card: Object.freeze({
    width: 480,
    minWidth: 320,
    maxWidth: 760,
    minHeight: 128,
    paddingX: 24,
    paddingY: 20,
    accentWidth: 4,
    chipHeight: 28,
    radiusType: 3,
  }),
});

// Backward-compatible name. The default professional profile is now the
// quieter Apple-inspired editorial profile.
export const PROFESSIONAL_TOKENS = APPLE_EDITORIAL_TOKENS;

const VARIANTS = Object.freeze({
  hero: {
    background: "primarySoft",
    border: "primary",
    accent: "primary",
    title: "primaryDark",
    summary: "text",
    titleSize: "heroTitle",
    strokeWidth: 2,
    showAccent: true,
    chipStyle: "text",
    tone: "primary",
    tinted: true,
  },
  standard: {
    background: "surface",
    border: "border",
    accent: "primary",
    title: "ink",
    summary: "text",
    titleSize: "cardTitle",
    strokeWidth: 1,
    showAccent: false,
    chipStyle: "text",
    tone: "primary",
    tinted: false,
  },
  milestone: {
    background: "surface",
    border: "border",
    accent: "primary",
    title: "ink",
    summary: "text",
    titleSize: "cardTitle",
    strokeWidth: 1,
    showAccent: false,
    chipStyle: "text",
    tone: "primary",
    tinted: false,
  },
  risk: {
    background: "warningSoft",
    border: "warning",
    accent: "warning",
    title: "warningDark",
    summary: "text",
    titleSize: "cardTitle",
    strokeWidth: 1,
    showAccent: true,
    chipStyle: "text",
    tone: "warning",
    tinted: true,
  },
  conclusion: {
    background: "successSoft",
    border: "success",
    accent: "success",
    title: "successDark",
    summary: "text",
    titleSize: "cardTitle",
    strokeWidth: 1,
    showAccent: false,
    chipStyle: "text",
    tone: "success",
    tinted: true,
  },
  muted: {
    background: "surfaceSoft",
    border: "borderSoft",
    accent: "subtle",
    title: "text",
    summary: "muted",
    titleSize: "cardTitle",
    strokeWidth: 1,
    showAccent: false,
    chipStyle: "text",
    tone: "neutral",
    tinted: true,
  },
});

const TONES = Object.freeze({
  neutral: { base: "subtle", dark: "text", soft: "surfaceSoft", border: "borderSoft" },
  primary: { base: "primary", dark: "primaryDark", soft: "primarySoft", border: "primaryBorder" },
  success: { base: "success", dark: "successDark", soft: "successSoft", border: "successBorder" },
  warning: { base: "warning", dark: "warningDark", soft: "warningSoft", border: "warningBorder" },
  danger: { base: "danger", dark: "dangerDark", soft: "dangerSoft", border: "dangerBorder" },
  purple: { base: "purple", dark: "purpleDark", soft: "purpleSoft", border: "purpleBorder" },
});

export function createWhiteboardDesign({
  runId,
  seedBase = 100000,
  tokens = PROFESSIONAL_TOKENS,
} = {}) {
  if (!runId || !/^[a-zA-Z0-9_-]+$/.test(runId)) {
    throw new Error("runId is required and may contain only letters, digits, _ and -");
  }

  const elements = [];
  const cards = [];
  const designWarnings = [];
  let serial = 0;

  const color = (value) => tokens.color[value] || PROFESSIONAL_TOKENS.color[value] || value;
  const semanticDark = (value) => color(TONES[value]?.dark || value);
  const fontSize = (value) => tokens.type[value] || value;
  const snap = (value) => Math.round(value / tokens.grid) * tokens.grid;

  function common(id, type, x, y, width, height, overrides = {}) {
    serial += 1;
    return {
      id: `viz-${runId}-${id}`,
      type,
      x: snap(x),
      y: snap(y),
      width: snap(width),
      height: snap(height),
      angle: 0,
      strokeColor: tokens.color.text,
      backgroundColor: "transparent",
      fillStyle: "solid",
      strokeWidth: 2,
      strokeStyle: "solid",
      roughness: 0,
      opacity: 100,
      seed: seedBase + serial,
      version: 1,
      versionNonce: seedBase + 10000 + serial,
      updated: 0,
      isDeleted: false,
      groupIds: [],
      frameId: null,
      roundness: type === "rectangle" ? { type: tokens.card.radiusType } : null,
      boundElements: [],
      link: null,
      locked: false,
      ...overrides,
    };
  }

  function rectangle({ id, x, y, width, height, ...style }) {
    const element = common(id, "rectangle", x, y, width, height, {
      ...style,
      strokeColor: color(style.strokeColor || "border"),
      backgroundColor: color(style.backgroundColor || "surface"),
    });
    elements.push(element);
    return element;
  }

  function text({
    id,
    value,
    x,
    y,
    width,
    height,
    fontSize: size = "cardSummary",
    strokeColor = "text",
    textAlign = "left",
    verticalAlign = "middle",
    lineHeight = 1.25,
    ...style
  }) {
    if (!String(value || "").trim()) throw new Error(`${id}: text value is empty`);
    const element = common(id, "text", x, y, width, height, {
      strokeColor: color(strokeColor),
      backgroundColor: "transparent",
      strokeWidth: 1,
      text: String(value),
      originalText: String(value),
      fontSize: fontSize(size),
      fontFamily: 1,
      textAlign,
      verticalAlign,
      lineHeight,
      autoResize: false,
      containerId: null,
      ...style,
    });
    elements.push(element);
    return element;
  }

  function arrow({
    id,
    points,
    strokeColor = "muted",
    strokeWidth = 2,
    strokeStyle = "solid",
    endArrowhead = "arrow",
  }) {
    if (!Array.isArray(points) || points.length < 2) throw new Error(`${id}: arrow needs at least two points`);
    const xs = points.map(([x]) => x);
    const ys = points.map(([, y]) => y);
    const minX = Math.min(...xs);
    const minY = Math.min(...ys);
    const maxX = Math.max(...xs);
    const maxY = Math.max(...ys);
    const localPoints = points.map(([x, y]) => [snap(x - minX), snap(y - minY)]);
    const element = common(id, "arrow", minX, minY, maxX - minX, maxY - minY, {
      strokeColor: color(strokeColor),
      backgroundColor: "transparent",
      strokeWidth,
      strokeStyle,
      points: localPoints,
      lastCommittedPoint: null,
      startBinding: null,
      endBinding: null,
      startArrowhead: null,
      endArrowhead,
    });
    elements.push(element);
    return element;
  }

  function card({
    id,
    x,
    y,
    width = tokens.card.width,
    variant = "standard",
    eyebrow,
    title: titleValue,
    summary,
    accentColor,
    tone,
    tinted,
    showAccent,
    chipStyle,
    link = null,
  }) {
    if (!VARIANTS[variant]) throw new Error(`${id}: unknown card variant ${variant}`);
    if (!String(titleValue || "").trim()) throw new Error(`${id}: card title is required`);

    const style = VARIANTS[variant];
    const resolvedToneName = tone || style.tone;
    const toneStyle = TONES[resolvedToneName];
    if (!toneStyle) throw new Error(`${id}: unknown card tone ${resolvedToneName}`);
    width = snap(clamp(width, tokens.card.minWidth, tokens.card.maxWidth));
    const resolvedShowAccent = showAccent ?? style.showAccent;
    const resolvedChipStyle = chipStyle || style.chipStyle || "text";
    const innerX = snap(x + tokens.card.paddingX + (resolvedShowAccent ? tokens.card.accentWidth + 8 : 0));
    const innerWidth = snap(width - (innerX - x) - tokens.card.paddingX);
    const titleSize = fontSize(style.titleSize);
    const summarySize = fontSize("cardSummary");
    const titleLayout = wrapText(String(titleValue), {
      width: innerWidth,
      fontSize: titleSize,
      maxLines: variant === "hero" ? 2 : 2,
    });
    const summaryLayout = summary ? wrapText(String(summary), {
      width: innerWidth,
      fontSize: summarySize,
      maxLines: 3,
    }) : null;

    if (titleLayout.truncated) designWarnings.push(`${id}: title was truncated to two lines`);
    if (summaryLayout?.truncated) designWarnings.push(`${id}: summary was truncated to three lines`);

    const chipBlock = eyebrow ? tokens.card.chipHeight + 8 : 0;
    const titleHeight = snap(titleLayout.lines.length * titleSize * 1.25);
    const summaryHeight = summaryLayout ? snap(summaryLayout.lines.length * summarySize * 1.35) : 0;
    const summaryGap = summaryLayout ? 12 : 0;
    const height = snap(Math.max(
      tokens.card.minHeight,
      tokens.card.paddingY * 2 + chipBlock + titleHeight + summaryGap + summaryHeight,
    ));

    const resolvedTinted = tinted ?? style.tinted;
    const resolvedAccent = color(accentColor || toneStyle.base || style.accent);
    const background = color(resolvedTinted ? toneStyle.soft : style.background);
    const border = color(resolvedTinted ? toneStyle.border : style.border);
    const titleColor = color(resolvedTinted || resolvedShowAccent ? toneStyle.dark : style.title);
    const summaryColor = color(style.summary);

    const backgroundElement = rectangle({
      id: `${id}-surface`, x, y, width, height,
      strokeColor: border,
      backgroundColor: background,
      strokeWidth: style.strokeWidth,
      link,
    });
    if (resolvedShowAccent) {
      rectangle({
        id: `${id}-accent`, x: x + 8, y: y + 16,
        width: tokens.card.accentWidth, height: height - 32,
        strokeColor: resolvedAccent,
        backgroundColor: resolvedAccent,
        strokeWidth: 1,
        opacity: 82,
      });
    }

    let cursorY = snap(y + tokens.card.paddingY);
    if (eyebrow) {
      const chipLayout = wrapText(String(eyebrow), {
        width: Math.min(innerWidth, 180),
        fontSize: fontSize("chip"),
        maxLines: 1,
      });
      const chipWidth = snap(clamp(chipLayout.units * fontSize("chip") * 0.62 + 16, 56, 190));
      if (resolvedChipStyle === "tinted") {
        rectangle({
          id: `${id}-chip`, x: innerX, y: cursorY,
          width: chipWidth, height: tokens.card.chipHeight,
          strokeColor: "borderSoft",
          backgroundColor: variant === "milestone" ? "primarySoft" : background,
          strokeWidth: 1,
        });
      }
      text({
        id: `${id}-chip-text`, value: chipLayout.text,
        x: innerX, y: cursorY,
        width: chipWidth, height: tokens.card.chipHeight,
        fontSize: "chip", strokeColor: resolvedAccent, textAlign: "left",
      });
      cursorY += tokens.card.chipHeight + 8;
    }

    text({
      id: `${id}-title`, value: titleLayout.text,
      x: innerX, y: cursorY, width: innerWidth, height: titleHeight,
      fontSize: titleSize, strokeColor: titleColor,
    });
    cursorY += titleHeight;

    if (summaryLayout) {
      cursorY += summaryGap;
      text({
        id: `${id}-summary`, value: summaryLayout.text,
        x: innerX, y: cursorY, width: innerWidth, height: summaryHeight,
        fontSize: summarySize, strokeColor: summaryColor, lineHeight: 1.35,
      });
    }

    const result = {
      id,
      x: backgroundElement.x,
      y: backgroundElement.y,
      width: backgroundElement.width,
      height: backgroundElement.height,
      variant,
      tone: resolvedToneName,
      tinted: resolvedTinted,
      accentColor: resolvedAccent,
      anchors: {
        top: [backgroundElement.x + backgroundElement.width / 2, backgroundElement.y],
        right: [backgroundElement.x + backgroundElement.width, backgroundElement.y + backgroundElement.height / 2],
        bottom: [backgroundElement.x + backgroundElement.width / 2, backgroundElement.y + backgroundElement.height],
        left: [backgroundElement.x, backgroundElement.y + backgroundElement.height / 2],
      },
    };
    cards.push(result);
    return result;
  }

  function boardTitle({ id = "board-title", title: titleValue, subtitle, x, y, width }) {
    const titleLayout = wrapText(titleValue, { width: width - 64, fontSize: tokens.type.boardTitle, maxLines: 2 });
    const titleHeight = snap(titleLayout.lines.length * tokens.type.boardTitle * 1.2);
    const subtitleLayout = subtitle ? wrapText(subtitle, { width: width - 64, fontSize: tokens.type.boardSubtitle, maxLines: 2 }) : null;
    const subtitleHeight = subtitleLayout ? snap(subtitleLayout.lines.length * tokens.type.boardSubtitle * 1.3) : 0;
    const height = snap(48 + titleHeight + (subtitleLayout ? 12 + subtitleHeight : 0));
    rectangle({
      id: `${id}-surface`, x: x + width / 2 - 80, y: y + height - 8, width: 160, height: 8,
      strokeColor: "primary", backgroundColor: "primary", strokeWidth: 1,
      roundness: null,
    });
    text({
      id: `${id}-text`, value: titleLayout.text,
      x: x + 32, y: y + 20, width: width - 64, height: titleHeight,
      fontSize: "boardTitle", strokeColor: "ink", textAlign: "center",
    });
    if (subtitleLayout) {
      text({
        id: `${id}-subtitle`, value: subtitleLayout.text,
        x: x + 32, y: y + 28 + titleHeight,
        width: width - 64, height: subtitleHeight,
        fontSize: "boardSubtitle", strokeColor: "muted", textAlign: "center",
      });
    }
    return { x: snap(x), y: snap(y), width: snap(width), height };
  }

  function section({ id, label, detail, x, y, width, accentColor = "primary" }) {
    rectangle({
      id: `${id}-band`, x, y: y + 60, width, height: 8,
      strokeColor: "borderSoft", backgroundColor: "borderSoft", strokeWidth: 1,
      roundness: null,
    });
    rectangle({
      id: `${id}-accent`, x: x + 8, y: y + 18, width: 6, height: 28,
      strokeColor: accentColor, backgroundColor: accentColor, strokeWidth: 1, opacity: 100,
    });
    text({
      id: `${id}-label`, value: label,
      x: x + 30, y: y + 8, width: Math.min(420, width * 0.35), height: 48,
      fontSize: "section", strokeColor: semanticDark(accentColor),
    });
    if (detail) {
      text({
        id: `${id}-detail`, value: detail,
        x: x + Math.min(460, width * 0.4), y: y + 10,
        width: width - Math.min(480, width * 0.42), height: 44,
        fontSize: "cardSummary", strokeColor: "muted",
      });
    }
    return { x: snap(x), y: snap(y), width: snap(width), height: 64 };
  }

  function audit() {
    const errors = [];
    const warnings = [...designWarnings];
    const ids = new Set();
    for (const element of elements) {
      if (ids.has(element.id)) errors.push(`duplicate element id: ${element.id}`);
      ids.add(element.id);
      for (const key of ["x", "y", "width", "height"]) {
        if (!Number.isFinite(element[key])) errors.push(`${element.id}.${key} is not finite`);
      }
      if (element.type === "text" && element.fontSize < 16) warnings.push(`${element.id}: font size below 16`);
    }

    for (let i = 0; i < cards.length; i += 1) {
      for (let j = i + 1; j < cards.length; j += 1) {
        if (overlapArea(cards[i], cards[j]) > 0) {
          errors.push(`cards overlap: ${cards[i].id} and ${cards[j].id}`);
        }
      }
    }

    const bounds = calculateBounds(elements);
    const semanticAccents = new Set(cards.filter((card) => card.tone !== "neutral").map((card) => card.accentColor));
    if (semanticAccents.size > 4) warnings.push(`${semanticAccents.size} semantic accent colors exceed the recommended maximum of four`);
    const nonNeutralFills = new Set(elements
      .filter((element) => element.type === "rectangle")
      .map((element) => element.backgroundColor)
      .filter((value) => value && !["transparent", tokens.color.surface, tokens.color.surfaceSoft].includes(value)));

    return {
      ok: errors.length === 0,
      errors,
      warnings: [...new Set(warnings)],
      stats: {
        elementCount: elements.length,
        cardCount: cards.length,
        semanticAccentCount: semanticAccents.size,
        nonNeutralFillCount: nonNeutralFills.size,
        bounds,
      },
    };
  }

  return {
    tokens,
    elements,
    cards,
    snap,
    rectangle,
    text,
    arrow,
    card,
    boardTitle,
    section,
    audit,
    toJSON: () => ({ elements }),
  };
}

export function wrapText(value, { width, fontSize, maxLines = 3, ellipsis = true }) {
  const text = String(value || "").trim();
  const capacity = Math.max(1, width / fontSize);
  const lines = [];
  let current = "";
  let units = 0;
  let truncated = false;

  for (const paragraph of text.split(/\r?\n/)) {
    if (lines.length >= maxLines) { truncated = true; break; }
    current = "";
    units = 0;
    for (const char of paragraph) {
      const next = glyphUnits(char);
      if (current && units + next > capacity) {
        lines.push(current.trimEnd());
        current = "";
        units = 0;
        if (lines.length >= maxLines) { truncated = true; break; }
      }
      current += char;
      units += next;
    }
    if (truncated) break;
    if (current || paragraph === "") lines.push(current.trimEnd());
  }

  if (lines.length > maxLines) {
    lines.length = maxLines;
    truncated = true;
  }
  if (truncated && ellipsis && lines.length) {
    const last = lines.length - 1;
    lines[last] = `${lines[last].replace(/[，。；、,.!?！？：:\s]+$/u, "")}…`;
  }
  return {
    text: lines.join("\n"),
    lines,
    lineCount: lines.length,
    truncated,
    units: textUnits(text),
  };
}

export function orthogonalPoints(from, to, { first = "horizontal", midpoint } = {}) {
  const [x1, y1] = from;
  const [x2, y2] = to;
  if (x1 === x2 || y1 === y2) return [[x1, y1], [x2, y2]];
  if (first === "vertical") {
    const midY = midpoint ?? (y1 + y2) / 2;
    return [[x1, y1], [x1, midY], [x2, midY], [x2, y2]];
  }
  const midX = midpoint ?? (x1 + x2) / 2;
  return [[x1, y1], [midX, y1], [midX, y2], [x2, y2]];
}

function glyphUnits(char) {
  if (/\s/u.test(char)) return 0.35;
  if (/[ -ÿ]/u.test(char)) return /[A-Z0-9]/u.test(char) ? 0.62 : 0.52;
  return 1;
}

function textUnits(value) {
  return [...String(value)].reduce((sum, char) => sum + glyphUnits(char), 0);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function overlapArea(a, b) {
  const width = Math.max(0, Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x));
  const height = Math.max(0, Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y));
  return width * height;
}

function calculateBounds(elements) {
  if (!elements.length) return null;
  return elements.reduce((bounds, element) => ({
    minX: Math.min(bounds.minX, element.x),
    minY: Math.min(bounds.minY, element.y),
    maxX: Math.max(bounds.maxX, element.x + element.width),
    maxY: Math.max(bounds.maxY, element.y + element.height),
  }), { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity });
}
