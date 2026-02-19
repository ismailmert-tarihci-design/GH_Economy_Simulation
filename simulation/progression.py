"""
Progression and gating logic for the Bluestar Economy Simulator.

Handles card level progression, gating calculations, and unlock schedules.
"""

from typing import Dict

from simulation.models import Card, CardCategory, ProgressionMapping


def get_max_unique_level(avg_shared_level: float, mapping: ProgressionMapping) -> int:
    """
    Determine the maximum unique card level allowed based on average shared level.

    Uses floor lookup: finds the highest shared_level <= avg_shared_level
    and returns the corresponding unique level.

    Args:
        avg_shared_level: Average level of shared cards (0-100)
        mapping: ProgressionMapping with shared_levels and unique_levels lists

    Returns:
        Maximum unique level allowed (gated)

    Example:
        If mapping = {1:1, 5:2, 10:3} and avg_shared_level=12,
        floor lookup returns key=10, so returns 3
    """
    if not mapping.shared_levels or not mapping.unique_levels:
        return 1

    # Find the highest shared_level that is <= avg_shared_level
    applicable_level = None
    for shared_level in mapping.shared_levels:
        if shared_level <= avg_shared_level:
            applicable_level = shared_level
        else:
            break

    # If no level found (avg_shared_level < min level), return first unique level
    if applicable_level is None:
        return mapping.unique_levels[0]

    # Get index of applicable level and return corresponding unique level
    idx = mapping.shared_levels.index(applicable_level)
    return mapping.unique_levels[idx]


def get_equivalent_shared_level(
    avg_unique_level: float, mapping: ProgressionMapping
) -> float:
    """
    Convert an average unique card level to its equivalent shared level
    using the progression mapping (reverse lookup).

    The mapping defines pairs: (shared_level, unique_level). This function
    interpolates: given a unique level, return what shared level it corresponds to.

    Uses linear interpolation between mapping entries for smooth scoring.

    Args:
        avg_unique_level: Average level of unique cards (1-10)
        mapping: ProgressionMapping with shared_levels and unique_levels lists

    Returns:
        Equivalent shared level (1-100 scale) for use in gap calculations.

    Example:
        Mapping: {1:1, 10:2, 20:3, ...}
        avg_unique_level=1.5 → interpolates between (1,1) and (10,2):
            fraction = (1.5-1)/(2-1) = 0.5
            result = 1 + 0.5*(10-1) = 5.5
    """
    if not mapping.shared_levels or not mapping.unique_levels:
        return 1.0

    shared = mapping.shared_levels
    unique = mapping.unique_levels

    # Clamp to mapping range
    if avg_unique_level <= unique[0]:
        return float(shared[0])
    if avg_unique_level >= unique[-1]:
        return float(shared[-1])

    # Find the two mapping entries that bracket avg_unique_level
    for i in range(len(unique) - 1):
        if unique[i] <= avg_unique_level <= unique[i + 1]:
            # Linear interpolation
            u_lo, u_hi = unique[i], unique[i + 1]
            s_lo, s_hi = shared[i], shared[i + 1]
            if u_hi == u_lo:
                return float(s_lo)
            fraction = (avg_unique_level - u_lo) / (u_hi - u_lo)
            return s_lo + fraction * (s_hi - s_lo)

    # Fallback (shouldn't reach here due to clamping)
    return float(shared[-1])


def compute_progression_score(card: Card, mapping: ProgressionMapping) -> float:
    """
    Compute normalized progression score for a card [0, 1].

    - Shared cards: level / 100
    - Unique cards: level / 10

    Args:
        card: Card object with level and category
        mapping: ProgressionMapping (for potential max levels)

    Returns:
        Normalized score in [0, 1] range
    """
    if card.category == CardCategory.UNIQUE:
        return min(card.level / 10.0, 1.0)
    else:
        return min(card.level / 100.0, 1.0)


def compute_mapping_aware_score(
    cards: list[Card], category: CardCategory, mapping: ProgressionMapping
) -> float:
    """
    Compute progression score on the SHARED scale [0, 1] for any category.

    Unlike compute_progression_score which uses independent scales (shared=level/100,
    unique=level/10), this projects unique progression onto the shared scale using
    the progression mapping for apples-to-apples comparison in the gap formula.

    Shared cards: avg_level / 100 (unchanged)
    Unique cards: get_equivalent_shared_level(avg_level) / 100

    This ensures the gap calculation in decide_rarity() correctly detects when
    one category is ahead per the progression mapping relationship.
    """
    cat_cards = [c for c in cards if c.category == category]
    if not cat_cards:
        return 0.0

    avg_level = sum(c.level for c in cat_cards) / len(cat_cards)

    if category == CardCategory.UNIQUE:
        equiv_shared = get_equivalent_shared_level(avg_level, mapping)
        return min(equiv_shared / 100.0, 1.0)
    else:
        return min(avg_level / 100.0, 1.0)


def compute_category_progression(
    cards: list[Card], category: CardCategory, mapping: ProgressionMapping
) -> float:
    """
    Compute average progression score across cards of a specific category.

    Args:
        cards: List of Card objects
        category: CardCategory to filter on
        mapping: ProgressionMapping for score computation

    Returns:
        Average progression score [0, 1] for the category, or 0 if no cards
    """
    category_cards = [c for c in cards if c.category == category]

    if not category_cards:
        return 0.0

    scores = [compute_progression_score(card, mapping) for card in category_cards]
    return sum(scores) / len(scores)


def can_upgrade_unique(
    card: Card, avg_shared_level: float, mapping: ProgressionMapping
) -> bool:
    """
    Check if a unique card can be upgraded without exceeding gating limit.

    Args:
        card: Unique card to check
        avg_shared_level: Current average shared card level
        mapping: ProgressionMapping for gating calculation

    Returns:
        True if card.level < max_allowed_level, False otherwise
    """
    if card.category != CardCategory.UNIQUE:
        raise ValueError("can_upgrade_unique only works with UNIQUE cards")

    max_allowed = get_max_unique_level(avg_shared_level, mapping)
    return card.level < max_allowed


def get_unlocked_unique_count(day: int, schedule: Dict[int, int]) -> int:
    """
    Calculate total unlocked unique cards based on unlock schedule.

    Sums all schedule entries where day_key <= current day.

    Args:
        day: Current day in simulation
        schedule: Dictionary mapping day keys to unlock counts
                  Example: {1: 8, 30: 1, 60: 1}

    Returns:
        Total number of unlocked unique cards by this day
    """
    total = 0
    for day_key, unlock_count in schedule.items():
        if day_key <= day:
            total += unlock_count
    return total
