import json
import urllib.request
from datetime import datetime, timezone


# ============================================================
# 1. جلب البيانات الحية (Live Data Fetching)
# ============================================================
def fetch_json(url, timeout=10):
  try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
      return json.loads(r.read().decode())
  except Exception:
    return None


def get_price(symbol, fallback):
  data = fetch_json(
      f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
  )
  if data and "chart" in data and data["chart"]["result"]:
    return data["chart"]["result"][0]["meta"].get(
        "regularMarketPrice", fallback
    )
  return fallback


# جلب الأسعار الفعلية الحالية
gold = get_price("GC=F", 4024.00)
silver = get_price("SI=F", 52.41)
dxy = get_price("DX-Y.NYB", 102.15)
y10 = get_price("%5ETNX", 5.018)

gsr = gold / silver if silver else 76.8
real_yield = y10 - 3.6

# ============================================================
# 2. المستويات الخوارزمية (Levels & Depth)
# ============================================================
levels = {
    "R2": 4115.93,
    "R1": 4091.56,
    "R0": 4070.00,
    "Pivot": 4042.00,
    "S1": 4033.73,
    "S2": 4020.00,
    "S3": 3995.00,
}

# ============================================================
# 3. محرك تقييم السوق (Scoring Engine)
# ============================================================
sentiment = {
    "cot_percentile": 34.8,
    "fear_greed": "Extreme Fear",
    "trend_strength": 7,
    "bull_probability": 40,
    "bear_probability": 60,
    "gdp_growth": 3.4,
    "headline_pce": 3.6,
    "core_pce": 3.1,
    "fed_rate": "3.75%-4.00%",
    "rate_hike_odds": 86,
}


def compute_score():
  score = 0
  factors = []

  if gsr > 80:
    score += 10
    factors.append((
        "Gold/Silver Ratio",
        f"{gsr:.1f}",
        "Silver cheap — gold support",
        10,
    ))
  elif gsr < 60:
    score -= 10
    factors.append((
        "Gold/Silver Ratio",
        f"{gsr:.1f}",
        "Silver expensive — pressure",
        -10,
    ))
  else:
    factors.append(("Gold/Silver Ratio", f"{gsr:.1f}", "Neutral zone", 0))

  if real_yield > 2.5:
    score -= 20
    factors.append(
        ("Real Yields", f"{real_yield:.2f}%", "Elevated — headwind", -20)
    )
  elif real_yield < 1.0:
    score += 15
    factors.append(("Real Yields", f"{real_yield:.2f}%", "Low — tailwind", 15))
  else:
    factors.append(("Real Yields", f"{real_yield:.2f}%", "Neutral", 0))

  pivot = levels["Pivot"]
  if gold > pivot + 10:
    score += 10
    factors.append(("Price vs Pivot", f"{gold:.0f} > {pivot:.0f}", "Above pivot", 10))
  elif gold < pivot - 10:
    score -= 10
    factors.append(("Price vs Pivot", f"{gold:.0f} < {pivot:.0f}", "Below pivot", -10))
  else:
    factors.append(("Price vs Pivot", f"{gold:.0f} ≈ {pivot:.0f}", "At pivot", 0))

  score = max(-100, min(100, score))
  action = "BUY" if score >= 15 else ("SELL" if score <= -15 else "WAIT")
  confidence = min(100, abs(score) + 20)

  if action == "BUY":
    entry, stop, target = levels["S2"], levels["S3"] - 10, levels["R1"]
  elif action == "SELL":
    entry, stop, target = levels["R0"], levels["R2"] + 10, levels["S2"]
  else:
    entry, stop, target = gold, 0, 0

  risk, reward = abs(entry - stop), abs(target - entry)
  rr = round(reward / risk, 2) if risk > 0 else 0

  return {
      "score": score,
      "action": action,
      "confidence": confidence,
      "rr": rr,
      "entry": entry,
      "stop": stop,
      "target": target,
      "factors": factors,
  }


result = compute_score()

# ============================================================
# 4. بناء التقرير الاحترافي (HTML Output)
# ============================================================
a = result["action"]
color = {"BUY": "#00c853", "SELL": "#d50000", "WAIT": "#ff9100"}.get(a, "#9e9e9e")

factor_rows = ""
for name, value, desc, contrib in result["factors"]:
  c = "#00c853" if contrib > 0 else ("#d50000" if contrib < 0 else "#9e9e9e")
  sign = "+" if contrib > 0 else ""
  factor_rows += f"<tr><td><b>{name}</b></td><td>{value}</td><td>{desc}</td><td style='color:{c};font-weight:bold'>{sign}{contrib}</td></tr>"

html_content = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Gold Intelligence Report {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</title>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;color:#e6edf3;padding:20px;direction:ltr}}
.container{{max-width:960px;margin:auto}}
h1{{color:#ffd700;text-align:center}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:20px;margin:16px 0}}
.action-box{{text-align:center;padding:24px;border-radius:12px;background:{color}22;border:2px solid {color}}}
.action-label{{font-size:48px;font-weight:bold;color:{color}}}
table{{width:100%;border-collapse:collapse;margin-top:8px}}
th{{text-align:left;color:#8b949e;border-bottom:1px solid #30363d;padding:8px 4px}}
td{{padding:8px 4px;border-bottom:1px solid #21262d}}
.metric{{display:inline-block;margin:8px 16px;text-align:center}}
.val{{font-size:22px;font-weight:bold;color:#ffd700}}
.lbl{{font-size:12px;color:#8b949e}}
</style></head><body><div class="container">
<h1>🥇 Gold Autonomous Intelligence Report</h1>
<p style="text-align:center;color:#8b949e">{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · XAU/USD</p>

<div class="card action-box">
  <div class="action-label">{a}</div>
  <p>Score: <b>{result['score']}</b>/100 · Confidence: <b>{result['confidence']}%</b> · R:R: <b>{result['rr']}:1</b></p>
</div>

<div class="card"><h2>📊 Market Snapshot</h2>
<div style="display:flex;flex-wrap:wrap;justify-content:space-around">
  <div class="metric"><div class="val">${gold:,.2f}</div><div class="lbl">Gold</div></div>
  <div class="metric"><div class="val">${silver:,.2f}</div><div class="lbl">Silver</div></div>
  <div class="metric"><div class="val">{gsr:.1f}</div><div class="lbl">GSR</div></div>
  <div class="metric"><div class="val">{dxy:.2f}</div><div class="lbl">DXY</div></div>
  <div class="metric"><div class="val">{real_yield:.2f}%</div><div class="lbl">Real Yield</div></div>
</div></div>

<div class="card"><h2>🧮 Factor Scorecard</h2>
<table><tr><th>Factor</th><th>Value</th><th>Interpretation</th><th>Score</th></tr>{factor_rows}</table></div>

<div class="card"><h2>🎯 Autonomous Trade Plan</h2>
<table>
<tr><td>Direction</td><td style="color:{color};font-weight:bold">{a}</td></tr>
<tr><td>Entry</td><td>${result['entry']:,.2f}</td></tr>
<tr><td>Stop Loss</td><td>${result['stop']:,.2f}</td></tr>
<tr><td>Take Profit</td><td>${result['target']:,.2f}</td></tr>
</table></div>
</div></body></html>"""

with open("index.html", "w", encoding="utf-8") as f:
  f.write(html_content)

print("✅ تم تحديث التقرير وتوليد صفحة الويب بنجاح!")