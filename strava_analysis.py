import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Note: This script reads the Strava API access token from the
# STRAVA_ACCESS_TOKEN environment variable. Before running the script,
# set this variable in your environment to a valid access token with
# at least the `activity:read` scope.


def get_activities(access_token: str, per_page: int = 200, page: int = 1):
    """Fetch a single page of activities from Strava."""
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": per_page, "page": page}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_all_activities(access_token: str):
    """Fetch all activities by iterating through paginated results."""
    all_activities = []
    page = 1
    while True:
        activities = get_activities(access_token, page=page)
        if not activities:
            break
        all_activities.extend(activities)
        page += 1
    return all_activities


def activities_to_dataframe(activities: list) -> pd.DataFrame:
    """Convert Strava activities list to a pandas DataFrame."""
    df = pd.json_normalize(activities)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["start_date_local"] = pd.to_datetime(df["start_date_local"])
    return df


def plot_distance_over_time(df: pd.DataFrame):
    """Plot total distance over time."""
    df["distance_km"] = df["distance"] / 1000.0
    df["date"] = df["start_date_local"].dt.date
    daily_distance = df.groupby("date")["distance_km"].sum()
    plt.figure(figsize=(10, 5))
    daily_distance.plot()
    plt.xlabel("Date")
    plt.ylabel("Distance (km)")
    plt.title("Daily Distance Over Time")
    plt.tight_layout()
    plt.show()


def plot_activity_type_distribution(df: pd.DataFrame):
    """Plot distribution of activity types."""
    plt.figure(figsize=(8, 4))
    sns.countplot(x="type", data=df)
    plt.xlabel("Activity Type")
    plt.ylabel("Count")
    plt.title("Distribution of Activity Types")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def calculate_fastest_times(df: pd.DataFrame, distance_km: float) -> float:
    """Estimate the fastest completion time (in seconds) for a given distance.

    The estimation is based on the average pace of each activity (moving time / distance).
    Only activities with at least the specified distance are considered.
    """
    subset = df[df["distance"] >= distance_km * 1000].copy()
    if subset.empty:
        return None
    subset["pace_sec_per_km"] = subset["moving_time"] / (subset["distance"] / 1000)
    subset["est_time_sec"] = subset["pace_sec_per_km"] * distance_km
    return subset["est_time_sec"].min()


def plot_fastest_times(df: pd.DataFrame):
    """Plot estimated fastest 5K and 10K times from the activity data."""
    fastest_5k_sec = calculate_fastest_times(df, 5)
    fastest_10k_sec = calculate_fastest_times(df, 10)
    labels = ["5 km", "10 km"]
    secs_list = [fastest_5k_sec, fastest_10k_sec]
    times_min = [(s / 60.0) if s is not None else 0 for s in secs_list]
    plt.figure(figsize=(6, 4))
    sns.barplot(x=labels, y=times_min)
    plt.ylabel("Time (minutes)")
    plt.title("Estimated Fastest 5K and 10K Times")
    plt.tight_layout()
    plt.show()
    for label, secs in zip(labels, secs_list):
        if secs is not None:
            td = pd.to_timedelta(secs, unit='s')
            print(f"Estimated fastest {label}: {td}")
        else:
            print(f"No activities long enough for {label}.")


def main():
    """Main function to fetch activities and generate visualisations."""
    access_token = os.getenv("STRAVA_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("STRAVA_ACCESS_TOKEN environment variable not set.")
    activities = get_all_activities(access_token)
    df = activities_to_dataframe(activities)
    print(f"Fetched {len(df)} activities from Strava.")
    plot_distance_over_time(df)
    plot_activity_type_distribution(df)
    plot_fastest_times(df)


if __name__ == "__main__":
    main()
