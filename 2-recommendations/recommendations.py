# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 19:35:30 2014

@author: shuaiwang
"""

from math import sqrt


# A dictionary of movie critics and their ratings of a small set of movies
critics = {
    'Lisa Rose': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Returns': 3.5,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0,
    },
    'Gene Seymour': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5,
        'Superman Returns': 5.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 3.5,
    },
    'Michael Phillips': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.0,
        'Superman Returns': 3.5,
        'The Night Listener': 4.0,
    },
    'Claudia Puig': {
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'The Night Listener': 4.5,
        'Superman Returns': 4.0,
        'You, Me and Dupree': 2.5,
    },
    'Mick LaSalle': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0,
        'Superman Returns': 3.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 2.0,
    },
    'Jack Matthews': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'The Night Listener': 3.0,
        'Superman Returns': 5.0,
        'You, Me and Dupree': 3.5,
    },
    'Toby': {'Snakes on a Plane': 4.5,
             'You, Me and Dupree': 1.0,
             'Superman Returns': 4.0
             }}


def sim_distance(prefs, p1, p2):
    """
    Given a dict of person, items and ratings, and two names p1, p2,
    returns a distance-based similarity score for p1 and p2.

    :param: prefs: a dict of movie critics and their rating of moives
    :param: p1: string name of one person
    :param: p2: string name of another person
    :return: a distance-based similarity score (0 < score < 1;
        higher -> more similar)
    """
    shared_item = [item for item in prefs[p1] if item in prefs[p2]]

    # no rating in common, return 0
    if len(shared_item) == 0:
        return 0

    sum_of_squares = sum((prefs[p1][item] - prefs[p2][item])**2
                         for item in shared_item)

    return 1 / (1 + sum_of_squares)


def sim_pearson(prefs, p1, p2):
    """
    Given a dict of person, items and ratings, and two names p1, p2,
    returns the Pearson correlation coefficient for p1 and p2.

    :param: prefs: a dict of movie critics and their rating of moives
    :param: p1: string name of one person
    :param: p2: string name of another person
    :return: Pearson correlation coefficient for p1 and p2
        (-1 < coefficient < 1; 1 means two persons have same rating
        for every item)
    """
    shared_item = [item for item in prefs[p1] if item in prefs[p2]]

    if len(shared_item) == 0:
        return 0

    # Add up all the preferences
    p1sum = sum(prefs[p1][item] for item in shared_item)
    p2sum = sum(prefs[p2][item] for item in shared_item)

    # Sum up the squares
    p1sumsq = sum(prefs[p1][item]**2 for item in shared_item)
    p2sumSq = sum(prefs[p2][item]**2 for item in shared_item)

    # Sum up the products
    sum_product = sum(prefs[p1][item] * prefs[p2][item]
                      for item in shared_item)

    # Calculate Pearson score
    num_shared_item = len(shared_item)
    numerator = sum_product - (p1sum * p2sum / num_shared_item)
    denominator = sqrt((p1sumsq - p1sum**2 / num_shared_item) *
                       (p2sumSq - p2sum**2 / num_shared_item))

    if denominator == 0:
        return 0

    return numerator / denominator


def top_matches(prefs, person, n=5, similarity=sim_pearson):
    """
    Given a dict of person, items and ratings, and a person's name,
    returns the top n matches for person from the pref dictionary.

    :param: prefs: a dict of movie critics and their rating of moives
    :param: person: string name of one person
    :param: n: number of matches; default -> 5
    :param: similarity: similarity metrics; default -> pearson coefficient
    :return: a list of tuples (similarity socre, name)
    """
    sim_list = [(similarity(prefs, person, other), other)
                for other in prefs if other != person]
    sim_list.sort(reverse=True)
    return sim_list[:n]


def recommend(prefs, person, similarity=sim_pearson):
    """
    Given a dict of person, items, and ratings, and a person's name,
    returns recommendations for this person by using a weighted average
    of every other user's rankings.

    :param: prefs: a dict of movie critics and their rating of moives
    :param: person: string name of one person
    :param: similarity: similarity metrics; default -> pearson coefficient
    :return: a list of tuples (estimated rating of an item, item)
    """
    totals = {}
    sim_sums = {}

    for other in prefs:
        if other == person:
            continue  # don't compare to oneself
        sim_score = similarity(prefs, person, other)
        if sim_score <= 0:
            continue   # ignore scores of zero or lower
        for item in prefs[other]:
            # only find items this person hasn't got yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # other's rating * sim_score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim_score
                # sum of similarities
                sim_sums.setdefault(item, 0)
                sim_sums[item] += sim_score

    rankings = [(total / sim_sums[item], item)
                for item, total in totals.items()]
    rankings.sort(reverse=True)
    return rankings


def transform_prefs(prefs):
    """
    Takes a dict of format {person: {item: rating}} and transform it into
    {item: {person: rating}}

    :param: prefs: a dict of movie critics and their rating of moives
    :return: a transformed dict where the key is item instead of person
    """
    results = {}
    for person in prefs:
        for item in prefs[person]:
            results.setdefault(item, {})
            # flip item and person
            results[item][person] = prefs[person][item]
    return results


movies = transform_prefs(critics)
