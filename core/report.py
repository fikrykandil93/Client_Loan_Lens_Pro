"""Credit Approval Form as a printable A4 PDF (fpdf2, built-in Helvetica)."""
from pathlib import Path

from fpdf import FPDF

from core.model_service import THRESHOLD
from core.theme import money

LOGO = str(Path(__file__).resolve().parent.parent / "assets" / "logo.svg")

INK = (9, 23, 35)
MUTED = (100, 110, 118)
LINE = (220, 225, 228)
MINT = (242, 248, 243)
CORAL = (255, 79, 64)
CORAL_DARK = (200, 55, 43)
CORAL_TINT = (255, 238, 236)
TEAL = (14, 138, 110)
TEAL_TINT = (228, 243, 238)


def _safe(text) -> str:
    """Built-in PDF fonts are Latin-1 only."""
    return (str(text).replace("–", "-").replace("—", "-").replace("•", "*").replace("×", "x")
            .encode("latin-1", "replace").decode("latin-1"))


def detail_groups(app: dict) -> dict:
    """Client details shown on the page and in the PDF."""
    yes_no = lambda v: "Yes" if v else "No"  # noqa: E731
    docs = [f"Document {d}" for d in (3, 5, 6, 8) if app[f"doc_{d}"]] + list(app["other_docs"])
    return {
        "Personal": [("Gender", "Female" if app["gender"] == "F" else "Male"),
                     ("Date of birth", f"{app['dob']:%d/%m/%Y}"), ("Marital status", app["family_status"]),
                     ("Children", app["children"]), ("Family members", app["family_members"]),
                     ("Education", app["education"])],
        "Work and income": [("Yearly income", money(app["income"])), ("Income type", app["income_type"]),
                            ("Occupation", app["occupation"]), ("Employer type", app["organization"]),
                            ("Months with employer", app["months_employed"])],
        "Assets and home": [("Owns a car", yes_no(app["own_car"])
                             + (f", {app['car_age']} years old" if app["own_car"] else "")),
                            ("Owns property", yes_no(app["own_realty"])), ("Housing", app["housing"]),
                            ("Region rating", app["region_rating"]),
                            ("Works in another region", yes_no(app["works_other_region"]))],
        "Credit check": [("Score 1", f"{app['ext1']:.2f}" if app["ext1"] is not None else "Not available"),
                         ("Score 2", f"{app['ext2']:.2f}"), ("Score 3", f"{app['ext3']:.2f}"),
                         ("Credit bureau record", yes_no(app["has_bureau"])),
                         ("Bureau inquiries", app["bureau_req"] if app["has_bureau"] else "–")],
        "Loan request": [("Loan type", app["contract_type"]), ("Client type", app["client_type"]),
                         ("Requested amount", money(app["amount"])),
                         ("Term", f"{app['term']} months" if app["term"] else "No fixed term"),
                         ("Down payment", money(app["down_payment"])
                          if app["contract_type"] == "Consumer loans" else "–")],
        "Documents": [("Provided", ", ".join(docs) if docs else "None")],
    }


def reason_value(app: dict, reason: str) -> str:
    """This client's value for one reason from model_service.explain()."""
    yes_no = lambda v: "Yes" if v else "No"  # noqa: E731
    n_docs = sum(app[f"doc_{d}"] for d in (3, 5, 6, 8)) + len(app["other_docs"])
    values = {
        "Loan type": app["contract_type"],
        "Client type": app["client_type"],
        "Loan size": f"{money(app['amount'])} ({app['amount'] / app['income']:.1f}x yearly income)",
        "Loan term": f"{app['term']} months" if app["term"] else "No fixed term",
        "Down payment": money(app["down_payment"]),
        "Yearly income": money(app["income"]),
        "Credit score 1": f"{app['ext1']:.2f}" if app["ext1"] is not None else "Not available",
        "Credit score 2": f"{app['ext2']:.2f}",
        "Credit score 3": f"{app['ext3']:.2f}",
        "Credit bureau": f"{app['bureau_req']} inquiries" if app["has_bureau"] else "No record",
        "Age": f"{app['age']} years",
        "Gender": "Female" if app["gender"] == "F" else "Male",
        "Marital status": app["family_status"],
        "Family size": f"{app['family_members']} members",
        "Education": app["education"],
        "Income type": app["income_type"],
        "Occupation": app["occupation"],
        "Employer type": app["organization"],
        "Time with employer": f"{app['months_employed']} months",
        "Car": yes_no(app["own_car"]),
        "Property": yes_no(app["own_realty"]),
        "Housing": app["housing"],
        "Region rating": str(app["region_rating"]),
        "Works in another region": yes_no(app["works_other_region"]),
        "Documents": f"{n_docs} provided",
    }
    return str(values.get(reason, ""))


class _Form(FPDF):
    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*LINE)
        self.line(15, self.get_y() - 2, 195, self.get_y() - 2)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(*MUTED)
        self.cell(150, 5, _safe("LoanLens decision support. The model supports the loan officer; "
                                "the final decision is made by a person."))
        self.cell(30, 5, f"Page {self.page_no()}", align="R")


def build_pdf(app: dict, res: dict, segment_text: str, profile, officer: dict) -> bytes:
    pdf = _Form(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(15, 14, 15)
    pdf.add_page()
    W = 180
    refused = res["decision"] == "Refused"
    accent, tint = (CORAL, CORAL_TINT) if refused else (TEAL, TEAL_TINT)

    # ---- Header ---------------------------------------------------------------
    pdf.image(LOGO, x=15, y=13, h=11)
    pdf.set_xy(105, 14)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(45, 4.5, "Reference", align="R")
    pdf.cell(45, 4.5, "Date", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(105)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*INK)
    pdf.cell(45, 5.5, res["reference"], align="R")
    pdf.cell(45, 5.5, f"{res['date']:%d/%m/%Y}", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 17)
    pdf.cell(W, 8, "Credit Approval Form", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(W, 7, _safe(app["name"]), new_x="LMARGIN", new_y="NEXT")
    nid = app["national_id"]
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*MUTED)
    ids = ([f"Client ID {app['client_id']}"] if app.get("client_id") else []) + \
          ([f"National ID {nid[:7]}*****{nid[-2:]}"] if nid else [])
    pdf.cell(W, 5, "   |   ".join(ids + [f"Age {app['age']}"]), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*LINE)
    pdf.line(15, pdf.get_y() + 3, 195, pdf.get_y() + 3)
    pdf.ln(4.5)

    # ---- Decision box ----------------------------------------------------------------
    y0 = pdf.get_y()
    pdf.set_fill_color(*tint)
    pdf.set_draw_color(*accent)
    box_h = 37 if res.get("reasons") else 26
    pdf.rect(15, y0, W, box_h, style="DF", round_corners=True, corner_radius=4)
    pdf.set_xy(21, y0 + 4)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*(CORAL_DARK if refused else TEAL))
    pdf.cell(80, 11, res["decision"].upper())
    pdf.set_xy(21, y0 + 15.5)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*MUTED)
    term = f" over {app['term']} months" if app["term"] else ""
    pdf.multi_cell(85, 4.5, _safe(f"Model recommendation for a {app['contract_type'].lower()[:-1]} of "
                                  f"{money(app['amount'])}{term}."), align="L")
    p = res["refusal_probability"]
    bx, by, bw = 112, y0 + 13.5, 76
    pdf.set_xy(bx, y0 + 6)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(40, 5, "Refusal probability")
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(*INK)
    pdf.set_xy(bx + 40, y0 + 5)
    pdf.cell(36, 7, f"{p * 100:.0f}%", align="R")
    pdf.set_fill_color(225, 229, 232)
    pdf.rect(bx, by, bw, 3.5, style="F", round_corners=True, corner_radius=1.7)
    pdf.set_fill_color(*accent)
    pdf.rect(bx, by, max(bw * p, 3.5), 3.5, style="F", round_corners=True, corner_radius=1.7)
    lx = bx + bw * THRESHOLD
    pdf.set_draw_color(*INK)
    pdf.set_line_width(0.5)
    pdf.line(lx, by - 1.5, lx, by + 5)
    pdf.set_line_width(0.2)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*MUTED)
    pdf.set_xy(lx - 15, by + 5.5)
    pdf.cell(30, 4, f"Limit {THRESHOLD * 100:.0f}%", align="C")
    reasons = res.get("reasons") or []
    if reasons:
        ry = y0 + 26
        pdf.set_draw_color(*(CORAL if refused else TEAL))
        pdf.set_xy(21, ry)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(30, 6, "Main reasons")
        for i, r in enumerate(reasons):
            rx = 46 + i * 48
            up = r["effect"] > 0
            pdf.set_fill_color(*(CORAL_DARK if up else TEAL))
            tri = [(rx, ry + 4.4), (rx + 3.4, ry + 4.4), (rx + 1.7, ry + 1.6)] if up else \
                  [(rx, ry + 1.6), (rx + 3.4, ry + 1.6), (rx + 1.7, ry + 4.4)]
            pdf.polygon(tri, style="F")
            pdf.set_xy(rx + 4.6, ry + 0.4)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*INK)
            pdf.cell(42, 3.2, _safe(r["reason"]))
            pdf.set_xy(rx + 4.6, ry + 3.7)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(*MUTED)
            pdf.cell(42, 3, _safe(reason_value(app, r["reason"]))[:34])
    pdf.set_y(y0 + box_h + 5)

    # ---- Amount + segment boxes ---------------------------------------------------------
    y1 = pdf.get_y()
    half = (W - 6) / 2
    for x in (15, 15 + half + 6):
        pdf.set_fill_color(*MINT)
        pdf.rect(x, y1, half, 48, style="F", round_corners=True, corner_radius=4)

    def row(x, y, label, value, color=INK, size=12):
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*MUTED)
        pdf.cell(40, 6, label)
        pdf.set_font("Helvetica", "B", size)
        pdf.set_text_color(*color)
        pdf.set_xy(x + 40, y)
        pdf.cell(half - 52, 6, value, align="R")

    x = 21
    pdf.set_xy(x, y1 + 5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*INK)
    pdf.cell(half - 12, 6, "Highest approvable amount")
    requested, best = app["amount"], res["max_amount"]
    row(x, y1 + 14, "Requested", money(requested))
    if not refused:
        note, share = "Approved for the full amount requested.", 1.0
        row(x, y1 + 21, "Highest approvable", money(requested), TEAL)
    elif best:
        share = best / requested
        note = (f"With every other detail unchanged, the model would approve up to {money(best)} "
                f"({share * 100:.0f}% of the request).")
        row(x, y1 + 21, "Highest approvable", money(best), TEAL)
    else:
        share = 0
        note = "Lowering the amount alone does not change the decision, even at $10,000."
        row(x, y1 + 21, "Highest approvable", "None found", CORAL_DARK, 10)
    pdf.set_fill_color(225, 229, 232)
    pdf.rect(x, y1 + 30, half - 12, 2.5, style="F", round_corners=True, corner_radius=1.2)
    if share:
        pdf.set_fill_color(*TEAL)
        pdf.rect(x, y1 + 30, max((half - 12) * share, 2.5), 2.5, style="F", round_corners=True, corner_radius=1.2)
    pdf.set_xy(x, y1 + 35)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(half - 12, 4, _safe(note), align="L")

    x = 15 + half + 12
    pdf.set_xy(x, y1 + 5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*INK)
    pdf.cell(half - 12, 6, "Client segment")
    pdf.set_xy(x, y1 + 12)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(half - 12, 7, _safe(res["segment"]))
    pdf.set_xy(x, y1 + 19.5)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(half - 12, 4, _safe(segment_text), align="L")
    ty = y1 + 28.5
    cols = [(x, 36, "L"), (x + 36, 21, "R"), (x + 57, 24, "R")]
    head = ["", "Client", "Segment avg."]
    income_pp = app["income"] / app["family_members"]
    body = [("Income per person", money(income_pp), money(profile["Income_Person"])),
            ("Age", str(app["age"]), f"{profile['Age']:.0f}"),
            ("Credit score 2", f"{app['ext2']:.2f}", f"{profile['Credit_Score']:.2f}")]
    for r_i, values in enumerate([head] + body):
        for (cx, cw, al), v in zip(cols, values):
            pdf.set_xy(cx, ty + r_i * 4.5)
            bold = r_i > 0 and cx != x
            pdf.set_font("Helvetica", "B" if bold else "", 8)
            pdf.set_text_color(*(INK if bold else MUTED))
            pdf.cell(cw, 4.6, _safe(v), align=al)
    pdf.set_y(y1 + 53)

    # ---- Client details -----------------------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*INK)
    pdf.cell(W, 7, "Client details", new_x="LMARGIN", new_y="NEXT")
    groups = list(detail_groups(app).items())
    col = (W - 12) / 3
    lw = 29
    for i in range(0, len(groups), 3):
        y = pdf.get_y() + 1
        heights = []
        for j, (title, items) in enumerate(groups[i:i + 3]):
            gx = 15 + j * (col + 6)
            pdf.set_xy(gx, y)
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(*INK)
            pdf.cell(col, 5.5, title)
            yy = y + 6.5
            if title == "Documents":           # a long list: use the full column width
                pdf.set_draw_color(*LINE)
                pdf.line(gx, yy, gx + col, yy)
                pdf.set_xy(gx, yy + 0.6)
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_text_color(*INK)
                pdf.multi_cell(col, 4.3, _safe(items[0][1]).replace("Document ", "Doc ").replace("Doc ", "Doc\u00a0"), align="L")
                heights.append(pdf.get_y() + 0.3 - y)
                continue
            for k, v in items:
                pdf.set_draw_color(*LINE)
                pdf.line(gx, yy, gx + col, yy)
                pdf.set_xy(gx, yy + 0.6)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(*MUTED)
                pdf.cell(lw, 4.3, _safe(k))
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_text_color(*INK)
                pdf.set_xy(gx + lw, yy + 0.6)
                pdf.multi_cell(col - lw, 4.3, _safe(v), align="R")
                yy = max(yy + 5.0, pdf.get_y() + 0.3)
            heights.append(yy - y)
        pdf.set_y(y + max(heights) + 2)

    # ---- Officer decision -----------------------------------------------------------------
    notes = _safe(officer.get("notes") or "")
    pdf.set_font("Helvetica", "", 8.5)
    note_lines = max(len(pdf.multi_cell(W - 30, 4.6, notes, dry_run=True, output="LINES")), 1) if notes else 1
    extra = max(note_lines - 1, 0) * 4.6
    if pdf.get_y() > 297 - 16 - 40 - extra:   # keep the officer block in one piece
        pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*INK)
    pdf.cell(W, 7, "Officer decision", new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y() + 1
    pdf.set_draw_color(*LINE)
    pdf.rect(15, y, W, 31 + extra, round_corners=True, corner_radius=4)
    pdf.set_xy(21, y + 4.5)
    for choice in ["Approve", "Refuse", "Refer for review"]:
        cx = pdf.get_x()
        pdf.set_draw_color(*INK)
        pdf.rect(cx, y + 5.1, 3.6, 3.6)
        if officer.get("decision") == choice:
            pdf.set_fill_color(*INK)
            pdf.rect(cx + 0.8, y + 5.9, 2, 2, style="F")
        pdf.set_xy(cx + 5.5, y + 4.5)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*INK)
        pdf.cell(38, 5, choice)
    pdf.set_xy(21, y + 11.5)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.cell(18, 5, "Notes")
    pdf.set_text_color(*INK)
    pdf.multi_cell(W - 30, 4.6, notes, align="L")
    sy = y + 24.5 + extra
    for i, (label, value) in enumerate([("Loan officer", officer.get("name") or ""), ("Signature", ""), ("Date", "")]):
        sx = 21 + i * 58
        pdf.set_draw_color(*MUTED)
        pdf.line(sx, sy, sx + 50, sy)
        pdf.set_xy(sx, sy - 5.5)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*INK)
        pdf.cell(50, 5, _safe(value))
        pdf.set_xy(sx, sy + 0.8)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(50, 4, label)

    return bytes(pdf.output())
