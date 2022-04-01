import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
punctuation = set([',', '.', ':', ';', '?', '!', '&'])
non_informant_words = set(["course", "automation", "essay", "demo", "tutorial", "feedback", "open-source", "presentation", "proposal"])

def filter_candidates(proposal_title, candidates, min_sim, extra_stopwords):
    """
    Return those candidates contributions that are similar to the proposal.
    """
    similar_contributions = []
    for candidate in candidates:
        matching_tokens, similar_flag = is_similar(proposal_title, candidate["title"], min_sim=min_sim, extra_stopwords=extra_stopwords)
        if(similar_flag):
            candidate["matching_token"] = matching_tokens
            similar_contributions.append(candidate)
    return similar_contributions


def is_irrelevant(token, extra_stopwords):
    # TODO: Since tokens and string are different things, it may be that this function does not work yet
    irrelevant_flag = token in stop_words or token in punctuation or token in non_informant_words 
    # check if token is in extra_stopwords
    irrelevant_flag |= token in map(str.lower, extra_stopwords)
    return irrelevant_flag

def is_similar(p_title, c_title, min_matches=1, min_sim=0.7, extra_stopwords=[]):
    """
    Checks whether the proposal title has at least min_matches words that
    are similar to the candidate title according to the threshold min_sim.
    The similarity computation is based only on spelling. Using a threshold
    instead of exact string matching leaves room for slight variations in spelling.
    :param p_title: proposal_title
    :param c_title: candidate_title
    :param min_matches: Number of words that have to match between the two titles
    :param min_sim: Number in the range [0,1] representing the threshold above which
                    two words are regarded as similar.
    """
    # Lemmatization and stemming do not sound reasonable for mostly technical terms
    # Thus removing stopwords and punctuation should be sufficient preprocessing
    p_tokens = [t for t in word_tokenize(p_title) if not is_irrelevant(t.lower(), extra_stopwords)]
    c_tokens = [t for t in word_tokenize(c_title) if not is_irrelevant(t.lower(), extra_stopwords)]

    matching_tokens = []
    for pt in p_tokens:
        for ct in c_tokens:
            if SequenceMatcher(None, pt, ct).ratio() >= min_sim:
                matching_tokens.append(pt)
                continue

    #print("Compare:")
    #print(p_tokens)
    #print(c_tokens)
    #print(f"Similar_tokens: {matching_tokens}")
    return matching_tokens, len(matching_tokens) >= 1


