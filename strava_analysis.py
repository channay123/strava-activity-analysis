import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Strava API credentials
CLIENT_ID = 50635
CLIENT_SECRET = "e5d66dcc2d6d76c08c2e946c13758c4060ab7113"
ACCESS_TOKEN = "e5a1f6df283ce68318bb7fa8caf4cfc314560acb"

# Note: The provided access token has read scope and expires on 2025-07-31. After it expires,
# you will need to refresh or generate a new token via the Strava API.
# See https://developers.strava.com/docs/getting-started/ for more details.

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
    # Convert date strings to datetime objects
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["start_date_local"] = pd.to_datetime(df["start_date_local"])
    return df


def plot_distance_over_time(df: pd.DataFrame):
    """Plot total distance over time."""
    # Convert distance from meters to kilometers
    df["distance_km"] = df["distance"] / 1000.0
    # Extract date from local start time
    df["date"] = df["start_date_local"].dt.date
    # Aggregate distance by date
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


def main():
    """Main function to fetch activities and generate visualizations."""
    activities = get_all_activities(ACCESS_TOKEN)
    df = activities_to_dataframe(activities)
    print(f"Fetched {len(df)} activities from Strava.")
    # Generate visualizations
    plot_distance_over_time(df)
    plot_activity_type_distribution(df)


if __name__ == "__main__":
    main()
