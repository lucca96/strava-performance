from src.client import StravaClient


def get_all_activities(access_token=None, max_pages=1, per_page=30, client=None):
    client = client or StravaClient()
    activities = []
    for page in range(1, max_pages + 1):
        page_activities = client.get_summary_page(page, per_page=per_page)
        if not page_activities:
            break
        activities.extend(page_activities)
    return activities


def get_activity_details(activity_id, access_token=None, client=None):
    client = client or StravaClient()
    return client.get_activity_details(activity_id)


def get_streams(activity_id, access_token=None, client=None):
    client = client or StravaClient()
    return client.get_activity_streams(activity_id)
