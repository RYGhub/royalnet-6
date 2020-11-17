from ..exc import RoyalnetException


class CampaignsError(RoyalnetException):
    """
    An error related to the campaigns module.
    """


class ChallengeFailedError(CampaignsError):
    """
    The data passed to the Campaign (or its async equivalent) failed the challenge.
    """


__all__ = (
    "CampaignsError",
    "ChallengeFailedError",
)
