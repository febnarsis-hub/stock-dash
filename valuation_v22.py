from __future__ import annotations


def _num(value):
    return value if isinstance(value, (int, float)) and value is not None else None


def calculate_v22(report: dict) -> dict:
    """Dashboard-ready core of the user's v2.2 anchor valuation rules.
    Missing inputs are never estimated.
    """
    years = {int(r.get("year")): r for r in report.get("years", []) if r.get("year") is not None}
    y24, y25 = years.get(2024), years.get(2025)
    if not y24 or not y25:
        return {"status": "data_needed", "reason": "2024·2025 결산 자료 필요"}
    op24, op25 = _num(y24.get("profit")), _num(y25.get("profit"))
    rev24, rev25 = _num(y24.get("revenue")), _num(y25.get("revenue"))
    if None in (op24, op25, rev24, rev25) or op24 <= 0 or op25 <= 0 or rev24 <= 0 or rev25 <= 0:
        return {"status": "data_needed", "reason": "2024·2025 매출·영업이익 자료 필요"}

    op_std = (op24 + op25) / 2
    anchor_ratio = max(op24, op25) / min(op24, op25)
    m24, m25 = op24 / rev24 * 100, op25 / rev25 * 100
    if anchor_ratio <= 1.25:
        quality = "A"
    elif anchor_ratio <= 1.50:
        quality = "B"
    else:
        quality = "C"
    if (rev25 - rev24) * (m25 - m24) < 0:
        quality = "C"

    current = report.get("years", [])[-1] if report.get("years") else {}
    current_op = _num(current.get("profit"))
    current_rev = _num(current.get("revenue"))
    k = current_op / op_std if current_op is not None else None
    current_margin = current_op / current_rev * 100 if current_op is not None and current_rev else None

    momentum = (k - 1) * 100 if k is not None else None
    momentum_symbol = "▼" if momentum is not None and momentum < 0 else "" if momentum is None else "★" * (3 if momentum >= 100 else 2 if momentum >= 50 else 1 if momentum >= 30 else 0)
    edge_symbol = "" if current_margin is None else "◆" * (3 if current_margin >= 40 else 2 if current_margin >= 30 else 1 if current_margin >= 20 else 0)

    margin_change = m25 - m24
    improvement_symbol = "▽" if margin_change < 0 else "▲▲" if margin_change >= 5 and m24 > 0 and margin_change / m24 >= .30 else "▲" if margin_change >= 5 or (m24 > 0 and margin_change / m24 >= .30) else ""
    if rev25 <= rev24 * .95 and margin_change > 0:
        improvement_symbol = "🔻축소균형"

    gate = False
    if current_margin is not None and current_margin > ((m24 + m25) / 2) * 1.5:
        gate = True
    recent = [r.get("profit") for r in report.get("years", [])[-3:] if _num(r.get("profit")) is not None]
    if current_op is not None and recent and current_op > (sum(recent) / len(recent)) * 1.8:
        gate = True
    if k is not None and k > 3:
        gate = True

    anchor_ev = _num(report.get("anchor_ev"))
    net_cash = _num(report.get("net_cash"))
    shares = _num(report.get("shares"))
    price = _num(report.get("price"))
    fair_ev = anchor_ev * k if anchor_ev is not None and k is not None else None
    fair_market_cap = fair_ev + net_cash if fair_ev is not None and net_cash is not None else None
    fair_price = fair_market_cap / shares if fair_market_cap is not None and shares and shares > 0 else None
    upside = (fair_price / price - 1) * 100 if fair_price is not None and price and price > 0 else None

    confidence = "⚠️" if gate or quality == "C" else "💯" if quality == "A" else "💪"
    needed = []
    if anchor_ev is None: needed.append("anchor_ev")
    if net_cash is None: needed.append("net_cash")
    if shares is None: needed.append("shares")

    return {
        "status": "reference_only" if quality == "C" else "ok",
        "anchor_quality": quality,
        "confidence": confidence,
        "op_standard": op_std,
        "anchor_ratio": anchor_ratio,
        "anchor_margin_avg": (m24 + m25) / 2,
        "current_year": current.get("year"),
        "current_op": current_op,
        "k": k,
        "momentum": momentum,
        "momentum_symbol": momentum_symbol,
        "edge_symbol": edge_symbol,
        "improvement_symbol": improvement_symbol,
        "fair_ev": fair_ev,
        "fair_market_cap": fair_market_cap,
        "fair_price": fair_price,
        "upside": upside,
        "normalization_gate": gate,
        "data_basis": report.get("basis", "확인 필요"),
        "data_needed": needed,
    }
