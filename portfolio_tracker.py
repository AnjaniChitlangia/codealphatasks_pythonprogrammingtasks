"""
Stock Portfolio Tracker
-----------------------
Calculates total investment, current value and profit/loss from a hardcoded
price table, then projects each holding forward over the user's investment
horizon and checks it against a target "safe to sell" return.

All prices and expected growth rates below are made-up sample values for
learning purposes -- this is not financial advice.
"""

import csv
import math
from datetime import datetime

# Hardcoded "current market prices" (per share), keyed by stock name
STOCK_PRICES = {
    "Apple": 180.0,
    "Tesla": 250.0,
    "Google": 140.0,
    "Microsoft": 410.0,
    "Amazon": 175.0,
    "Nvidia": 120.0,
    "Meta": 500.0,
    "Infosys": 18.5,
    "TCS": 45.0,
    "Reliance": 30.0,
}

# Assumed long-term expected annual return for each stock (sample values)
EXPECTED_ANNUAL_RETURN = {
    "Apple": 0.12,
    "Tesla": 0.15,
    "Google": 0.11,
    "Microsoft": 0.12,
    "Amazon": 0.13,
    "Nvidia": 0.18,
    "Meta": 0.12,
    "Infosys": 0.10,
    "TCS": 0.10,
    "Reliance": 0.11,
}
DEFAULT_ANNUAL_RETURN = 0.12

# Hardcoded 52-week (low, high) price range for each stock (sample values)
PRICE_RANGE_52W = {
    "Apple": (165.0, 237.0),
    "Tesla": (180.0, 480.0),
    "Google": (130.0, 205.0),
    "Microsoft": (385.0, 470.0),
    "Amazon": (160.0, 240.0),
    "Nvidia": (85.0, 155.0),
    "Meta": (440.0, 740.0),
    "Infosys": (16.0, 23.0),
    "TCS": (40.0, 52.0),
    "Reliance": (28.0, 37.0),
}
TOP_PICKS = 3

# Default custom scenario (the user can change both when running the program).
# Longer tenures get a higher default rate.
DEFAULT_SCENARIO_YEARS = 10
LONG_TERM_YEARS = 10
LONG_TERM_RATE = 15.0    # % per year when tenure >= 10 years
SHORT_TERM_RATE = 12.0   # % per year when tenure < 10 years


def default_rate_for(years):
    return LONG_TERM_RATE if years >= LONG_TERM_YEARS else SHORT_TERM_RATE

# Lets the user type "apple", "APPLE" or "Apple"
NAME_LOOKUP = {name.lower(): name for name in STOCK_PRICES}


def money(x):
    return f"-${-x:,.2f}" if x < 0 else f"${x:,.2f}"


def ask_float(prompt, minimum=0.0, default=None):
    """Keep asking until the user enters a valid number >= minimum."""
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            value = float(raw)
            if value < minimum:
                print(f"  Please enter a value of at least {minimum}.")
                continue
            return value
        except ValueError:
            print("  Invalid number, try again.")


def ask_int(prompt, minimum=1):
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and int(raw) >= minimum:
            return int(raw)
        print(f"  Please enter a whole number of at least {minimum}.")


def years_to_reach(current, target, rate):
    """Years for `current` to grow to `target` at annual `rate` (compounded)."""
    if current >= target:
        return 0.0
    if rate <= 0:
        return math.inf
    return math.log(target / current) / math.log(1 + rate)


def yearly_values(start_value, rate, years):
    """List of (year, value) at the end of each year; includes a final
    fractional year if `years` is not a whole number."""
    points = [(y, start_value * (1 + rate) ** y) for y in range(1, int(years) + 1)]
    if years != int(years):
        points.append((years, start_value * (1 + rate) ** years))
    return points


def analyse_holding(name, qty, buy_price, years, target_pct):
    current_price = STOCK_PRICES[name]
    rate = EXPECTED_ANNUAL_RETURN.get(name, DEFAULT_ANNUAL_RETURN)

    invested = qty * buy_price
    current_value = qty * current_price
    profit = current_value - invested
    profit_pct = profit / invested * 100

    yearly = yearly_values(current_value, rate, years)
    projected_value = yearly[-1][1]

    target_price = buy_price * (1 + target_pct / 100)
    yrs_to_target = years_to_reach(current_price, target_price, rate)

    if current_price >= target_price:
        advice = "Target reached - can consider selling"
    elif yrs_to_target <= years:
        advice = f"Target expected in ~{yrs_to_target:.1f} yrs (within horizon)"
    else:
        advice = "Target unlikely within horizon - hold longer or revise"

    return {
        "Stock": name,
        "Quantity": qty,
        "Buy Price": round(buy_price, 2),
        "Current Price": round(current_price, 2),
        "Invested": round(invested, 2),
        "Current Value": round(current_value, 2),
        "P/L": round(profit, 2),
        "P/L %": round(profit_pct, 2),
        "Horizon (yrs)": years,
        "Exp. Annual Return %": round(rate * 100, 2),
        "Projected Value": round(projected_value, 2),
        "Projected Return": round(projected_value - invested, 2),
        "Target Sell Price": round(target_price, 2),
        "Target Amount": round(qty * target_price, 2),
        "Advice": advice,
        "_yearly": yearly,  # not written to CSV
    }


def collect_portfolio():
    print("\nAvailable stocks and current prices:")
    for name, price in STOCK_PRICES.items():
        rate = EXPECTED_ANNUAL_RETURN.get(name, DEFAULT_ANNUAL_RETURN) * 100
        print(f"  {name:<10} ${price:>8.2f}   (expected ~{rate:.0f}%/yr)")

    holdings = []
    print("\nEnter your holdings. Type 'done' as the stock name to finish.")
    while True:
        raw = input("\nStock name: ").strip().lower()
        if raw == "done":
            break
        if raw not in NAME_LOOKUP:
            print("  Unknown stock. Choose one from the list above.")
            continue
        name = NAME_LOOKUP[raw]
        print(f"  {name} current price: ${STOCK_PRICES[name]:.2f} per share")

        qty = ask_int("  Quantity: ")
        buy_price = ask_float("  Price you bought at (per share): ", minimum=0.01)
        years = ask_float("  How many years do you plan to hold? ", minimum=0.1)
        default_target = 15.0 if years > 10 else 12.0
        target = ask_float(
            f"  Target return % at which you'd sell [default {default_target:g}]: ",
            minimum=0.0, default=default_target,
        )
        holdings.append(analyse_holding(name, qty, buy_price, years, target))
        print(f"  Added {qty} x {name}.")
    return holdings


def yearly_table(yearly, invested, indent="    "):
    lines = [f"{indent}{'Year':>6} {'Value':>16} {'Return':>16} {'Return %':>10}"]
    for year, value in yearly:
        gain = value - invested
        lines.append(
            f"{indent}{year:>6g} {money(value):>16} {money(gain):>16}"
            f" {gain / invested * 100:>+9.1f}%"
        )
    return lines


def ask_scenario():
    print("\nCustom scenario: see what your portfolio could become at a rate"
          " and tenure of your choice.")
    years = ask_float(
        f"  Tenure in years [default {DEFAULT_SCENARIO_YEARS}]: ",
        minimum=0.1, default=DEFAULT_SCENARIO_YEARS,
    )
    default_rate = default_rate_for(years)
    rate = ask_float(
        f"  Expected rate of return % per year [default {default_rate:g}"
        f" for {'10+' if years >= LONG_TERM_YEARS else 'under 10'} years]: ",
        minimum=0.0, default=default_rate,
    )
    return rate / 100, years


def score_stock(name):
    """Simple model score: 60% weight on expected annual return, 40% on how
    far the price sits below its 52-week high (room to recover)."""
    price = STOCK_PRICES[name]
    low, high = PRICE_RANGE_52W[name]
    rate = EXPECTED_ANNUAL_RETURN.get(name, DEFAULT_ANNUAL_RETURN)
    below_high = (high - price) / high
    range_position = (price - low) / (high - low)   # 0 = at low, 1 = at high
    score = 0.6 * rate * 100 + 0.4 * below_high * 100
    return {
        "Stock": name,
        "Price": price,
        "Exp. Return %": rate * 100,
        "Below 52w High %": below_high * 100,
        "Range Position": range_position,
        "Score": score,
    }


def ask_budget():
    raw = input("\nHow much money would you like to invest now in new shares?"
                " (press Enter to skip): ").strip()
    try:
        budget = float(raw)
        return budget if budget > 0 else None
    except ValueError:
        return None


def build_picks_report(budget=None):
    ranked = sorted((score_stock(n) for n in STOCK_PRICES),
                    key=lambda r: r["Score"], reverse=True)
    lines = [
        "=" * 70,
        f"TOP {TOP_PICKS} STOCKS TO CONSIDER NOW (model ranking on sample data)",
        "  Score = 60% expected yearly return + 40% distance below 52-week high",
        f"  {'#':<3}{'Stock':<12}{'Price':>10}{'Exp.Ret':>9}{'Below High':>12}{'Score':>8}",
    ]
    for i, r in enumerate(ranked, 1):
        marker = " <- pick" if i <= TOP_PICKS else ""
        lines.append(
            f"  {i:<3}{r['Stock']:<12}{money(r['Price']):>10}"
            f"{r['Exp. Return %']:>8.0f}%{r['Below 52w High %']:>11.1f}%"
            f"{r['Score']:>8.1f}{marker}"
        )

    lines.append("")
    for r in ranked[:TOP_PICKS]:
        zone = ("near its 52-week low" if r["Range Position"] < 0.33
                else "mid-range" if r["Range Position"] < 0.66
                else "near its 52-week high")
        lines.append(
            f"  {r['Stock']}: ~{r['Exp. Return %']:.0f}%/yr expected, trading"
            f" {r['Below 52w High %']:.0f}% below its high ({zone})."
        )

    if budget:
        share = budget / TOP_PICKS
        lines += ["", f"  Splitting {money(budget)} equally across the top {TOP_PICKS}:"]
        spent = 0.0
        for r in ranked[:TOP_PICKS]:
            qty = int(share // r["Price"])
            cost = qty * r["Price"]
            spent += cost
            lines.append(f"    {r['Stock']:<12} {qty:>5} shares  = {money(cost)}")
        lines.append(f"    Total spent: {money(spent)}   Left over: {money(budget - spent)}")

    lines.append("  Based only on the hardcoded sample prices above - not live data"
                 " and not financial advice.")
    return "\n".join(lines)


def add_scenario_values(holdings, rate, years):
    """Adds each holding's value under the custom scenario (also goes to CSV)."""
    label = f"@{rate:.1%} x {years:g}y"
    for h in holdings:
        value = round(h["Current Value"] * (1 + rate) ** years, 2)
        h[f"Value {label}"] = value
        h[f"Return {label}"] = round(value - h["Invested"], 2)
        h["_scenario_value"] = value


def build_report(holdings, scenario_rate, scenario_years):
    total_invested = sum(h["Invested"] for h in holdings)
    total_current = sum(h["Current Value"] for h in holdings)
    total_projected = sum(h["Projected Value"] for h in holdings)
    total_pl = total_current - total_invested
    total_pl_pct = total_pl / total_invested * 100 if total_invested else 0
    scenario_yearly = yearly_values(total_current, scenario_rate, scenario_years)
    scenario_final = scenario_yearly[-1][1]

    lines = [
        "=" * 70,
        f"PORTFOLIO REPORT  ({datetime.now():%Y-%m-%d %H:%M})",
        "=" * 70,
    ]
    for h in holdings:
        lines += [
            f"{h['Stock']}  x{h['Quantity']}",
            f"  Bought at          : ${h['Buy Price']:.2f} per share"
            f"  ->  Invested {money(h['Invested'])}",
            f"  Current price      : ${h['Current Price']:.2f} per share"
            f"  ->  Current amount {money(h['Current Value'])}",
            f"  Profit/Loss now    : {money(h['P/L'])} ({h['P/L %']:+.2f}%)",
            f"  Expected value at the end of each year"
            f" (~{h['Exp. Annual Return %']:.0f}%/yr, return vs. amount invested):",
            *yearly_table(h["_yearly"], h["Invested"]),
            f"  Target sell price: ${h['Target Sell Price']:.2f}  ->  {h['Advice']}",
            f"  Amount if sold at target   : {h['Quantity']} x"
            f" ${h['Target Sell Price']:.2f} = {money(h['Target Amount'])}"
            f"  (profit {money(h['Target Amount'] - h['Invested'])})",
            f"  Estimated amount after {h['Horizon (yrs)']:g} yrs:",
            f"    = current amount x (1 + rate) ^ years",
            f"    = {money(h['Current Value'])} x"
            f" (1 + {h['Exp. Annual Return %'] / 100:g}) ^ {h['Horizon (yrs)']:g}",
            f"    = {money(h['Current Value'])} x"
            f" {(1 + h['Exp. Annual Return %'] / 100) ** h['Horizon (yrs)']:.4f}",
            f"    = {money(h['Projected Value'])}",
            f"  Expected return = {money(h['Projected Value'])} -"
            f" {money(h['Invested'])} invested = {money(h['Projected Return'])}"
            f" ({h['Projected Return'] / h['Invested'] * 100:+.1f}%)",
            "-" * 70,
        ]

    lines += [
        f"TOTAL INVESTED      : {money(total_invested)}",
        f"TOTAL CURRENT VALUE : {money(total_current)}",
        f"TOTAL PROFIT/LOSS   : {money(total_pl)} ({total_pl_pct:+.2f}%)",
        f"PROJECTED VALUE     : {money(total_projected)}"
        f"  (return {money(total_projected - total_invested)}, each over its own horizon)",
        "=" * 70,
        f"YOUR SCENARIO: whole portfolio kept for {scenario_years:g} years"
        f" at {scenario_rate:.1%} per year",
        f"  Starting from current value {money(total_current)}",
        *yearly_table(scenario_yearly, total_invested),
        "",
        f"  {'Stock':<12} {'Invested':>14} {'Expected Value':>16} {'Expected Return':>16} {'Return %':>9}",
        *[
            f"  {h['Stock']:<12} {money(h['Invested']):>14}"
            f" {money(h['_scenario_value']):>16}"
            f" {money(h['_scenario_value'] - h['Invested']):>16}"
            f" {(h['_scenario_value'] - h['Invested']) / h['Invested'] * 100:>+8.1f}%"
            for h in holdings
        ],
        "",
        f"  Expected value at the end : {money(scenario_final)}",
        f"  Expected return           : {money(scenario_final - total_invested)}"
        f" ({(scenario_final - total_invested) / total_invested * 100:+.1f}%"
        f" on {money(total_invested)} invested)",
        f"  Money grows about {(1 + scenario_rate) ** scenario_years:.2f}x"
        f" in {scenario_years:g} years at {scenario_rate:.1%}.",
        "=" * 70,
        "Note: prices and return rates are sample values, not financial advice.",
    ]
    return "\n".join(lines)


def save_txt(report, filename="portfolio_report.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"Saved report to {filename}")


def save_csv(holdings, filename="portfolio_report.csv"):
    fields = [k for k in holdings[0] if not k.startswith("_")]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(holdings)
    print(f"Saved report to {filename}")


def main():
    print("=== Stock Portfolio Tracker ===")
    holdings = collect_portfolio()
    if not holdings:
        print("No holdings entered. Goodbye!")
        return

    scenario_rate, scenario_years = ask_scenario()
    add_scenario_values(holdings, scenario_rate, scenario_years)
    budget = ask_budget()
    report = (build_report(holdings, scenario_rate, scenario_years)
              + "\n" + build_picks_report(budget))
    print("\n" + report)

    choice = input("\nSave results? (txt / csv / both / no): ").strip().lower()
    if choice in ("txt", "both"):
        save_txt(report)
    if choice in ("csv", "both"):
        save_csv(holdings)


if __name__ == "__main__":
    main()
