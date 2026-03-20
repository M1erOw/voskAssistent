def checkSimilar(action,template):
    S = (1 << len(action)) - 1
    block = {}
    block_get = block.get
    x = 1
    for ch1 in action:
        block[ch1] = block_get(ch1, 0) | x
        x <<= 1

    for ch2 in template:
        Matches = block_get(ch2, 0)
        u = S & Matches
        S = (S + u) | (S - u)

    res = bin(S)[-len(action) :].count("0")
    maximum = len(action) + len(template)
    dist = maximum - 2 * res
    norm_dist = dist / maximum if maximum else 0
    norm_sim = 1.0 - norm_dist
    return norm_sim