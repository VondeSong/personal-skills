# Reading a site without a browser

Fetch raw HTML and the stylesheets it links, then inspect their authored declarations. Markdown-converting fetches strip the evidence needed here. Work in a dedicated temporary directory, never in the user's project.

## Windows PowerShell

Use the URL named by the user. The commands below save raw HTML, list linked stylesheets and resolve their URLs against the final page URL, including a document `<base href>` when present.

```powershell
$taskUrl = 'https://example.com/' # Replace with the URL the user named.
$taskScratch = Join-Path $env:TEMP ('interface-source-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $taskScratch | Out-Null
$taskPage = Join-Path $taskScratch 'page.html'
$taskResponse = Invoke-WebRequest -Uri $taskUrl -TimeoutSec 25
[IO.File]::WriteAllText($taskPage, [string]$taskResponse.Content, [Text.UTF8Encoding]::new($false))
Get-Item -LiteralPath $taskPage | Select-Object Length
$taskFinal = if ($taskResponse.BaseResponse.RequestMessage) { $taskResponse.BaseResponse.RequestMessage.RequestUri } else { $taskResponse.BaseResponse.ResponseUri }
$taskBase = [uri]$taskFinal
$taskBaseMatch = [regex]::Match($taskResponse.Content, '<base\b[^>]*href=["'']([^"'']+)["'']', 'IgnoreCase')
if ($taskBaseMatch.Success) { $taskBase = [uri]::new($taskBase, [Net.WebUtility]::HtmlDecode($taskBaseMatch.Groups[1].Value)) }
$taskCssUrls = foreach ($taskLink in [regex]::Matches($taskResponse.Content, '<link\b[^>]*>', 'IgnoreCase')) {
    if ($taskLink.Value -notmatch 'rel=["''][^"'']*\bstylesheet\b') { continue }
    $taskHref = [regex]::Match($taskLink.Value, 'href=["'']([^"'']+)["'']', 'IgnoreCase')
    if ($taskHref.Success) { [uri]::new($taskBase, [Net.WebUtility]::HtmlDecode($taskHref.Groups[1].Value)).AbsoluteUri }
}
$taskCssUrls | Sort-Object -Unique
```

For complex or malformed markup, use an available HTML parser rather than widening these regexes. Fetch the relevant linked stylesheets with `Invoke-WebRequest -TimeoutSec 25 -OutFile`, assigning each a distinct filename in `$taskScratch`. Use `rg -o` for extraction, `Sort-Object -Unique` for deduplication, `Group-Object` for counts and `Select-Object -First` for bounded output.

The POSIX snippets below illustrate patterns. Run them only in an available POSIX shell; on Windows, translate the operations into the PowerShell equivalents above. Do not assume `mktemp`, `grep`, `sed`, `wc` or `curl` shell behavior.

## Utility CSS is self-describing

Where the site uses utility classes, the markup already contains the declarations and no stylesheet lookup is needed. Grep the class attribute for the effect:

```bash
grep -oE '(backdrop-)?blur-\[[^]]*\]|(backdrop-)?blur-[a-z0-9]+' page.html | sort | uniq -c | sort -rn
grep -oE 'class="[^"]*(gradient|blur|mask|mix-blend)[^"]*"' page.html | head -20
```

A class list carries every responsive and state variant at once. `blur-[50px] md:h-214 md:-translate-x-1/2` says the element changes shape at the `md` breakpoint.

Semantic CSS gives you a hashed class name instead, such as `Hero_glow__a1b2c`. Take that name to the stylesheet and grep it there.

## Inline styles carry the values utilities cannot express

A multi-stop gradient is usually too specific for a utility, so it lands in a `style` attribute:

```bash
grep -oE 'linear-gradient\([^)]*\)' page.html | sort -u | head
grep -oE 'radial-gradient\([^)]*\)' page.html | sort -u | head
grep -oE 'style="[^"]*(transform|filter|mask)[^"]*"' page.html | head
```

## The stylesheet, for tokens and generated utilities

```bash
grep -oE '(:root|:host)[^{]*\{[^}]*\}' style.css | head -3 | tr ';' '\n'   # the token layer
grep -oE '@layer [a-z, ]+' style.css | sort -u                             # Tailwind v4 emits theme, base, components, utilities
grep -oE '@media[^{]*\((m(in|ax)-width:|width *[<>])[^)]*\)' style.css | sort -u   # real breakpoints
grep -oE '@font-face\{[^}]*\}' style.css | head                           # families, weights, formats
grep -oE '@keyframes [a-zA-Z-]+' style.css | sort -u                      # named animations
```

To understand a custom utility, grep its class name in the stylesheet and read the declaration whole. That is how `gradient-ease-in-out` turns into its mechanism, a generated stop list built with `color-mix()` and relative color syntax.

## Stack fingerprints from the HTML alone

```bash
grep -ocE '__NEXT_DATA__|/_next/static' page.html          # Next.js
grep -oc 'self.__next_f' page.html                          # App Router with RSC payload
grep -ocE '__NUXT__|/_nuxt/' page.html                      # Nuxt
grep -ocE '__remixContext|___gatsby|astro-island' page.html  # Remix, Gatsby, Astro
grep -oc 'class="[^"]*svelte-' page.html                     # Svelte
grep -oc 'data-radix-' page.html                             # Radix primitives
grep -oc 'bg-linear-to' page.html                            # Tailwind v4, where v3 wrote bg-gradient-to
grep -oE '<meta name="generator"[^>]*>' page.html
```

## What this method cannot tell you

Say so rather than guessing past it:

- **Paint order and what is actually visible.** A declaration in the CSS may be overridden or never rendered.
- **Live animation state.** Whether an effect moves at all.
- **Resolved values.** A `rem` stays a `rem`, and you never learn the pixel size.
