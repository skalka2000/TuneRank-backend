import numpy as np

def get_current_user_id():
    # Stub for now — replace with real user ID from auth later
    return 1


def calculate_weighted_average(songs, power: float = 1.0):
    numerator = 0.0
    denominator = 0.0

    for song in songs:
        if song.rating is None:
            continue

        base_weight = 0.5 if song.is_interlude else 1.0
        weight = base_weight * (max(song.rating, 6) ** power)

        numerator += song.rating * weight
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