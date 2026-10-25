"""HeatSense test configuration and Hypothesis profile registration."""

import os

from hypothesis import HealthCheck, settings

# Register dev profile for rapid local iteration
settings.register_profile("dev", max_examples=50)

# Register CI profile for deterministic, exhaustive property checking
settings.register_profile(
    "ci",
    max_examples=200,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)

# Select active profile via HYPOTHESIS_PROFILE environment variable (default: dev)
active_profile = os.getenv("HYPOTHESIS_PROFILE", "dev")
settings.load_profile(active_profile)
