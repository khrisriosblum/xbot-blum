
import time
from .settings import settings

def post_to_x(text: str) -> dict:
    """
    Publish a tweet to X (formerly Twitter) using the Twitter API v2.

    If the ``DRY_RUN`` setting is enabled, this function will simply log the
    message and return without making any API requests. Otherwise it sleeps
    ``SLEEP_BEFORE_PUBLISH`` seconds to allow URL previews to generate and
    then attempts to publish the tweet.

    On success, a dictionary with ``{"status": "ok", "id": "..."}`` is
    returned.  If a dry‐run was performed, ``{"status": "dry_run"}`` is
    returned.  On failure, ``{"status": "error", "error": "..."}`` is
    returned with the associated exception message.

    The function uses ``tweepy.Client`` (API v2) with OAuth 1.0a user context.
    The previous implementation relied on the deprecated v1.1
    ``update_status`` endpoint via ``tweepy.API``.  Basic X API access
    restricts most v1.1 endpoints and will respond with a 403 Forbidden error
    code 453 ("You currently have access to a subset of X API v2 endpoints and
    limited v1.1 endpoints only") when trying to post using v1.1.  Switching to
    the v2 ``create_tweet`` endpoint resolves this issue and is the
    recommended way to post tweets going forward【187664688831490†L89-L94】.  See
    the Tweepy documentation for details on using ``Client.create_tweet()``【290481613596620†L909-L975】.
    """
    # Honour dry‐run mode to prevent accidental posts
    if settings.DRY_RUN:
        print("[DRY_RUN] Would post:\n", text)
        # simulate network latency
        time.sleep(1)
        return {"status": "dry_run"}

    # Wait before publishing so that link previews can be generated
    wait_s = max(0, settings.SLEEP_BEFORE_PUBLISH)
    if wait_s:
        time.sleep(wait_s)

    try:
        import tweepy
        # Initialize Tweepy client for API v2 using OAuth 1.0a user context
        # A bearer token is not strictly required when the consumer and access
        # credentials are provided.  ``user_auth`` defaults to True, which
        # ensures user context is used for create_tweet.
        client = tweepy.Client(
            consumer_key=settings.X_API_KEY,
            consumer_secret=settings.X_API_SECRET,
            access_token=settings.X_ACCESS_TOKEN,
            access_token_secret=settings.X_ACCESS_SECRET,
        )
        # Make the API call to create the tweet
        response = client.create_tweet(text=text)
        # The response is a Tweepy Response object; extract the tweet ID
        tweet_id = None
        # The returned type may be a dict if return_type is set to dict.  Try to
        # extract the ID from the various possible structures.
        if isinstance(response, dict):
            tweet_id = response.get("data", {}).get("id")
        else:
            # For Tweepy Response objects, the data attribute holds the JSON
            data = getattr(response, "data", None)
            if isinstance(data, dict):
                tweet_id = data.get("id")
        return {"status": "ok", "id": str(tweet_id) if tweet_id else ""}
    except Exception as e:
        # Catch all exceptions and return an error message.  In addition to
        # network or authentication failures, a 403 Forbidden error may be
        # returned if your account does not have the required access level for
        # posting tweets.  In that case please ensure your X developer app is
        # associated with a project and has write permissions enabled, and that
        # your plan includes access to the manage Tweets endpoint【187664688831490†L60-L91】.
        return {"status": "error", "error": str(e)}
