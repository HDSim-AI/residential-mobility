"""PSID survey fields to first-person facts.

Ported from the pipeline behind the published residential-mobility results, so personas built here
read the same way.

Two things were removed on the way out, both deliberate:

  Mappers for stated move intentions. PSID asks whether a family expects to move; that answer
  predicts the outcome directly, so it was already excluded from persona construction upstream and
  the mappers sat unused. They are not carried over, because a public package that contains them is
  a public package where someone will eventually call them.

  Nothing else. The remaining composition is unchanged, including how negative and missing codes
  render as no fact at all rather than as a guess.

The income-to-needs ratio deserves a note, since it is easy to read backwards. It divides family
income by the Census needs standard for that family's size and composition. A value of 1.0 sits at
the poverty line and 5.65 means comfortable. A high ratio is financial room, not financial stress.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import pandas as pd


KEY_COLUMNS_FOR_PERSONA = [
    "HOUSEID",
    "PERSONID",
    "AGE",
    "SEX",
    "RELATION_TO_HEAD",
    "EMPLOYMENT_STATUS",
    "WTR_COLLEGE_DEGREE",
    "DEGREE_TYPE",
    "YEARS_EDUCATION",
    "CURRENTLY_ENROLLED",
    "HEALTH_SELF",
    "HAD_COVID",
    "NUM_JOBS_PY",
    "ER82017",
    "ER82022",
    "ER82023",
    "ER82026",
    "ER82032",
    "ER82004",
    "ER82927",
    "ER85629",
    "ER85770",
    "ER85774",
    "ER85121",
    "ER85126",
    "ER82009",
    "ER84520",
    "ER84585",
    "ER84595",
    "ER84721",
    "ER84796",
    "ER85445",
    "ER85447",
    "ER85466",
    "ER85284",
    "ER85332",
    "ER85666",
    "ER85690",
    "ER85809",
    "ER85780",
    "ER85781",
]


def clean_float(val: Any) -> Optional[float]:
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def safe_int(val: Any) -> Optional[int]:
    c = clean_float(val)
    if c is None or c >= 999:
        return None
    return int(c)


def map_sex(code: Any) -> Optional[str]:
    c = clean_float(code)
    if c == 1:
        return "male"
    if c == 2:
        return "female"
    return None


def map_employment(code: Any) -> Optional[str]:
    mapping = {
        1: "working now",
        2: "temporarily laid off",
        3: "looking for work or unemployed",
        4: "retired",
        5: "permanently disabled",
        6: "keeping house",
        7: "a student",
        8: "other",
    }
    c = clean_float(code)
    if c is None or c >= 98:
        return None
    return mapping.get(int(c))


def map_relation_to_head(code: Any) -> str:
    """ER35103, verified against IND2023ER_formats.sas (FAM uses parallel codes).
    PSID 2023 codes include partner/cohabitor (22, 88), foster (38), in-laws (37, 47, 57),
    grandparents (66, 67, 68, 69), nieces/nephews (70, 71), uncles/aunts (72, 73), cousins (74, 75)."""
    c = clean_float(code)
    if c is None:
        return "a member of this household"
    ic = int(c)
    if ic == 10:
        return "the reference person (head) of this household"
    if ic == 20:
        return "the legal spouse of the household reference person"
    if ic == 22:
        return "the long-term cohabiting partner of the household reference person"
    if ic == 88:
        return "a first-year cohabitor of the household reference person"
    if ic in (30, 33):
        return "a child of the household reference person"
    if ic == 35:
        return "a child of the partner of the household reference person"
    if ic == 37:
        return "a son- or daughter-in-law of the household reference person"
    if ic == 38:
        return "a foster son or daughter of the household reference person"
    if ic == 83:
        return "a child of a first-year cohabitor of the household reference person"
    if ic in (40, 47, 48):
        return "a sibling (or sibling-in-law) of the household reference person"
    if ic in (50, 57, 58):
        return "a parent (or parent-in-law) of the household reference person"
    if ic in (60, 65):
        return "a grandchild or great-grandchild of the household reference person"
    if ic in (66, 67, 68, 69):
        return "a grandparent or great-grandparent of the household reference person"
    if ic in (70, 71):
        return "a niece or nephew of the household reference person"
    if ic in (72, 73):
        return "an uncle or aunt of the household reference person"
    if ic in (74, 75):
        return "a cousin of the household reference person"
    if ic == 90:
        return "the legal spouse of the household reference person (designated uncooperative for this wave)"
    return "another member of this household"


def map_marital(code: Any) -> Optional[str]:
    """ER82026, RP marital status. PSID 2023 codes: 1=Married, 2=Never married, 3=Widowed,
    4=Divorced/annulled, 5=Separated, 8=DK, 9=NA/refused."""
    c = clean_float(code)
    if c is None or c >= 8:
        return None
    m = {
        1: "married",
        2: "never married",
        3: "widowed",
        4: "divorced or annulled",
        5: "separated",
    }
    return m.get(int(c))


def map_tenure(code: Any) -> Optional[str]:
    c = clean_float(code)
    if c is None or c >= 98:
        return None
    if int(c) == 1:
        return "own or are buying the home"
    if int(c) == 5:
        return "rent the home"
    if int(c) == 8:
        return "have another housing arrangement"
    return None








def map_health(code: Any) -> Optional[str]:
    """Family-file self-rated health ladder (ER84520 RP / ER84721 SP).
    Codes: 1=Excellent, 2=Very good, 3=Good, 4=Fair, 5=Poor, 8=DK, 9=NA."""
    c = clean_float(code)
    if c is None or c >= 8:
        return None
    ladder = {1: "excellent health", 2: "very good health", 3: "good health", 4: "fair health", 5: "poor health"}
    return ladder.get(int(c))


def map_individual_health_good(code: Any) -> Optional[str]:
    """ER35188 ('HEALTH GOOD? 23'), binary in PSID 2023: 1=Yes in poor health, 5=No not in poor health.
    Different from family-file ladder; do not reuse map_health."""
    c = clean_float(code)
    if c is None or c >= 8:
        return None
    if int(c) == 1:
        return "is reported in poor health"
    if int(c) == 5:
        return "is reported not in poor health"
    return None


def map_degree_type(code: Any) -> Optional[str]:
    """
    Map PSID 2023 ER35135 (TYPE OF HIGHEST DEGREE).

    Verified against IND2023ER_formats.sas:
        1=Associate, 2=Bachelor, 3=Master, 4=Doctorate, 5=LLB/JD,
        6=MD/DDS/DVM/DO, 8=Honorary, 97=Other, 99=DK, 0=Inap.

    Returns None for Inap/DK/Honorary/Other so we don't emit ambiguous facts.
    """
    c = clean_float(code)
    if c is None or c <= 0 or c >= 97:
        return None
    ic = int(c)
    deg = {
        1: "an associate degree",
        2: "a bachelor's degree",
        3: "a master's degree",
        4: "a doctoral degree (PhD)",
        5: "a law degree (LLB/JD)",
        6: "a medical degree (MD, DDS, DVM, or DO)",
    }
    return deg.get(ic)


def map_rp_sp_education_fam(code: Any) -> Optional[str]:
    """Family-file completed-education years for RP / SP (ER85780 / ER85781).

    PSID format (FAM2023ER): 0='No grades of school', 1-17='Actual number of years',
    99='DK; NA', plus inap=0 for ER85781. NOT a degree-type ladder, must not call
    map_degree_type here (older versions of this map did, which produced bogus labels
    like 'a bachelor's degree' for `1 year of school`).
    """
    c = clean_float(code)
    if c is None:
        return None
    iv = int(c)
    if iv == 0:
        return "no formal grades of schooling"
    if iv >= 98:
        return None
    return years_education_label(c)


def years_education_label(yrs: Any) -> Optional[str]:
    """Convert ER35152 (YEARS COMPLETED EDUCATION) to a human phrase."""
    y = clean_float(yrs)
    if y is None or y <= 0 or y >= 99:
        return None
    iy = int(y)
    if iy < 9:
        return f"about {iy} years of formal schooling (less than high school)"
    if iy == 12:
        return "high school graduation (12 years of schooling)"
    if 9 <= iy <= 11:
        return f"about {iy} years of schooling (some high school)"
    if 13 <= iy <= 15:
        return f"about {iy} years of schooling (some college)"
    if iy == 16:
        return "16 years of schooling (typically a bachelor's degree)"
    if iy >= 17:
        return f"{iy} years of schooling (graduate-level)"
    return f"about {iy} years of schooling"


def map_beale_rurality(er85774: Any) -> Optional[str]:
    c = safe_int(er85774)
    if c is None:
        return None
    if c in (1, 2, 3):
        return "large or small metropolitan area (survey Beale code 1–3)"
    if c in (4, 5, 6):
        return "non-metropolitan area adjacent to a metro (Beale code 4–6)"
    if c in (7, 8, 9):
        return "rural or thinly settled area (Beale code 7–9)"
    return None


def income_to_needs_ratio_ctx(inc: Any, needs: Any) -> Optional[float]:
    """ER85629 (total family income 2022, dollars) ÷ ER85770 (census needs standard 2022, dollars).
    Negative income is legitimate (business losses), so allow any non-DK value."""
    ia = clean_float(inc)
    na = clean_float(needs)
    if ia is None or na is None or na <= 0 or ia >= 99999998:
        return None
    return float(ia / na)


def immigrant_supplement_flag(er82009: Any) -> Optional[int]:
    v = clean_float(er82009)
    if v is None:
        return None
    vid = int(v)
    if 3001 <= vid <= 3511 or 4001 <= vid <= 4851:
        return 1
    return 0


def map_race_rp(code: Any) -> Optional[str]:
    """ER85121, L40 RACE OF REFERENCE PERSON-MENTION 1. Codes: 1 White, 2 Black/African-American,
    3 American Indian/Alaska Native, 4 Asian, 5 Native Hawaiian/Pacific Islander, 7 Other, 9 DK/NA."""
    c = clean_float(code)
    if c is None or c == 9:
        return None
    m = {
        1: "White",
        2: "Black or African-American",
        3: "American Indian or Alaska Native",
        4: "Asian",
        5: "Native Hawaiian or Pacific Islander",
        7: "self-described as another race",
    }
    return m.get(int(c))


def map_ethnic_rp(code: Any) -> Optional[str]:
    """ER85126, L41 ETHNIC GROUP-RP. Codes: 1 American, 2 hyphenated, 3 national origin,
    4 Hispanic, 5 racial, 6 religious, 7 other, 9 DK/NA."""
    c = clean_float(code)
    if c is None or c == 9:
        return None
    m = {
        1: "an American identity",
        2: "a hyphenated American identity (e.g., African-American, Mexican-American)",
        3: "a national-origin identity (e.g., Irish, German, Iranian)",
        4: "a nonspecific Hispanic identity (e.g., Chicano, Latino)",
        5: "a race-based identity",
        6: "a religious identity",
        7: "another self-described identity",
    }
    return m.get(int(c))


def births_2021_count(er85809: Any) -> Optional[int]:
    """ER85809 - BIRTHS TO REF PERSON AND SPOUSE-2021. Codes: 0 None, 1 One, 2 Two, 3 Three,
    8 DK/NA, **9 = no Spouse/Partner in FU or not asked** (inapplicable, NOT a count).
    Returns the count (0-3) or None for DK/inapplicable."""
    c = clean_float(er85809)
    if c is None or c >= 8:
        return None
    return int(c)


def get_household_context(group_df: pd.DataFrame) -> Dict[str, Any]:
    """Shared context from first row of a household group (all rows share family fields)."""
    row = group_df.iloc[0]
    hh_size = safe_int(row.get("ER82017"))
    income = clean_float(row.get("ER85629"))
    own_rent = map_tenure(row.get("ER82032"))
    marital = map_marital(row.get("ER82026"))
    n_children = safe_int(row.get("ER82022"))
    y_child = safe_int(row.get("ER82023"))
    vehicles = safe_int(row.get("ER82927"))
    state_fips = safe_int(row.get("ER82004"))
    beale_label = map_beale_rurality(row.get("ER85774"))
    inc_needs = income_to_needs_ratio_ctx(row.get("ER85629"), row.get("ER85770"))
    immig = immigrant_supplement_flag(row.get("ER82009"))
    rp_layoff = clean_float(row.get("ER85445")) or 0.0
    sp_layoff = clean_float(row.get("ER85466")) or 0.0
    rp_un22 = clean_float(row.get("ER85447")) or 0.0
    rp_un21 = clean_float(row.get("ER85284")) or 0.0
    sp_un21 = clean_float(row.get("ER85332")) or 0.0
    cc_debt = clean_float(row.get("ER85666"))
    wealth = clean_float(row.get("ER85690"))
    rp_lung = clean_float(row.get("ER84585"))
    rp_arth = clean_float(row.get("ER84595"))
    sp_arth = clean_float(row.get("ER84796"))
    births_n = births_2021_count(row.get("ER85809"))
    race_label = map_race_rp(row.get("ER85121"))
    eth_label = map_ethnic_rp(row.get("ER85126"))

    ctx: Dict[str, Any] = {
        "hh_size": hh_size,
        "income": income,
        "own_rent_label": own_rent,
        "marital_label": marital,
        "num_children_fu": n_children,
        "age_youngest_child": y_child,
        "vehicle_count": vehicles,
        "state_fips": state_fips,
        "beale_label": beale_label,
        "income_to_needs_ratio": inc_needs,
        "immigrant_supplement": immig,
        "rp_layoff_weeks_2022": rp_layoff if rp_layoff > 0 else None,
        "sp_layoff_weeks_2022": sp_layoff if sp_layoff > 0 else None,
        "rp_unemp_weeks_2022": rp_un22 if rp_un22 > 0 else None,
        "rp_unemp_weeks_2021": rp_un21 if rp_un21 > 0 else None,
        "sp_unemp_weeks_2021": sp_un21 if sp_un21 > 0 else None,
        "credit_card_debt_imp": cc_debt,
        "wealth_no_equity_imp": wealth,
        "rp_lung_limit_activity": rp_lung,
        "rp_arthritis_limit_activity": rp_arth,
        "sp_arthritis_limit_activity": sp_arth,
        "births_2021_count": births_n,
        "race_rp_label": race_label,
        "ethnic_rp_label": eth_label,
    }
    for col in (
        "BH_TENURE_YEARS_2021",
        "BH_MOVE_COUNT_PRIOR_WAVES",
        "BH_INCOME_VOLATILITY_PRIOR",
        "BH_HHSIZE_DELTA_PRIOR_MAX",
    ):
        if col in row.index:
            v = row[col]
            if pd.notna(v):
                ctx[col.lower()] = v
    return ctx


def household_context_facts(ctx: Dict[str, Any], member_relation_code: Any = None) -> List[str]:
    """
    Narrated shared constraints (prepended to every member's fact list).

    Omits rooms, housing value/rent (post-move), move intent, move reasons, those carry leakage or duplicate tenure.
    """
    facts: List[str] = []
    rel = clean_float(member_relation_code)
    is_rp = rel is not None and int(rel) == 10
    is_sp = rel is not None and int(rel) in (20, 22, 90)
    if ctx.get("hh_size") is not None:
        facts.append(f"Household context: there are {ctx['hh_size']} people in this family unit.")
    sf = ctx.get("state_fips")
    if sf is not None:
        facts.append(f"Household context: residence state (FIPS code) is {sf}.")
    bl = ctx.get("beale_label")
    if bl:
        facts.append(f"Household context: locality type description — we {bl}.")
    if ctx.get("immigrant_supplement") == 1:
        facts.append(
            "Household context: the family identifiers indicate membership in PSID immigrant sample supplements."
        )
    if ctx.get("own_rent_label"):
        facts.append(f"Household context: the household {ctx['own_rent_label']}.")
    inc = ctx.get("income")
    if inc is not None and inc < 99999998:
        facts.append(f"Household context: total family income is about {int(inc)} dollars.")
    rn = ctx.get("income_to_needs_ratio")
    if rn is not None:
        facts.append(f"Household context: family income relative to census needs standard is about {rn:.2f}.")
    if ctx.get("vehicle_count") is not None:
        vc = ctx["vehicle_count"]
        facts.append(
            f"Household context: the household owns {vc} vehicle(s)."
            if vc != 0
            else "Household context: the household does not own a vehicle."
        )
    marital = ctx.get("marital_label")
    if marital:
        if is_rp:
            facts.append(f"My marital status is: {marital}.")
        elif is_sp:
            facts.append(f"I am the spouse/partner; the household's marital status is: {marital}.")
        else:
            facts.append(f"Household context: the household head's marital status is: {marital} (this refers to the head, not to me).")
    nc = ctx.get("num_children_fu")
    if nc is not None:
        facts.append(f"Household context: the family unit includes {nc} children.")
    yc = ctx.get("age_youngest_child")
    if yc is not None and 0 < yc < 999:
        facts.append(f"Household context: the youngest child in the unit is {yc} years old.")
    wk = ctx.get("rp_layoff_weeks_2022")
    if wk is not None and wk > 0:
        facts.append(f"Household context: the reference person had about {int(wk)} weeks laid off in 2022 (survey weeks).")
    wk = ctx.get("sp_layoff_weeks_2022")
    if wk is not None and wk > 0:
        facts.append(f"Household context: the spouse/partner had about {int(wk)} weeks laid off in 2022.")
    wk = ctx.get("rp_unemp_weeks_2022")
    if wk is not None and wk > 0:
        facts.append(f"Household context: the reference person was unemployed about {int(wk)} weeks in 2022.")
    wk = ctx.get("rp_unemp_weeks_2021")
    if wk is not None and wk > 0:
        facts.append(f"Household context: the reference person was unemployed about {int(wk)} weeks in 2021.")
    wk = ctx.get("sp_unemp_weeks_2021")
    if wk is not None and wk > 0:
        facts.append(f"Household context: the spouse/partner was unemployed about {int(wk)} weeks in 2021.")
    debt = ctx.get("credit_card_debt_imp")
    if debt is not None and 0 < debt < 99999998:
        facts.append(f"Household context: imputed revolving credit-card debt is about {int(debt)} dollars.")
    nw = ctx.get("wealth_no_equity_imp")
    if nw is not None and not (isinstance(nw, float) and math.isnan(nw)) and abs(nw) < 99999998:
        facts.append(f"Household context: imputed net wealth excluding home equity is about {int(nw)} dollars.")
    if ctx.get("rp_lung_limit_activity") == 1.0:
        facts.append(
            "Household context: the reference person reports a lung condition that limits normal activity."
        )
    if ctx.get("rp_arthritis_limit_activity") == 1.0:
        facts.append(
            "Household context: the reference person reports arthritis limiting normal activity."
        )
    if ctx.get("sp_arthritis_limit_activity") == 1.0:
        facts.append(
            "Household context: the spouse/partner reports arthritis limiting normal activity."
        )
    br = ctx.get("births_2021_count")
    if br is not None and br > 0:
        word = {1: "one birth", 2: "two births", 3: "three births"}.get(int(br), f"{int(br)} births")
        facts.append(
            f"Household context: the survey records {word} to the reference person or spouse/partner in 2021."
        )
    rc = ctx.get("race_rp_label")
    if rc:
        facts.append(f"Household context: the reference person's first-mentioned race is {rc}.")
    ec = ctx.get("ethnic_rp_label")
    if ec:
        facts.append(f"Household context: the reference person's ethnic identification is {ec}.")
    # Behavioral biography from earlier PSID waves (2019 + 2021, strictly pre-2023).
    # These come from the persona-only BH supplement (variable_plan.md §2.5); they are NOT
    # carried in the ML CSVs or in hh_summary.
    ten = ctx.get("bh_tenure_years_2021")
    if ten is not None and not (isinstance(ten, float) and math.isnan(float(ten))):
        t = float(ten)
        # Use neutral wording, let the number speak. Avoid loaded labels like "stable"
        # which the downstream LLM tends to over-weight as evidence against moving.
        if t >= 4.0:
            phrase = (
                "at least 4 years at the same address "
                "(the household did not change residence between the 2019 and 2021 PSID waves)"
            )
        elif t <= 0.0:
            phrase = "less than a year (the household had just moved during 2019–2021)"
        elif abs(t - round(t)) < 1e-6:
            phrase = f"about {int(round(t))} year(s)"
        else:
            phrase = f"about {t:.1f} years"
        # Keep the explicit "(prior-wave snapshot)" tag so the writer cannot
        # convert this into a present-tense claim about the current 2023 tenure.
        facts.append(
            f"Prior-wave snapshot (from the 2021 PSID survey, BEFORE the 2021–2023 outcome window): "
            f"the household's tenure at the current residence AS OF MID-2021 was {phrase}. "
            f"This is a pre-2023 historical fact about 2021; do NOT report it as the current tenure."
        )
    mc = ctx.get("bh_move_count_prior_waves")
    if mc is not None and not (isinstance(mc, float) and math.isnan(float(mc))):
        n = int(round(float(mc)))
        word = {0: "did not move", 1: "moved once", 2: "moved twice"}.get(n, f"moved {n} times")
        facts.append(
            f"Panel history (2017–2019 and 2019–2021 windows): the household {word} across those two prior waves."
        )
    ivol = ctx.get("bh_income_volatility_prior")
    if ivol is not None and not (isinstance(ivol, float) and math.isnan(float(ivol))):
        v = float(ivol)
        band = "low" if v < 0.25 else ("moderate" if v < 0.60 else "high")
        facts.append(
            f"Panel history (incomes 2018, 2020, 2022): family-income volatility "
            f"(coefficient of variation) was {v:.2f} — a {band} level of year-to-year variation."
        )
    hdc = ctx.get("bh_hhsize_delta_prior_max")
    if hdc is not None and not (isinstance(hdc, float) and math.isnan(float(hdc))):
        d = int(round(float(hdc)))
        if d == 0:
            phrase = "remained the same"
        else:
            phrase = f"changed by about {d} person(s)"
        facts.append(
            f"Panel history (2019 vs 2021 PSID waves): the family-unit size {phrase} between those two prior surveys."
        )
    return facts


def _education_facts_for_row(row: pd.Series) -> List[str]:
    """
    Emit at most ONE education fact per person to avoid contradictions.
    Priority: degree (if got college degree) > years_education label > family-file fallback.
    """
    facts: List[str] = []
    age = clean_float(row.get("AGE") if "AGE" in row else row.get("ER35104"))
    seq = safe_int(row.get("PERSONID") if "PERSONID" in row else row.get("ER35102"))
    deg_type = row.get("DEGREE_TYPE") if "DEGREE_TYPE" in row else row.get("ER35135")
    yrs = row.get("YEARS_EDUCATION") if "YEARS_EDUCATION" in row else row.get("ER35152")
    wtr_deg = clean_float(row.get("WTR_COLLEGE_DEGREE") if "WTR_COLLEGE_DEGREE" in row else row.get("ER35134"))

    if age is not None and age < 16:
        return facts

    deg_label = map_degree_type(deg_type)
    yrs_label = years_education_label(yrs)

    if wtr_deg == 1.0 and deg_label:
        facts.append(f"My highest degree is {deg_label}.")
    elif wtr_deg == 5.0 and yrs_label:
        facts.append(f"I have {yrs_label}; I do not have a college degree.")
    elif yrs_label:
        facts.append(f"I have {yrs_label}.")
    else:
        if seq == 1:
            fe = map_rp_sp_education_fam(row.get("ER85780"))
            if fe:
                facts.append(f"As the reference person, my education is {fe}.")
        elif seq == 2:
            fe = map_rp_sp_education_fam(row.get("ER85781"))
            if fe:
                facts.append(f"As the spouse/partner, my education is {fe}.")
    return facts


def generate_facts_list(row: pd.Series, hh_context: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Factual first-person bullet list for one person.
    Order: household context → identity → composition → work/education → health → mobility hints.
    """
    seq = safe_int(row.get("PERSONID") if "PERSONID" in row else row.get("ER35102"))
    rel = row.get("RELATION_TO_HEAD") if "RELATION_TO_HEAD" in row else row.get("ER35103")
    age = clean_float(row.get("AGE") if "AGE" in row else row.get("ER35104"))
    sex_code = row.get("SEX") if "SEX" in row else row.get("ER32000")
    sex = map_sex(sex_code)

    facts: List[str] = []
    if hh_context:
        facts.extend(household_context_facts(hh_context, member_relation_code=rel))

    facts.append(f"I am {map_relation_to_head(rel)}.")

    if age is not None and age < 999:
        if sex == "male":
            word = "boy" if age < 18 else "man"
        elif sex == "female":
            word = "girl" if age < 18 else "woman"
        else:
            word = "person"
        facts.append(f"I am a {int(age)}-year-old {word}.")
    elif sex:
        facts.append(f"I am {sex}.")

    emp = row.get("EMPLOYMENT_STATUS") if "EMPLOYMENT_STATUS" in row else row.get("ER35116")
    et = map_employment(emp)
    if et:
        facts.append(f"Regarding employment, I am {et}.")

    facts.extend(_education_facts_for_row(row))

    enrolled = clean_float(row.get("CURRENTLY_ENROLLED") if "CURRENTLY_ENROLLED" in row else row.get("ER35150"))
    if enrolled == 1.0:
        facts.append("I am currently enrolled in school.")

    nj = safe_int(row.get("NUM_JOBS_PY") if "NUM_JOBS_PY" in row else row.get("ER35221"))
    if nj is not None and nj > 0 and nj < 98:
        facts.append(f"I had {nj} job(s) in the prior year (survey report).")

    hself = map_individual_health_good(row.get("HEALTH_SELF") if "HEALTH_SELF" in row else row.get("ER35188"))
    if hself:
        facts.append(f"Regarding my health, the survey indicates this person {hself}.")
    if seq == 1:
        hrp = map_health(row.get("ER84520"))
        if hrp:
            facts.append(f"Regarding health (reference person 1–5 self-rated scale), the data indicate {hrp}.")
    elif seq == 2:
        hsp = map_health(row.get("ER84721"))
        if hsp:
            facts.append(f"Regarding health (spouse/partner 1–5 self-rated scale), the data indicate {hsp}.")

    cov = clean_float(row.get("HAD_COVID") if "HAD_COVID" in row else row.get("ER35199"))
    if cov == 1.0:
        facts.append("The survey indicates I had COVID-19.")
    elif cov == 5.0:
        facts.append("The survey indicates I did not have COVID-19.")

    return facts


def generate_individual_narrative(row: pd.Series, hh_context: Optional[Dict[str, Any]] = None) -> str:
    """Backward-compatible single string (joined facts)."""
    return " ".join(generate_facts_list(row, hh_context))
