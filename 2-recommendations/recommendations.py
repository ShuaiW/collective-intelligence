#!/usr/bin/python

"""
A program that makes recommendations.
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
    Computes a distance-based similarity score for p1 and p2.

    :param: prefs: a user-centric or item-centric dict
    :param: p1: string name of one person
    :param: p2: string name of another person
    :return: a distance-based similarity score (0 < score < 1;
        higher -> more similar)
    """
    shared_item = [item for item in prefs[p1] if item in prefs[p2]]
    # No rating in common, return 0
    if len(shared_item) == 0: 
        return 0
    sum_of_squares = sum((prefs[p1][item] - prefs[p2][item])**2
                         for item in shared_item)
    return 1 / (1 + sum_of_squares)


def sim_pearson(prefs, p1, p2):
    """
    Computes Pearson correlation coefficient for p1 and p2.

    :param: prefs: a user-centric or item-centric dict
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
    p1_sum = sum(prefs[p1][item] for item in shared_item)
    p2_sum = sum(prefs[p2][item] for item in shared_item)
    # Sum up the squares
    p1_sum_sq = sum(prefs[p1][item]**2 for item in shared_item)
    p2_sum_sq = sum(prefs[p2][item]**2 for item in shared_item)
    # Sum up the products
    sum_product = sum(prefs[p1][item] * prefs[p2][item]
                      for item in shared_item)
    # Calculate Pearson score
    num_shared_item = len(shared_item)
    numerator = sum_product - (p1_sum * p2_sum / num_shared_item)
    denominator = sqrt((p1_sum_sq - p1_sum**2 / num_shared_item) *
                       (p2_sum_sq - p2_sum**2 / num_shared_item))
    if denominator == 0: 
        return 0
    return numerator / denominator


def top_matches(prefs, person, n=5, similarity=sim_pearson):
    """
    Computes the top n matches for person from the pref dictionary.

    :param: prefs: a user-centric or item-centric dict
    :param: person: string name of one person
    :param: n: number of matches; default -> 5
    :param: similarity: similarity metrics; default=pearson coefficient
    :return: a list of tuples (similarity socre, name)
    """
    sim_list = [(similarity(prefs, person, other), other)
                for other in prefs if other != person]
    sim_list.sort(reverse=True)
    return sim_list[:n]


def user_based_recommend(prefs, person, similarity=sim_pearson):
    """
    Recommends items to user with item-based methods.

    :param: prefs: a user-centric or item-centric dict
    :param: person: string name of one person
    :param: similarity: similarity metrics; default=pearson coefficient
    :return: a list of tuples (estimated rating, recommended item)
    """
    rating_by_sim_total = {}
    sim_score_total = {}

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
                rating_by_sim_total.setdefault(item, 0)
                rating_by_sim_total[item] += prefs[other][item] * sim_score
                # sum of similarities
                sim_score_total.setdefault(item, 0)
                sim_score_total[item] += sim_score

    rankings = [(total / sim_score_total[item], item)
                for item, total in rating_by_sim_total.items()]
    rankings.sort(reverse=True)
    return rankings


def transform_prefs(prefs):
    """
    Transforms a dict of format between user-centric and item-centric.

    :param: prefs: a user-centric or item-centric dict
    :return: a item-centric dict if input is user-centric; 
        user-centric otherwise
    """
    transformed = {}
    for person in prefs:
        for item in prefs[person]:
            transformed.setdefault(item, {})
            # flip item and person
            transformed[item][person] = prefs[person][item]
    return transformed

# item-bssed dictionary
movies = transform_prefs(critics)


### Item-based filtering: comparisons between items will not change as often
### as comparison between users. This means it can be done at low-traffic 
### times or on a computer separate from the main application

def sim_items_base(prefs, n=10):
    """
    Creates a dictionary of items and thier top n similar items.

    Note: This function needs to be run more often early on when the user base
    and number of rating is small. As the user base grows, the scores will 
    become more stable.

    :param: prefs: a user-centric dictionary
    :param: n: optional, the number of most similar items (default=10)
    :return: a dictionary of items and their most similar items
    """
    item_base = {}   
    # Invert the preference matrix to be item-centric
    item_prefs = transform_prefs(prefs)
    c = 0
    for item in item_prefs:
        # Status update for large datasets
        c += 1
        if c % 100 == 0:
            print "{0} / {1}".format(c, len(item_prefs))
        # Find the n most similar items to this one
        scores = top_matches(item_prefs, item, n=n, similarity=sim_distance)
        item_base[item] = scores
    return item_base
    
    
def item_based_recommend(prefs, sim_item_base, user):
    """
    Recommends items to user with item-based methods.
    (Don't have to calculate the similarities scores for all the other critics
     because the item similarity dataset was built in advance)
    
    :param: prefs: a user-centric dictionary
    :param: sim_items_base: a similar items base
    :param: user: a string user name
    :return: a list of tuples (estimated score, recommended item)
    """
    user_rating = prefs[user]
    rating_by_sim_total = {}
    sim_score_total = {}  
    # loop over items rated by this user
    for (item, rating) in user_rating.items():
        # loop over items similar to this one
        for (sim_score, item2) in sim_item_base[item]:
            if item2 in user_rating:
                continue        # ignore if user has rated item2
            # weighted sum of rating by similartiy
            rating_by_sim_total.setdefault(item2, 0)
            rating_by_sim_total[item2] += rating * sim_score            
            # sum of all similarities
            sim_score_total.setdefault(item2, 0)
            sim_score_total[item2] += sim_score          
    # divide weighted sum by sum
    rankings = [(score / sim_score_total[item], item)
                for item, score in rating_by_sim_total.items()]
    rankings.sort(reverse=True)
    return rankings
            
        