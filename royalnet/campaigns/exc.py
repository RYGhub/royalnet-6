class ChallengeFailedError(Exception):
    """
    The data passed to the Campaign (or its async equivalent) failed the challenge.
    """
