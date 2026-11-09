"""LoanLens design tokens and global CSS (Monzo-inspired, original components)."""
import streamlit as st

# ---- Design tokens -------------------------------------------------------
INK = "#091723"          # main text, primary buttons
INK_SOFT = "#112231"     # secondary dark surface
MUTED = "rgba(9, 23, 35, 0.62)"
LINE = "rgba(9, 23, 35, 0.12)"
MINT = "#F2F8F3"         # section / card surface
PAPER = "#FFFFFF"
CORAL = "#FF4F40"        # brand accent + refused
TEAL = "#0E8A6E"         # approved
AMBER = "#E8A33D"        # warnings

FONT_DISPLAY = "'Bricolage Grotesque', sans-serif"
FONT_TEXT = "'Onest', sans-serif"

# Plotly colors that follow the tokens
STATUS_COLORS = {"Approved": TEAL, "Refused": CORAL}
SEQUENCE = [INK, TEAL, CORAL, "#5B7BA6", AMBER, "#8A9AA8"]

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Onest:wght@400;500;600;700&display=swap');

:root {{
  --ink: {INK}; --ink-soft: {INK_SOFT}; --muted: {MUTED}; --line: {LINE};
  --mint: {MINT}; --paper: {PAPER}; --coral: {CORAL}; --teal: {TEAL}; --amber: {AMBER};
  --display: {FONT_DISPLAY}; --text: {FONT_TEXT};
  --r-sm: 12px; --r-md: 24px; --r-lg: 40px; --r-pill: 999px;
}}

/* Base typography */
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea,
.stApp button, .stApp [data-testid="stMarkdownContainer"] {{
  font-family: var(--text);
  font-variant-numeric: tabular-nums;
}}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
  font-family: var(--display); font-weight: 800; color: var(--ink);
  letter-spacing: -0.02em;
}}
.block-container {{ padding-top: 6.5rem; max-width: 1180px; }}

/* Top header bar: same surface as the former sidebar */
[data-testid="stHeader"] {{
  background: var(--mint); border-bottom: 1px solid var(--line); height: 4.25rem;
}}
[data-testid="stHeader"] [data-testid="stToolbar"] {{ height: 100%; align-items: center; }}
[data-testid="stHeaderLogo"] {{ height: 2.1rem; margin-right: 1.5rem; }}
[data-testid="stTopNavLink"] {{
  border-radius: var(--r-pill); padding: 0.45rem 1rem; transition: background 150ms ease;
}}
[data-testid="stTopNavLink"]:hover {{ background: rgba(9, 23, 35, 0.06); }}
[data-testid="stTopNavLink"][aria-current="page"] {{ background: rgba(9, 23, 35, 0.09); }}
[data-testid="stTopNavLink"][aria-current="page"] p {{ font-weight: 700; }}
[data-testid="stTopNavLink"]:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 2px; }}

/* Home only: faded photo behind the page (class set by pages/home.py) */
.stApp:has(.ll-home-marker) {{
  background:
    linear-gradient(rgba(255,255,255,0.86), rgba(255,255,255,0.93)),
    var(--hero-img) center top / cover no-repeat fixed;
}}

/* Buttons: pill shape */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
  border-radius: var(--r-pill); font-weight: 600; padding: 0.6rem 1.4rem;
  min-height: 44px; transition: transform 150ms ease, background 150ms ease;
}}
.stButton > button:active, .stDownloadButton > button:active {{ transform: scale(0.98); }}

/* ---- LoanLens components ---- */
.ll-brand {{ font-family: var(--display); font-weight: 800; font-size: 1.6rem; color: var(--ink); letter-spacing: -0.03em; }}
.ll-brand span {{ color: var(--coral); }}
.ll-brand-sub {{ color: var(--muted); font-size: 0.85rem; margin-top: -0.2rem; }}

.ll-hero h1 {{ font-size: clamp(2.4rem, 5vw, 3.9rem); line-height: 1.02; margin: 0 0 1rem 0; max-width: 14ch; }}
.ll-hero p {{ font-size: 1.15rem; line-height: 1.55; color: var(--muted); max-width: 56ch; margin: 0; }}

.ll-panel {{ background: var(--mint); border-radius: var(--r-md); padding: 1.75rem 2rem; }}
.ll-panel-dark {{ background: var(--ink); color: #fff; border-radius: var(--r-md); padding: 1.75rem 2rem; }}
.ll-label {{ color: var(--muted); font-size: 0.95rem; font-weight: 500; }}
.ll-panel-dark .ll-label {{ color: rgba(255,255,255,0.7); }}
.ll-big {{ font-family: var(--display); font-weight: 800; font-size: clamp(2.4rem, 4.5vw, 3.4rem); line-height: 1; letter-spacing: -0.03em; }}
.ll-mid {{ font-family: var(--display); font-weight: 800; font-size: 1.9rem; line-height: 1.05; letter-spacing: -0.02em; }}
.ll-note {{ color: var(--muted); font-size: 0.9rem; line-height: 1.5; }}

/* Split bar: approved vs refused */
.ll-split {{ display: flex; height: 18px; border-radius: var(--r-pill); overflow: hidden; margin: 1.1rem 0 1.25rem 0; }}
.ll-split .a {{ background: var(--teal); }}
.ll-split .r {{ background: var(--coral); }}
.ll-legend {{ display: flex; gap: 2.5rem; flex-wrap: wrap; }}
.ll-legend .dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 0.45rem; }}

/* Steps (a real sequence) */
.ll-steps {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }}
.ll-step {{ border: 1px solid var(--line); border-radius: var(--r-md); padding: 1.4rem 1.5rem; background: var(--paper); }}
.ll-step .n {{ font-family: var(--display); font-weight: 800; font-size: 1rem; width: 2rem; height: 2rem; border-radius: 50%;
  background: var(--ink); color: #fff; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0.9rem; }}
.ll-step h4 {{ font-size: 1.15rem; margin: 0 0 0.35rem 0; }}
.ll-step p {{ color: var(--muted); margin: 0; line-height: 1.5; font-size: 0.97rem; }}

.ll-page-head {{ margin-bottom: 0.5rem; }}
.ll-banner {{ border-radius: var(--r-md); padding: 2.4rem 2.25rem 2.2rem 2.25rem; border: 1px solid var(--line);
  min-height: 210px; display: flex; flex-direction: column; justify-content: center; }}
@media (max-width: 760px) {{ .ll-banner {{ padding: 1.6rem 1.25rem; min-height: 0; }} }}
.ll-page-head h1 {{ font-size: clamp(1.9rem, 3vw, 2.6rem); line-height: 1.08; margin: 0 0 0.6rem 0;
  max-width: 36ch; text-wrap: balance; }}
.ll-page-head p {{ color: var(--muted); font-size: 1.05rem; line-height: 1.55; max-width: 62ch; margin: 0; }}

/* Metric strip: one-line labels, values on one baseline */
.ll-strip {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); background: var(--mint);
  border-radius: var(--r-md); padding: 1.35rem 0; margin: 0.75rem 0 0.5rem 0; }}
.ll-strip > div {{ padding: 0 1.4rem; border-left: 1px solid var(--line); display: flex; flex-direction: column; gap: 0.35rem; }}
.ll-strip > div:first-child {{ border-left: none; }}
.ll-strip .ll-label {{ font-size: 0.88rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.ll-strip .ll-mid {{ font-size: 1.7rem; }}

/* Filter: pill segmented control */
[data-testid="stWidgetLabel"] p {{ color: var(--muted); font-size: 0.88rem; font-weight: 500; }}
.ll-filter-summary {{ color: var(--muted); font-size: 0.92rem; margin-left: 0.25rem; }}
.ll-filter-summary::before {{ content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  background: var(--teal); margin-right: 0.5rem; vertical-align: middle; }}
.ll-empty {{ display: flex; align-items: center; justify-content: center; height: 260px; color: var(--muted);
  background: var(--mint); border-radius: var(--r-sm); font-size: 0.95rem; text-align: center; padding: 1rem; }}
[data-testid="stButtonGroup"] button[aria-checked] {{ border-radius: var(--r-pill) !important; border: 1px solid var(--line) !important;
  margin-right: 0.4rem; padding: 0.35rem 1rem; min-height: 40px; background: var(--paper); box-shadow: none !important; }}
[data-testid="stButtonGroup"] button[aria-checked="true"] {{ background: var(--ink) !important; border-color: var(--ink) !important; }}
[data-testid="stButtonGroup"] button[aria-checked="true"] p {{ color: #fff !important; font-weight: 600; }}
[data-testid="stButtonGroup"] button:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 2px; }}
.ll-chart-title {{ font-family: var(--display); font-weight: 800; font-size: 1.15rem; color: var(--ink); }}
.ll-finding {{ color: var(--muted); font-size: 0.95rem; line-height: 1.45; margin: 0.2rem 0 0.4rem 0;
  min-height: 2.9em; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: var(--r-md) !important; }}
.ll-sec {{ display: flex; gap: 0.85rem; align-items: flex-start; margin-bottom: 0.4rem; }}
.ll-sec .n {{ font-family: var(--display); font-weight: 800; width: 2rem; height: 2rem; flex: none; border-radius: 50%;
  background: var(--ink); color: #fff; display: inline-flex; align-items: center; justify-content: center; }}
.ll-sec .tt {{ flex: 1; }}
.ll-status {{ flex: none; font-size: 0.82rem; font-weight: 600; padding: 0.25rem 0.7rem; border-radius: var(--r-pill);
  background: rgba(9,23,35,0.06); color: var(--muted); margin-top: 0.15rem; white-space: nowrap; }}
.ll-status.ok {{ background: rgba(14,138,110,0.12); color: var(--teal); }}
.ll-calc {{ background: var(--mint); border-radius: var(--r-sm); padding: 0.55rem 0.9rem; margin-top: 1.75rem;
  display: flex; align-items: baseline; gap: 0.6rem; font-size: 0.9rem; color: var(--muted); }}
.ll-calc b {{ font-family: var(--display); font-size: 1.25rem; color: var(--ink); }}
.ll-calc span {{ font-size: 0.8rem; }}
.ll-progress {{ margin: 0.3rem 0 0.6rem 0; }}
.ll-progress .lbl {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.4rem 0.5rem;
  font-size: 0.86rem; color: var(--muted); }}
.ll-progress .lbl > span:first-child {{ white-space: nowrap; }}
.ll-progress .steps {{ white-space: nowrap; flex: none; }}
.ll-progress .steps span {{ display: inline-flex; width: 1.35rem; height: 1.35rem; border-radius: 50%; margin-left: 0.2rem;
  align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 700; background: rgba(9,23,35,0.08); color: var(--muted); }}
.ll-progress .steps span.ok {{ background: var(--teal); color: #fff; }}
.ll-progress .bar {{ height: 8px; border-radius: var(--r-pill); background: rgba(9,23,35,0.08); margin-top: 0.45rem; overflow: hidden; }}
.ll-progress .bar div {{ height: 100%; background: var(--teal); border-radius: var(--r-pill); transition: width 250ms ease; }}
.ll-sec .t {{ font-family: var(--display); font-weight: 800; font-size: 1.2rem; color: var(--ink); line-height: 1.2; }}
.ll-sec .h {{ color: var(--muted); font-size: 0.9rem; margin-top: 0.1rem; }}
.ll-sub {{ font-weight: 600; font-size: 0.92rem; color: var(--ink); margin: 0.6rem 0 -0.2rem 0; }}
.ll-err, .ll-warn {{ font-size: 0.85rem; line-height: 1.35; margin: -0.35rem 0 0.4rem 0; display: flex; gap: 0.35rem; }}
.ll-err {{ color: #C8372B; }}
.ll-warn {{ color: #9A6412; }}
.ll-err::before {{ content: "●"; font-size: 0.6rem; margin-top: 0.3rem; }}
.ll-warn::before {{ content: "▲"; font-size: 0.6rem; margin-top: 0.3rem; }}
[data-testid="stColumn"]:has(.ll-sticky-marker) {{ position: sticky; top: 5.5rem; align-self: flex-start; }}
.ll-summary {{ background: var(--mint); border-radius: var(--r-md); padding: 1.3rem 1.4rem; }}
.ll-summary .r {{ display: flex; justify-content: space-between; gap: 1rem; padding: 0.55rem 0;
  border-bottom: 1px solid var(--line); font-size: 0.93rem; }}
.ll-summary .r:last-child {{ border-bottom: none; }}
.ll-summary .r span {{ color: var(--muted); }}
.ll-summary .r b {{ text-align: right; font-weight: 600; }}
.ll-summary .ll-chart-title {{ margin-bottom: 0.4rem; }}
.ll-err-box, .ll-warn-box {{ border-radius: var(--r-sm); padding: 0.85rem 1rem; font-size: 0.88rem; line-height: 1.45; }}
.ll-err-box {{ background: #FDECEA; color: #8E2A21; }}
.ll-warn-box {{ background: #FDF3E1; color: #7A4F0E; }}
.ll-err-box ul, .ll-warn-box ul {{ margin: 0.35rem 0 0 1rem; padding: 0; }}
.ll-doc-head {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 1.5rem; flex-wrap: wrap;
  padding-bottom: 1.25rem; border-bottom: 1px solid var(--line); margin-bottom: 1.25rem; }}
.ll-form-title {{ font-family: var(--display); font-weight: 800; font-size: clamp(1.5rem, 2.4vw, 1.9rem);
  color: var(--ink); letter-spacing: -0.01em; }}
.ll-doc-head h1 {{ font-size: clamp(1.9rem, 3vw, 2.5rem); margin: 0.15rem 0 0.25rem 0; line-height: 1.05; }}
.ll-doc-meta {{ display: flex; gap: 2rem; }}
.ll-doc-meta div {{ display: flex; flex-direction: column; gap: 0.15rem; }}
.ll-doc-meta span {{ color: var(--muted); font-size: 0.85rem; }}
.ll-doc-meta b {{ font-weight: 600; }}
.ll-decision {{ border-radius: var(--r-md); padding: 1.75rem 2rem; display: grid; grid-template-columns: 1.1fr 1fr;
  gap: 2rem; align-items: center; margin-bottom: 1rem; }}
.ll-decision.approved {{ background: rgba(14,138,110,0.09); border: 1px solid rgba(14,138,110,0.25); }}
.ll-decision.refused {{ background: rgba(255,79,64,0.08); border: 1px solid rgba(255,79,64,0.28); }}
.ll-decision-main {{ display: flex; gap: 1.1rem; align-items: center; }}
.ll-decision-icon {{ width: 3.4rem; height: 3.4rem; flex: none; border-radius: 50%; display: inline-flex; align-items: center;
  justify-content: center; font-size: 1.6rem; font-weight: 800; color: #fff; }}
.approved .ll-decision-icon {{ background: var(--teal); }}
.refused .ll-decision-icon {{ background: var(--coral); }}
.ll-decision-word {{ font-family: var(--display); font-weight: 800; font-size: clamp(2.2rem, 4vw, 3rem); line-height: 1;
  letter-spacing: -0.03em; }}
.approved .ll-decision-word {{ color: var(--teal); }}
.refused .ll-decision-word {{ color: #D93A2E; }}
.ll-decision-sub {{ color: var(--muted); margin-top: 0.35rem; line-height: 1.45; }}
.ll-prob-top {{ display: flex; justify-content: space-between; align-items: baseline; color: var(--muted); font-size: 0.92rem; }}
.ll-prob-top b {{ font-family: var(--display); font-size: 1.9rem; color: var(--ink); }}
.ll-prob-track {{ position: relative; height: 14px; border-radius: var(--r-pill); background: rgba(9,23,35,0.08);
  margin: 0.6rem 0 1.6rem 0; }}
.ll-prob-track .fill {{ height: 100%; border-radius: var(--r-pill); }}
.approved .ll-prob-track .fill {{ background: var(--teal); }}
.refused .ll-prob-track .fill {{ background: var(--coral); }}
.ll-prob-track .limit {{ position: absolute; top: -5px; bottom: -5px; width: 2px; background: var(--ink); }}
.ll-prob-track .limit span {{ position: absolute; top: 24px; left: 50%; transform: translateX(-50%); white-space: nowrap;
  font-size: 0.78rem; color: var(--muted); }}
.ll-amount-row {{ display: flex; justify-content: space-between; align-items: baseline; padding: 0.55rem 0;
  border-bottom: 1px solid var(--line); }}
.ll-amount-row span {{ color: var(--muted); }}
.ll-amount-row b {{ font-family: var(--display); font-size: 1.5rem; }}
.ll-amount-row b.teal {{ color: var(--teal); }}
.ll-amount-row b.coral {{ color: #D93A2E; font-size: 1.2rem; }}
.ll-amount-bar {{ height: 12px; border-radius: var(--r-pill); background: rgba(9,23,35,0.08); margin: 1rem 0 0.8rem 0; overflow: hidden; }}
.ll-amount-bar .ok {{ height: 100%; background: var(--teal); border-radius: var(--r-pill); min-width: 12px; }}
.ll-seg-name {{ font-family: var(--display); font-weight: 800; font-size: 1.6rem; margin: 0.4rem 0 0.2rem 0; color: var(--ink); }}
.ll-seg-table {{ width: 100%; border-collapse: collapse; margin-top: 0.6rem; font-size: 0.92rem; }}
.ll-seg-table th {{ text-align: right; color: var(--muted); font-weight: 500; padding: 0.4rem 0; }}
.ll-seg-table td {{ text-align: right; padding: 0.45rem 0; border-top: 1px solid var(--line); font-weight: 600; }}
.ll-seg-table td:first-child, .ll-seg-table th:first-child {{ text-align: left; color: var(--muted); font-weight: 500; }}
.ll-dl-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1rem; }}
.ll-dl {{ background: var(--mint); border-radius: var(--r-md); padding: 1.2rem 1.35rem; }}
.ll-dl-title {{ font-family: var(--display); font-weight: 800; font-size: 1.05rem; margin-bottom: 0.4rem; color: var(--ink); }}
.ll-dl .r {{ display: flex; justify-content: space-between; gap: 1rem; padding: 0.4rem 0; border-bottom: 1px solid var(--line);
  font-size: 0.9rem; }}
.ll-dl .r:last-child {{ border-bottom: none; }}
.ll-dl .r span {{ color: var(--muted); }}
.ll-dl .r b {{ font-weight: 600; text-align: right; }}
@media (max-width: 900px) {{
  .ll-decision {{ grid-template-columns: 1fr; gap: 1.2rem; padding: 1.4rem 1.25rem; }}
  .ll-dl-grid {{ grid-template-columns: 1fr; }}
}}
.ll-section-title {{ font-family: var(--display); font-weight: 800; font-size: 1.6rem; margin: 2.75rem 0 1rem 0; color: var(--ink); letter-spacing: -0.02em; }}

@media (max-width: 760px) {{
  .ll-steps {{ grid-template-columns: 1fr; }}
  .ll-strip {{ grid-template-columns: 1fr 1fr; row-gap: 1.1rem; }}
  .ll-strip > div:nth-child(odd) {{ border-left: none; }}
  .ll-panel, .ll-panel-dark {{ padding: 1.4rem 1.25rem; }}
  .stApp .block-container {{ padding-top: 6rem !important; }}
}}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}

/* ---- Why the model decided ---- */
.ll-reasons{{border:1px solid #E3EAE5;border-radius:24px;padding:20px 24px 10px;margin:14px 0 16px;background:#fff}}
.ll-reasons .ll-note{{margin:2px 0 8px}}
.ll-reason{{display:grid;grid-template-columns:28px 1fr minmax(160px,38%);align-items:center;gap:14px;padding:11px 0;border-top:1px solid #EEF2EF}}
.ll-reason-arrow{{width:28px;height:28px;border-radius:50%;display:grid;place-items:center;font-size:.72rem}}
.ll-reason.up .ll-reason-arrow{{background:#FFEDEB;color:#C8372B}}
.ll-reason.down .ll-reason-arrow{{background:#E4F3EE;color:#0E8A6E}}
.ll-reason-text b{{display:block;font-weight:700;color:#091723}}
.ll-reason-text span{{font-size:.86rem;color:#5C6770}}
.ll-reason-effect span{{display:block;font-size:.78rem;color:#5C6770;margin-top:5px}}
.ll-reason-bar{{height:8px;border-radius:99px;background:#EEF2EF;overflow:hidden}}
.ll-reason-bar div{{height:100%;border-radius:99px}}
.ll-reason.up .ll-reason-bar div{{background:#FF4F40}}
.ll-reason.down .ll-reason-bar div{{background:#0E8A6E}}
@media (max-width:640px){{.ll-reason{{grid-template-columns:28px 1fr}}.ll-reason-effect{{grid-column:2}}}}

/* ---- Segments & Model ---- */
.ll-segcards{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.85rem;margin-bottom:1.6rem}}
.ll-segcard{{border:1px solid var(--line);border-radius:var(--r-md);padding:1.1rem 1.1rem .8rem;background:var(--paper);display:flex;flex-direction:column}}
.ll-tier{{align-self:flex-start;font-size:.75rem;font-weight:700;padding:.2rem .6rem;border-radius:var(--r-pill)}}
.ll-tier.prime{{background:#E4F3EE;color:#0B6F58}}
.ll-tier.near{{background:#FDF1DD;color:#8A5A10}}
.ll-tier.sub{{background:#FFEDEB;color:#B3352A}}
.ll-segcard-name{{font-family:var(--display);font-weight:800;font-size:1.2rem;line-height:1.15;margin:.55rem 0 .2rem;color:var(--ink)}}
.ll-segcard-share{{font-size:.85rem;color:var(--muted)}}
.ll-segcard-share b{{color:var(--ink);font-size:1rem}}
.ll-segcard p{{font-size:.84rem;color:var(--muted);line-height:1.4;margin:.6rem 0 .5rem;min-height:5.7em}}
.ll-segcard .r{{display:flex;justify-content:space-between;gap:.4rem;font-size:.8rem;padding:.38rem 0;border-top:1px solid var(--line)}}
.ll-segcard .r span{{color:var(--muted);white-space:nowrap}}
.ll-segcard .r b{{color:var(--ink);font-weight:700}}
.ll-read{{height:440px;box-sizing:border-box;margin-top:3.55rem}}
.ll-read ul{{margin:.8rem 0 0;padding-left:1.1rem}}
.ll-read li{{margin-bottom:.9rem;color:var(--muted);line-height:1.45;font-size:.93rem}}
.ll-read li b{{color:var(--ink)}}
.ll-steps-4{{grid-template-columns:repeat(4,minmax(0,1fr))}}
.ll-steps-plain .ll-step h4{{margin-top:0}}
@media (max-width:1100px){{.ll-segcards{{grid-template-columns:repeat(3,minmax(0,1fr))}}.ll-steps-4{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media (max-width:760px){{.ll-segcards{{grid-template-columns:repeat(2,minmax(0,1fr))}}.ll-read{{height:auto;margin-top:0}}}}
@media (max-width:520px){{.ll-segcards,.ll-steps-4{{grid-template-columns:1fr}}.ll-segcard p{{min-height:0}}}}

/* ---- Existing client lookup ---- */
.ll-found{{background:var(--mint);border-radius:var(--r-sm);padding:.6rem .9rem;font-size:.9rem;color:var(--muted);line-height:1.5}}
.ll-found b{{color:var(--ink)}}
.ll-found b.coral{{color:#C8372B}}
.ll-found b.teal{{color:var(--teal)}}
.ll-found.ok{{border-left:4px solid var(--teal)}}
.ll-hint{{background:#FDF1DD;color:#6B4708;border-radius:var(--r-sm);padding:.45rem .7rem;font-size:.84rem;margin-top:.35rem}}
.ll-bank{{font-size:.92rem;color:var(--muted);margin:-.4rem 0 .4rem .25rem}}
.ll-bank b.coral{{color:#C8372B}} .ll-bank b.teal{{color:var(--teal)}}
</style>
"""


def apply_theme() -> None:
    """Inject fonts and component styles once per page run."""
    st.html(_CSS)


def money(value: float) -> str:
    """US dollars, no cents: $150,000."""
    return f"${value:,.0f}"


def number(value: float) -> str:
    return f"{value:,.0f}"


def pct(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}%"


def page_background(image_path: str) -> None:
    """Faded photo behind the current page (used on Home only)."""
    import base64
    from pathlib import Path

    path = Path(__file__).resolve().parent.parent / image_path
    if not path.exists():
        return
    data = base64.b64encode(path.read_bytes()).decode()
    st.html(
        f'<style>:root {{ --hero-img: url("data:image/jpeg;base64,{data}"); }}</style>'
        '<span class="ll-home-marker"></span>'
    )


def _image_data(image_path: str) -> str | None:
    import base64
    from pathlib import Path

    path = Path(__file__).resolve().parent.parent / image_path
    return base64.b64encode(path.read_bytes()).decode() if path.exists() else None


def page_head(title: str, subtitle: str, banner: str | None = None) -> None:
    """Page title block. With a banner, a faded photo sits behind the title only.

    The white veil is strongest on the left (where the text is) and lighter on the
    right, so the photo shows without competing with the title.
    """
    style = ""
    cls = "ll-page-head"
    data = _image_data(banner) if banner else None
    if data:
        cls += " ll-banner"
        style = (
            'style="background:'
            "linear-gradient(90deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.90) 45%, "
            "rgba(255,255,255,0.78) 100%), "
            f'url(data:image/jpeg;base64,{data}) center / cover no-repeat;"'
        )
    st.html(f'<div class="{cls}" {style}><h1>{title}</h1><p>{subtitle}</p></div>')
