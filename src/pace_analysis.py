from src.analysis import analyze_pace_from_laps, format_pace
from src.client import StravaClient


def get_laps(activity_id, access_token=None, client=None):
    client = client or StravaClient()
    return client.get_activity_laps(activity_id)


def analyze_pace(activity_id, access_token=None, verbose=True, details=None, laps=None, client=None):
    client = client or StravaClient()
    if details is None:
        details = client.get_activity_details(activity_id)
    if laps is None:
        laps = client.get_activity_laps(activity_id)

    result, missing = analyze_pace_from_laps(details, laps)
    if missing:
        if verbose:
            print("Sem dados suficientes para pace:", ", ".join(missing))
        return None

    if verbose:
        print("\n=== ANALISE DE PERFORMANCE (PACE) ===\n")
        print("Pace medio:", result["pace_avg"])

        print("\nSplits:")
        for i, pace in enumerate(result["splits_sec_km"]):
            print(f"KM {i + 1}: {format_pace(pace)}")

        print(f"\nConsistencia (score 0-10): {result['consistency_score']:.1f}")
        print(f"Drift: {result['pace_drift_sec_km']:.1f} seg/km")

        if result.get("pace_interpretation"):
            print("\nInterpretacao:")
            for item in result["pace_interpretation"].split(" | "):
                print("-", item)

        if result.get("pace_insights"):
            print("\nInsights:")
            for item in result["pace_insights"].split(" | "):
                print("-", item)

    return result
