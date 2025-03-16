def calc_distance(predicted_drivers: list[str], point_scorers: list[str]) -> float | None:
    if not point_scorers:
        return None

    n = len(point_scorers)
    predicted = predicted_drivers[:n]

    distance = 0
    for ix, name in enumerate(point_scorers):
        try:
            jy = predicted.index(name)

        except ValueError:
            jy = n

        distance += abs(ix - jy)

    return distance / sum(max(k, n - k) for k in range(n))
