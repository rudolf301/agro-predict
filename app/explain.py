from datetime import date

LANG_TEXTS = {
    "en": {
        "optimal": "Optimal planting date for {crop}: {date}.",
        "historical": "Historically, frost at this location after this date occurs only in {pct}% of years.",
        "forecast_ok": "The 14-day forecast shows low frost risk (avg {prob}%).",
        "forecast_risk": "The 14-day forecast shows elevated frost risk (avg {prob}%, {days} risk days for this crop).",
        "elevation": "At {elev} m elevation, soil warms slower than valley areas.",
        "crop_frost_none": "{crop} is frost-sensitive \u2014 any frost event can destroy the crop.",
        "crop_frost_low": "{crop} tolerates only light frost.",
        "crop_frost_moderate": "{crop} tolerates moderate frost after establishment.",
        "delay": "Consider delaying planting until forecast stabilizes.",
        "green": "Conditions are favorable for planting.",
        "yellow": "Conditions are borderline \u2014 monitor forecasts daily.",
        "red": "Do not plant now \u2014 frost risk is too high.",
    },
    "bs": {
        "optimal": "Optimalni datum sjetve za {crop}: {date}.",
        "historical": "Istorijski, mraz na ovoj lokaciji nakon ovog datuma javlja se samo u {pct}% godina.",
        "forecast_ok": "14-dnevna prognoza pokazuje nizak rizik od mraza (prosjek {prob}%).",
        "forecast_risk": "14-dnevna prognoza pokazuje povi\u0161en rizik od mraza (prosjek {prob}%, {days} rizi\u010dnih dana za ovu kulturu).",
        "elevation": "Na nadmorskoj visini od {elev} m, zemlji\u0161te se zagrijava sporije od dolinskih podru\u010dja.",
        "crop_frost_none": "{crop} je osjetljiva na mraz \u2014 svaki mraz mo\u017ee uni\u0161titi usjev.",
        "crop_frost_low": "{crop} podnosi samo lagani mraz.",
        "crop_frost_moderate": "{crop} podnosi umjereni mraz nakon razvoja.",
        "delay": "Razmislite o odga\u0111anju sjetve dok se prognoza ne stabilizira.",
        "green": "Uslovi su povoljni za sjetvu.",
        "yellow": "Uslovi su grani\u010dni \u2014 pratite prognoze dnevno.",
        "red": "Ne sijte sada \u2014 rizik od mraza je previsok.",
    },
}


def build_explanation(prediction: dict, lang: str = "en") -> list[str]:
    t = LANG_TEXTS.get(lang, LANG_TEXTS["en"])
    bullets: list[str] = []

    rec = prediction["recommended_planting"]
    crop = prediction["crop"]
    risk = prediction["risk"]
    loc = prediction["location"]

    if rec.get("date"):
        bullets.append(
            t["optimal"].format(crop=crop["name_en"], date=rec["date"])
        )
        bullets.append(
            t["historical"].format(pct=round(rec["historical_frost_rate"] * 100, 1))
        )

    avg_prob_pct = round(risk["avg_frost_probability_14d"] * 100, 1)
    if risk["crop_frost_risk_days_14d"] == 0:
        bullets.append(t["forecast_ok"].format(prob=avg_prob_pct))
    else:
        bullets.append(
            t["forecast_risk"].format(
                prob=avg_prob_pct, days=risk["crop_frost_risk_days_14d"]
            )
        )

    if loc["elevation_m"] >= 400:
        bullets.append(t["elevation"].format(elev=round(loc["elevation_m"])))

    tolerance_key = f"crop_frost_{crop['frost_tolerance']}"
    if tolerance_key in t:
        bullets.append(t[tolerance_key].format(crop=crop["name_en"]))

    bullets.append(t[risk["traffic_light"]])

    if risk["traffic_light"] == "red":
        bullets.append(t["delay"])

    return bullets
