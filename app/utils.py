import numpy as np
from fastapi import Request

RATING_FLOOR = 6.0
RATING_CEILING = 10.0

def get_current_user_id(request: Request):
    user_id = request.query_params.get("user_id")
    return int(user_id) if user_id else 1

def calculate_weighted_average(
    songs,
    power: float = 1.0,
    interlude_weight: float = 0.5,
    epic_weight: float = 2.0,
):
    numerator = 0.0
    denominator = 0.0

    for song in songs:
        if song.rating is None:
            continue

        st = getattr(song, "song_type", "song")

        if st == "interlude":
            base_weight = interlude_weight
        elif st == "epic":
            base_weight = epic_weight
        else:
            base_weight = 1.0
        
        r = song.rating
        r_for_weight = min(max(r, RATING_FLOOR), RATING_CEILING)

        weight = base_weight * (r_for_weight ** power)

        numerator += r * weight
        denominator += weight

    return round(numerator / denominator, 2) if denominator else None


def apply_logistic_normalization(rating, greatness_threshold: float = 8.0, scaling_factor: float = 0.3, steep_factor: float = 3):

    def rescale_linear(r, mu=greatness_threshold):
        if r == mu:
            y=mu
        elif r > mu:
            y = mu + ((r - mu) / (10 - mu)) * (10 - mu)
        else:
            y = (r / mu) * mu
        return y
    
    def logistic_scaling(r, mu=greatness_threshold, steep_factor = steep_factor):
        right_steep = steep_factor
        left_steep = steep_factor*(10-mu)/mu
        if r < mu:
            y = 1 + 2*(mu-1) / (1 + np.exp(-left_steep * (r - mu)))
        elif r > mu:
            y = mu - (10 - mu) + 2*(10 - mu) / (1 + np.exp(-right_steep * (r - mu)))
        else:
            y = mu
        return y
    
    if scaling_factor == 0:
        return rating
    
    linear_scaled = rescale_linear(rating)
    logistic_scaled = logistic_scaling(rating)
    final_scaled = scaling_factor * logistic_scaled + (1-scaling_factor) * linear_scaled
    return final_scaled