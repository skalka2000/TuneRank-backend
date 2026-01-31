def calculate_weighted_average(songs, power: float = 1.0):
    numerator = 0.0
    denominator = 0.0

    for song in songs:
        if song.rating is None:
            continue

        base_weight = 0.5 if song.is_interlude else 1.0
        weight = base_weight * (song.rating ** power)

        numerator += song.rating * weight
        denominator += weight

    return round(numerator / denominator, 2) if denominator else None
