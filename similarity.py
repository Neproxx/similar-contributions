import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from difflib import SequenceMatcher

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
punctuation = set([',', '.', ':', ';', '?', '!', '&'])

def filter_candidates(proposal_title, candidates):
    """
    Return those candidates contributions that are similar to the proposal.
    """
    similar_contributions = []
    for candidate in candidates:
        if is_similar(proposal_title, candidate["title"]):
            similar_contributions.append(candidate)
    return similar_contributions


def is_irrelevant(token):
    return token in stop_words or token in punctuation


def is_similar(p_title, c_title, min_matches=1, min_sim=0.7):
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
    p_tokens = [t for t in word_tokenize(p_title) if not is_irrelevant(t)]
    c_tokens = [t for t in word_tokenize(c_title) if not is_irrelevant(t)]

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
    return len(matching_tokens) >= 1


