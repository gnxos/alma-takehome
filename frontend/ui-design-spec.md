# UI Design Specification — Lead Management System

This document is the single source of truth for visual and interaction design.
Hand this file directly to Claude Code alongside the system design doc — it
contains everything needed to build both surfaces (public intake form,
internal attorney dashboard) without further design decisions.

---

## 0. Grounding the design

**Subject:** a law firm's case-intake pipeline. A prospect submits their
information and CV for evaluation; an attorney reviews it and marks when
they've made contact. Two audiences, two moods:

- **Public form** — a stranger, once, deciding whether to trust this firm
  with their case. Should feel considered and calm, like a well-typeset
  letterhead — not a generic SaaS signup screen.
- **Internal dashboard** — an attorney doing this dozens of times a day.
  Should feel like an efficient operational tool — dense, fast, no ceremony.

The same tokens power both, but the two surfaces should not look
interchangeable. The form is the firm's front door; the dashboard is a work
tool.

### 0.1 Reference: tryalma.com

You asked me to pull the design system from [tryalma.com](https://www.tryalma.com)
— Alma, a modern immigration law firm with the same shape of business as
ours (attorneys, cases, prospects, milestones). Being direct about what I
could and couldn't get: my fetch tool reads a page's content and structure,
not its rendered CSS or fonts, and it can't screenshot the live site — so I
have real, sourced UI *patterns* and copy below, but not verified hex codes
or exact typefaces. If pixel-exact fidelity to Alma matters to you, the
fastest path is to screenshot the site yourself and drop the image into
Claude Code directly — it can read colors and fonts straight off a screenshot
in a way I can't from here.

What I *did* confirm directly from the live page, and have folded into the
sections below:

- **A prospect-facing case list with status pills** — Alma's homepage shows
  a live "Active cases" table: Name / Status / Current Milestone, with
  status values like *In Progress*, *In Review*, *Approved*. This is
  functionally the same object as our lead table, and it validates the
  pill-badge approach already in §5.2 — I've adopted the summary-stat-row
  pattern below (§5.0) directly from this.
- **A step-by-step case timeline** — checkmarked completed steps, a filled
  dot for the current step, numbered upcoming steps, each labeled with a
  day count ("Day 1," "Day 4," "Day 9"...). I've added this as an optional
  richer alternative to a flat badge in §6.1.
- **Stat highlight cards** — big number, short label, one-line caption in
  smaller muted text (e.g. "98%+ / Approval / Approval rates across
  hundreds of cases"). Same treatment proposed for the dashboard header in
  §5.0.
- **Plain, short submission microcopy** — Alma's own form confirms with
  "Thank you! Your submission has been received!" and fails with "Oops!
  Something went wrong while submitting the form." Confirms the tone
  already specified in §3.4/§3.5 — direct, no corporate padding.
- **An explicit consent line under the submit action** — "By clicking
  'Sign Up,' you agree to our Terms of Service." Added to our form in §3.1.
- **Editorial-calm visual register overall**: confident, declarative
  headlines ("Stop managing immigration," "Cases that keep moving"), a
  restrained neutral palette carrying most of the page, and color spent
  only on status signaling — not decoration. This validates the direction
  already in §1 (a quiet neutral base, one primary, one signature accent,
  color reserved for state) rather than requiring a rework of the token
  system itself.

---

## 1. Design tokens

### 1.1 Color

| Token | Hex | Use |
|---|---|---|
| `ink-900` | `#12151C` | Primary text, headings |
| `ink-700` | `#3A3F4B` | Secondary text |
| `ink-400` | `#7A7F8C` | Placeholder, disabled text |
| `ink-200` | `#D8D9DE` | Borders, dividers |
| `paper-0` | `#FFFFFF` | Cards, inputs |
| `paper-50` | `#F7F6F3` | Page background (warm, not cream — cooler/greyer than a typical off-white) |
| `paper-100` | `#EFEDE8` | Section backgrounds, hover fills |
| `navy-600` | `#1F3A5F` | Primary brand / primary actions |
| `navy-700` | `#16283F` | Primary hover/active |
| `brass-500` | `#8A6D3B` | Signature accent — used sparingly (docket numbers, dividers, the "reached out" stamp) |
| `sage-600` | `#4B6350` | Success / REACHED_OUT state |
| `sage-50` | `#EEF2ED` | Success background |
| `ochre-600` | `#A9762F` | Pending / warning state |
| `ochre-50` | `#FAF3E7` | Pending background |
| `brick-600` | `#9B3A2E` | Error / destructive |
| `brick-50` | `#FBEEEC` | Error background |

Do **not** introduce a generic blue (`#2563EB`-style) or terracotta/cream
combination — `navy-600` is the only primary blue and `brass-500` is the only
warm accent, each used deliberately, not interchangeably.

### 1.2 Typography

Two type roles, not one neutral sans everywhere:

- **Display serif** — `"Source Serif 4"` or `"Newsreader"` (fallback:
  `Georgia, serif`). Used only on the public form: the page title, the
  docket/reference number, and the confirmation headline. Nowhere in the
  internal dashboard.
- **UI sans** — `"Inter"` (fallback: `system-ui, sans-serif`). Used for all
  body copy, form labels, inputs, buttons, and the entire internal
  dashboard.

Type scale (applies to both, via the sans unless noted):

| Token | Size / Line height | Weight | Use |
|---|---|---|---|
| `display-lg` | 40px / 1.15 (serif) | 500 | Public form page title |
| `display-md` | 28px / 1.2 (serif) | 500 | Confirmation screen headline |
| `heading-lg` | 22px / 1.3 | 600 | Dashboard page title, drawer title |
| `heading-md` | 17px / 1.4 | 600 | Card/section headers |
| `body-md` | 15px / 1.6 | 400 | Default body text, table cells |
| `body-sm` | 13px / 1.5 | 400 | Helper text, timestamps, captions |
| `label-sm` | 12px / 1.3, uppercase, tracking 0.04em | 600 | Form field labels, table column headers |
| `mono-sm` | 13px / 1.4, `"IBM Plex Mono"` fallback `monospace` | 500 | Reference/docket numbers, email addresses in tables |

### 1.3 Spacing, radius, shadow

- Spacing scale (px): `4, 8, 12, 16, 24, 32, 48, 64` — no arbitrary values.
- Radius: `6px` (inputs, buttons), `10px` (cards), `999px` (badges/pills).
  Deliberately **not** zero-radius (that reads as the broadsheet-cliché
  direction) and not the heavy `16px+` rounded-everything SaaS look either.
- Shadow: only two, used sparingly —
  `shadow-card: 0 1px 3px rgba(18,21,28,0.06), 0 1px 2px rgba(18,21,28,0.04)`
  `shadow-modal: 0 12px 32px rgba(18,21,28,0.18)`
  Flat surfaces (table rows, page background) get no shadow at all.

### 1.4 Signature element

**The docket number.** The public form generates a reference number the
moment the page loads (`INT-2026-0842` style — year + sequential/random
4-digit), printed in `mono-sm` + `brass-500` beneath the page title, the way
a law firm stamps a file the moment it's opened. This same reference number
reappears in the confirmation screen and, later, in the internal dashboard's
lead detail view — giving prospect and attorney a shared, concrete anchor
for the same case. It is the one ornamental flourish in the whole system;
everything else stays quiet.

---

## 2. Layout system

- Container max-width: `680px` for the public form (reads like a document,
  not a dashboard), `1280px` for the internal dashboard.
- Breakpoints: `sm 640px`, `md 768px`, `lg 1024px`, `xl 1280px`.
- Public form: single column, generous vertical rhythm (`32px` between
  field groups), centered on `paper-50` background.
- Dashboard: fixed left-aligned content, no centering — table should use the
  full width down to `lg`, then stack to cards below `md`.

### 2.1 Responsive strategy

Every page in this system is built mobile-first: base styles target the
smallest viewport, then `min-width` media queries (or Tailwind's default
`sm:`/`md:`/`lg:`/`xl:` prefixes) layer on desktop refinements. Nothing in
this spec should be built desktop-first and then squeezed down — that's
how form fields end up too small to tap and tables end up horizontally
scrolling on a phone.

Three viewport bands to design and test against, used consistently across
every page below:

| Band | Width | Primary device | What changes |
|---|---|---|---|
| **Compact** | `<640px` | Phone | Single column everywhere, full-width controls, stacked cards instead of tables, `16–20px` container padding |
| **Regular** | `640–1023px` | Tablet, small laptop | Form stays single column but gains breathing room; dashboard table becomes viable but tighter than desktop |
| **Wide** | `≥1024px` | Desktop | Full layouts as described in each page's default spec |

General rules that apply everywhere, not just on one page:

- **Touch targets**: every tappable element (buttons, inputs, table rows,
  badges that are clickable, the file dropzone) is at least `44×44px` on
  Compact and Regular, even if the visual element looks smaller — pad the
  hit area, don't shrink the target.
- **No horizontal scroll, ever**, on any page at any width. If content
  doesn't fit, it restacks or truncates — it doesn't cause the viewport to
  scroll sideways. The one sanctioned exception is a deliberately
  horizontally-scrollable table on Regular width only (§5.4), and even
  that must show a visual affordance (edge fade) that it scrolls.
- **Font sizes never shrink below `body-sm` (13px)** at any breakpoint —
  scale layout and spacing down, not text past that floor.
- **Test at 375px width minimum** (a small phone, e.g. iPhone SE) as the
  hard lower bound; nothing should clip or overlap at that width.

---

## 3. Page: Public Lead Intake Form

**Route:** `/apply` · **Auth:** none · **Goal:** one clear action — submit.

### 3.1 Structure (top to bottom)

1. **Header band** (`paper-100` background, `24px` vertical padding)
   - Firm wordmark, left-aligned, `heading-md`, `ink-900`. Text-only, no
     logo asset needed — Claude Code should render it as styled text.
2. **Title block**
   - `display-lg`, serif: "Tell us about your case."
   - Reference number line directly beneath, `mono-sm`, `brass-500`:
     `Reference INT-2026-0842` — generated client-side on mount, sent to
     the API on submit as a client-supplied idempotency hint (not the DB
     primary key).
   - One line of `body-md`, `ink-700`: what happens next, e.g. "An attorney
     will review your information and follow up by email." Written from the
     prospect's side — what happens to them, not how the system works.
3. **Form card** (`paper-0` background, `shadow-card`, `10px` radius, `32px`
   padding, single column)
   - Fields in this order: First name, Last name, Email, Resume/CV upload.
   - Every field: `label-sm` label above, `paper-0` input below, `8px` gap.
   - Field spacing: `24px` between field groups.
4. **Submit button** — full width on mobile, right-aligned auto-width on
   desktop. Primary style (`navy-600` fill).
5. **Consent line** — directly beneath the button, `body-sm ink-400`,
   centered: "By submitting, you agree to our [Terms of Service] and
   [Privacy Policy]." — pattern taken from tryalma.com's own form (see
   §0.1). Link text in `ink-700`, underlined.
6. **Footer line** — `body-sm`, `ink-400`, centered: firm address / copyright.

### 3.2 Field specs

**Text inputs (First name, Last name, Email)**
- Height `44px`, `1px solid ink-200` border, `6px` radius, `12px 14px`
  padding, `body-md`.
- Focus: border → `navy-600`, `0 0 0 3px rgba(31,58,95,0.12)` ring.
- Error: border → `brick-600`, helper text below in `body-sm brick-600`
  with a small inline error icon — message states what's wrong and how to
  fix it ("Enter a valid email address," never "Invalid input").
- Email field additionally validates format on blur, not on every keystroke.

**Resume/CV upload**
- Custom dropzone component, not a bare `<input type=file>`.
- Default state: dashed `1.5px ink-200` border, `10px` radius, `40px`
  vertical padding, centered content: an upload glyph, `body-md` "Drag your
  résumé here, or click to browse," `body-sm ink-400` "PDF or Word, up to
  10MB."
- Drag-over state: border → `navy-600` solid, background → `paper-100`.
- File-selected state: dropzone collapses to a compact row — file-type
  icon, filename (truncated middle if long), file size in `body-sm`, a
  text "Replace" action and a small "×" remove action, right-aligned.
- Uploading state: same row, thin `2px` progress bar along the bottom edge
  in `navy-600`, filename dimmed to `ink-400` until complete.
- Error state (wrong type / too large): row shows in `brick-50` background
  with `brick-600` text, message names the problem and the fix directly:
  "That file is 14MB — resumes must be under 10MB."

### 3.3 Submit button states

- Idle: "Submit application," `navy-600` fill, `paper-0` text.
- Loading (post-click): label → "Submitting…", small spinner replaces
  nothing (doesn't shift width), button disabled, no layout shift.
- Disabled (required fields incomplete): `ink-200` fill, `ink-400` text,
  no pointer cursor. Do not hide the button — let the prospect see the
  goal and discover what's missing via field-level errors on attempted
  submit.

### 3.4 Success state

On successful submit, the form card content is replaced in place (not a
new route) by a confirmation state:
- `display-md` serif headline: "Your application is in."
- Reference number repeated in `mono-sm brass-500`.
- `body-md ink-700`: "We've sent a copy to [email]. An attorney will
  reach out from here." Active voice, names exactly what happened.
- No further action offered — this is the end of the flow. Optionally a
  quiet text link "Submit another application" in `ink-400`.

### 3.5 Submission failure (network/server error)

Card stays populated with the prospect's entered data (never clear the
form on failure). A `brick-50` banner appears above the fields: "Something
went wrong on our end — your information hasn't been sent yet. Try again."
with a "Retry" button. Field data persists in local component state so
nothing is lost.

### 3.6 Responsive

**Compact (`<640px`)**
- Container padding `16px`, form card padding `20px` (down from `32px`).
- `display-lg` drops to `28px` / 1.2 line-height so the title wraps to at
  most two lines on a narrow screen.
- Header band (§3.1.1) drops to `16px` vertical padding; wordmark shrinks
  to `heading-md` if it isn't already that size.
- Fields stack full-width, `20px` gap between field groups (down from
  `24px`).
- Submit button is always full-width, placed directly after the file
  upload field with no extra margin logic — it should be the natural next
  thing to tap after attaching a résumé.
- Dropzone vertical padding drops to `28px`; label text drops to `body-sm`
  so "Drag your résumé here, or click to browse" doesn't wrap awkwardly on
  narrow phones (on touch devices this is effectively a tap target anyway
  — "drag" language still applies since desktop users share the component,
  but functionally it's a full-area tap-to-browse).
- Confirmation state (§3.4) headline drops to `22px`; content otherwise
  unchanged.

**Regular (`640–1023px`)**
- Container padding `24px`, form card padding stays at `32px`.
- `display-lg` renders at its default `40px` — plenty of room at this
  width.
- Everything else matches the Wide spec; this band is really "Wide minus
  the outer container width," since the form's own max-width (`680px`)
  is already narrower than most tablets.

**Wide (`≥1024px`)**
- Spec as written in §3.1–§3.5, unchanged. Form card stays centered at
  `680px` max-width regardless of how much wider the viewport gets — do
  not let the card stretch full-width on large monitors.

---

## 4. Page: Attorney Login

**Route:** `/login` · **Auth:** none (this issues it) · **Goal:** get to
the dashboard.

- Centered card, `400px` max-width, on `paper-50` background — deliberately
  plain, sans-serif only (this is a tool screen, not the firm's front
  door).
- `heading-lg` "Sign in," email + password fields (same input spec as
  §3.2 minus the file upload), primary submit button full width.
- Auth error (bad credentials): single `body-sm brick-600` line beneath
  the button: "That email or password isn't right." No field-level
  blaming of which one is wrong (standard security practice).
- No "forgot password" / self-registration flows required for v1 — this
  is an internal tool provisioned out-of-band; note this explicitly to
  Claude Code so it doesn't scope-creep into building them.

**Responsive**: this page barely changes across breakpoints since the
card is already narrow. On Compact, the `400px` max-width becomes
`calc(100% - 32px)` (i.e. `16px` side margins) instead of a fixed pixel
value, and the card loses its `shadow-card` in favor of sitting flush
against the page (optional — a full-bleed login card reads cleaner on a
small phone than a floating one with visible page background on all
sides). Card vertical centering can become top-anchored with `48px` top
margin on Compact if the on-screen keyboard would otherwise push the
button off-screen.

---

## 5. Page: Internal Dashboard — Lead List

**Route:** `/dashboard` · **Auth:** required, redirect to `/login` if no
valid session.

### 5.1 Structure

1. **Top bar** (`paper-0`, `1px solid ink-200` bottom border, `56px`
   height): firm wordmark left, signed-in attorney email + "Sign out"
   text action right. `body-sm`.
2. **Page header** (`24px` top padding): `heading-lg` "Leads," with a
   `body-sm ink-400` count subtitle: "128 total · 34 pending."
3. **Stat row** (optional but recommended — see §5.0) below the page
   header, above the table.
4. **Table** — the main content, full container width.

### 5.0 Stat row (pattern sourced from tryalma.com, §0.1)

A row of 3 stat cards, matching Alma's own "98%+ / Approval" treatment:
big number top, `label-sm` uppercase label below it, no caption needed at
our scale (Alma's caption exists because their number needs a disclaimer
— ours doesn't). Suggested cards: **Total leads**, **Pending**, **Reached
out** — each pulling live from the same data that populates the table, so
there's no separate query to keep in sync.

- Card: `paper-0` background, `1px solid paper-100` border (no shadow —
  these sit flush in a row, not floating), `10px` radius, `20px` padding.
- Number: `28px / 600 weight`, `ink-900`. Not a new type token — this is
  the one place a one-off size is acceptable, since it's a distinct visual
  role (stat display) from any existing scale step.
- Label: `label-sm`, `ink-400`.
- Pending/Reached-out cards use their respective state color for the
  number only (`ochre-600` / `sage-600`) — label stays neutral `ink-400`.
  Total leads number stays `ink-900`.
- Layout: `3` equal-width columns with `12px` gaps on Wide/Regular; stacks
  to a single column of full-width cards on Compact (§2.1).
- This row is a nice-to-have, not required for v1 — flag it as an easy
  addition once the base table is working, not a blocker to the first
  working version.

### 5.2 Table spec

Columns, in order: **Name** · **Email** · **Submitted** · **State** ·
(row-hover-only) **Action**.

- Header row: `label-sm` column labels, `paper-100` background, `44px`
  height, sticky on scroll.
- Name column: sortable (default sort: Submitted, newest first — attorneys
  triage new leads first). Sort indicator is a small chevron next to the
  active column label, no icon on inactive columns.
- Email column: `mono-sm ink-700`, click-to-copy on hover (small copy icon
  appears right of the text on row hover only — doesn't clutter default
  state).
- Submitted column: relative time ("2 hours ago") with the absolute
  timestamp as a native tooltip on hover.
- State column: `StateBadge` component —
  - `PENDING`: `ochre-50` background, `ochre-600` text, `999px` pill,
    label "Pending."
  - `REACHED_OUT`: `sage-50` background, `sage-600` text, same pill,
    label "Reached out." Optionally echoes the signature stamp motif with
    a small check glyph before the label — the one place the internal
    tool borrows a touch of the form's ceremony, because this state
    change is the moment of human follow-through the whole system exists
    to track.
- Row height `56px`, `1px solid paper-100` row dividers (not `ink-200` —
  keep rows quiet), hover fill `paper-50`.
- Row click opens the lead detail (see §6) — entire row is clickable, not
  just a "view" link, since this is the primary action on this screen.

### 5.3 States

- **Loading**: skeleton rows (`paper-100` shimmer blocks matching column
  widths), 6 rows, no spinner — skeletons read faster for a table this
  shape.
- **Empty** (zero leads at all): centered `body-md ink-700` "No
  applications yet." + `body-sm ink-400` "New submissions from the intake
  form will show up here." No illustration needed — text-only empty state
  is enough for an internal tool.
- **Empty filtered state** (if search/filter added later and returns
  nothing): "No leads match your filters." + a text "Clear filters"
  action. (Search/filtering is not required for v1 scope — see §8 note.)
- **Error** (list fetch fails): `brick-50` banner at top of table area,
  "Couldn't load leads. Retry," with retry button — table area stays
  otherwise empty, don't show stale data silently.

### 5.4 Responsive

**Compact (`<640px`)**
- Table fully collapses to a stacked card list — one card per lead:
  - Name as `heading-md`, top line.
  - Email as `body-sm ink-400` (drop the `mono-sm` treatment here; monospace
    email addresses at this width tend to wrap mid-word) directly below.
  - Submitted (relative time) as `body-sm ink-400`, same line as email,
    separated by a middot.
  - `StateBadge` top-right of the card, vertically centered against the
    name line.
- Cards: `paper-0` background, `shadow-card`, `10px` radius, `16px`
  padding, `12px` gap between cards, `16px` side margins on the page.
- No copy-to-clipboard affordance on this band (no hover state to reveal
  it) — tapping the email opens the device's mail app via `mailto:`
  instead, which is the touch-native equivalent.
- Top bar (§5.1.1): firm wordmark stays, attorney email is hidden (it's
  not actionable info at a glance on a phone), "Sign out" becomes an icon
  button.
- Page header count subtitle wraps to its own line under "Leads" if
  needed rather than truncating.

**Regular (`640–1023px`, i.e. tablet)**
- Table stays a real table (not cards) — an attorney on an iPad should
  still get the scanning speed of rows. Drop the **Action** hover-column
  entirely at this width (row click is the only affordance needed) and
  narrow the **Submitted** column to relative-time-only, no room for a
  wide timestamp.
- If the table's natural width still doesn't fit (rare, given the column
  set is already lean), allow the table body only to scroll horizontally
  within its container — header row and page chrome stay fixed — with a
  `12px`-wide `linear-gradient` edge fade on the right side of the table
  container as the visual cue that more content exists. This is the one
  sanctioned horizontal-scroll case referenced in §2.1.
- Top bar and page header behave as their Wide spec.

**Wide (`≥1024px`)**
- Full spec as written in §5.0–§5.3.

---

## 6. Lead Detail (drawer)

Opens as a right-side slide-in drawer over the dashboard (not a route
change) — `480px` wide on desktop, full-screen sheet on mobile.
`shadow-modal`, `paper-0` background.

- **Header**: reference number in `mono-sm brass-500` (same value shown to
  the prospect — this is the connective thread from §1.4), close "×"
  top-right.
- **Body**, stacked sections with `24px` gaps:
  - Prospect name as `heading-lg`.
  - Email, as `mono-sm`, click-to-copy.
  - Submitted timestamp, absolute + relative.
  - Résumé: a document-style row — filename, size, a "Download" button
    (secondary style) that opens the stored file. No inline preview
    required for v1.
- **Footer** (sticky to drawer bottom, `1px solid ink-200` top border,
  `16px` padding):
  - If `PENDING`: primary button "Mark as reached out."
  - If `REACHED_OUT`: state already shown in header area as a badge next
    to the reference number; footer shows a secondary/ghost button "Move
    back to pending" for correcting mistakes — not a hard requirement but
    prevents attorneys getting stuck if they click too fast. Confirm this
    trade-off with the team; omit if the state machine must be strictly
    one-directional.

### 6.1 State transition confirmation

Clicking "Mark as reached out" opens a small centered confirm dialog
(`360px`, `shadow-modal`): `heading-md` "Mark as reached out?", `body-sm
ink-700` "This records that you've contacted [First name]. It can't be
undone automatically." Two buttons: "Cancel" (ghost) and "Confirm" (primary,
`navy-600`). On confirm: dialog closes, drawer badge updates in place,
underlying table row's badge and sort position update without a full page
reload, and a toast confirms: "Marked as reached out."

### 6.1a Optional: timeline treatment (pattern sourced from tryalma.com, §0.1)

Our lead only ever has two states, so a full multi-step timeline is more
than the data supports — don't build one for v1. If a slightly richer
visual than a lone badge in the drawer header is wanted later, a two-node
version of Alma's case-timeline pattern is a reasonable upgrade, not a
required one:

```
● Application received — Aug 12          ○ Reached out
```

Filled dot + `ink-900` label for the completed step, hollow dot + `ink-400`
label for the not-yet-reached step, connected by a `1px` line that fills
`sage-600` up to the current point once "Mark as reached out" is confirmed.
This is purely decorative sugar on top of the same `state` field — it must
not become a separate piece of state to keep in sync, and it's a fine
thing to cut if it's adding build time without adding clarity.

### 6.2 Responsive

**Compact (`<640px`)**
- Drawer becomes a full-screen sheet, not a partial overlay — `100vw`
  wide, slides up from the bottom (feels more native on touch than
  sliding in from the side) or in from the right, either is acceptable,
  but pick one and use it consistently for both Drawer and Dialog.
- Header gets a full-width top bar with the close "×" and reference
  number on the same row; body content below scrolls independently of
  the header, which stays fixed.
- Footer action button(s) become full-width and stick to the bottom of
  the viewport (`env(safe-area-inset-bottom)` padding for iOS notch
  devices), so the primary action is always reachable without scrolling.
- The confirm dialog (§6.1) also goes full-width with `16px` side margins
  rather than a fixed `360px`, and its two buttons stack full-width
  (Confirm on top, Cancel below) rather than sitting side by side —
  thumb-reachable and unambiguous about which is primary.

**Regular (`640–1023px`)**
- Drawer keeps its `480px` fixed width but should not exceed roughly 90%
  of viewport width on the narrower end of this band — clamp with
  `min(480px, 90vw)`.
- Confirm dialog stays centered at its `360px` fixed width; this band has
  enough room for it as designed.

**Wide (`≥1024px`)**
- Full spec as written in §6–§6.1.

---

## 7. Shared components — build order for Claude Code

Build these as standalone primitives first, then compose pages from them.
This keeps both surfaces visually consistent without duplicating styles.

1. `Button` — variants: `primary`, `secondary`, `ghost`, `destructive`;
   sizes: `sm` (32px), `md` (40px), `lg` (44px). Loading state built in
   (spinner + disabled), not a separate component.
2. `Input`, `TextArea` — default / focus / error / disabled, per §3.2.
3. `FileUpload` — the four states in §3.2, as one component with internal
   state machine (`idle → dragging → selected → uploading → error`).
4. `StateBadge` — takes `state: 'PENDING' | 'REACHED_OUT'`, renders per
   §5.2 mapping. Single source of the state→color mapping — do not
   reimplement this switch anywhere else.
5. `Table` — generic sortable table shell; the leads list supplies columns
   and row renderer.
6. `Drawer` — right-side slide-in, used for lead detail; should be a
   generic primitive (title, body slot, footer slot) not lead-specific.
7. `Dialog` — centered confirm modal, generic (title, body, actions).
8. `Toast` — bottom-right stack, `success` / `error` / `info` variants,
   auto-dismiss 4s, manually dismissible.
9. `Skeleton` — a single block-shimmer primitive reused for table loading.

Build every primitive responsive from the start, per §2.1 — don't build
`Drawer` or `Dialog` as fixed-width and retrofit a mobile variant later;
their Compact behavior (full-screen sheet, stacked buttons) should be a
built-in size variant, not a page-level override. Same for `Button`: full
width is a prop (`fullWidth`), not something each page hacks in with a
wrapper `<div>`.

---

## 8. Accessibility checklist

- All interactive elements reachable by keyboard in visual order; visible
  focus ring on every focusable element (`0 0 0 3px rgba(31,58,95,0.12)`,
  same ring as input focus).
- Form errors are associated to their field via `aria-describedby` and the
  error region uses `aria-live="polite"` so screen readers announce it
  without needing focus to move.
- Color is never the only signal for state: `StateBadge` carries a text
  label, not just a color chip.
- Contrast: every text/background pairing in §1.1 meets 4.5:1 at the sizes
  specified (verify `ochre-600` on `ochre-50` and `sage-600` on `sage-50`
  specifically — muted tones need checking, not just the brand colors).
- Drawer and Dialog trap focus while open and return focus to the
  triggering element on close.
- Respect `prefers-reduced-motion`: disable the drawer slide-in transition
  and skeleton shimmer animation, use instant/opacity-only fallback.
- Touch targets meet the `44×44px` minimum from §2.1 on Compact and
  Regular bands — this is an accessibility requirement (WCAG 2.5.5) as
  much as a usability one.
- Verify zoom/text-resize to 200% doesn't clip content or cause overlap
  on any page, independent of the breakpoint testing in §2.1.

---

## 9. Explicitly out of scope for v1 (flag if Claude Code starts building these)

- Search, filtering, or pagination on the lead list (fine to add the
  column-sort only, per §5.2).
- Password reset / attorney self-registration on the login page.
- Inline résumé preview (download-only is sufficient).
- Multiple attorney roles/permissions — a single `AttorneyUser` role is
  enough.

---

## 10. Handoff note for Claude Code

Implement in this order for fastest path to a working E2E demo:
1. Design tokens as Tailwind config + CSS variables (§1).
2. Shared component primitives (§7).
3. Public form page (§3) — this is the only page a stranger ever sees, so
   get it right first.
4. Login (§4) + auth guard for `/dashboard`.
5. Lead list (§5) wired to `GET /api/v1/leads`.
6. Lead detail drawer + state transition (§6) wired to `PATCH
   /api/v1/leads/{id}/state`.

Every color, spacing, and radius value used in code should trace back to a
named token in §1 — no inline hex codes or arbitrary pixel values in
components.

After each page is built, check it at all three bands from §2.1 (375px,
~768px, ~1280px browser widths cover it) before moving to the next page —
retrofitting responsiveness across five pages at the end is slower and
buggier than building each one responsive as you go.
