# UK PDF Portfolio — Combined Management Briefing

Bilingual slide deck combining **B902 east extension** (Scitech FS) and **HPLC + lyophilizer retrofit** (RBPC FS) for a single leadership walkthrough.

## Open

- **`UK_PDF_Portfolio_Briefing_2026-05-28.html`** — standard retrofit breakdown (25% section contingencies)
- **`UK_PDF_Portfolio_Briefing_2026-06-08.html`** — retrofit **direct/indirect + 30% price risk & project contingency** format
- **`UK_PDF_Portfolio_Briefing_2026-06-12.html`** — adds **C1 module OEB5 upgrade** as third workstream (£2.48M internal estimate)

Open any file in a browser · **中文 / EN** toggle · **← →** to navigate

## Rebuild

```bash
python3 scripts/build_portfolio_briefing.py
python3 scripts/build_portfolio_briefing_2026-06-08.py
python3 scripts/build_portfolio_briefing_2026-06-12.py
```

Sources: `scripts/build_management_briefing.py` + `scripts/build_hplc_lyopho_briefing.py` (data/constants only).

## Slide map (2026-06-12 deck, 25 pages)

1. Cover · 2. Project overview (3 workstreams + delivery link)  
3–9. Extension · 10–17. HPLC/lyoph retrofit · 18–24. C1 OEB5 upgrade · 25. Portfolio decisions · Thank you

(No investment comparison chart, extension scope baseline, or portfolio decision slide.)

Individual decks remain in `汇报/PDF-Extension-COO-CFO/` and `汇报/HPLC-Lyophilizer/`.
