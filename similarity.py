import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from difflib import SequenceMatcher

nltk.download('stopwords')
nltk.download('punkt')
stop_words = set(stopwords.words('english'))
punctuation = set([',', '.', ':', ';', '?', '!', '&'])
non_informant_words = set(["course", "automation", "essay", "demo", "tutorial", "feedback", "open-source", "presentation", "proposal"])

def filter_candidates(proposal_title, candidates, min_sim, words_ignore):
    """
    Return those candidates contributions that are similar to the proposal.
    """
    stemmer = SnowballStemmer("english")
    similar_contributions = []
    for candidate in candidates:
        matching_tokens, similar_flag = is_similar(proposal_title, candidate["title"],
                                                  stemmer, min_sim, words_ignore)
        if(similar_flag):
            candidate["matching_token"] = matching_tokens
            similar_contributions.append(candidate)
    return similar_contributions


def is_irrelevant(token, words_ignore, stemmer):
    irrelevant_flag = token in stop_words or token in punctuation or token in non_informant_words 
    irrelevant_flag |= stemmer.stem(token) in [stemmer.stem(s.lower()) for s in words_ignore]
    return irrelevant_flag

def is_similar(p_title, c_title, stemmer, min_sim=0.7, words_ignore=[], min_matches=1):
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
    p_tokens = [t for t in word_tokenize(p_title) if not is_irrelevant(t.lower(), words_ignore, stemmer)]
    c_tokens = [t for t in word_tokenize(c_title) if not is_irrelevant(t.lower(), words_ignore, stemmer)]

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


