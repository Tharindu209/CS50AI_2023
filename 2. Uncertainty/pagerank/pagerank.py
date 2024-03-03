import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    prop_dist = {}

    dict_len = len(corpus.keys())
    pages_len = len(corpus[page])

    if len(corpus[page]) < 1:
        for key in corpus.keys():
            prop_dist[key] = 1 / dict_len

    else:
        random_factor = (1 - damping_factor) / dict_len
        even_factor = damping_factor / pages_len

        for key in corpus.keys():
            if key not in corpus[page]:
                prop_dist[key] = random_factor
            else:
                prop_dist[key] = even_factor + random_factor

    return prop_dist


def sample_pagerank(corpus, damping_factor, n):
    samples_dict = corpus.copy()
    for i in samples_dict:
        samples_dict[i] = 0
    sample = None

    for _ in range(n):
        if sample:
            dist = transition_model(corpus, sample, damping_factor)
            dist_lst = list(dist.keys())
            dist_weights = [dist[i] for i in dist]
            sample = random.choices(dist_lst, dist_weights, k=1)[0]
        else:
            sample = random.choice(list(corpus.keys()))

        samples_dict[sample] += 1

    for item in samples_dict:
        samples_dict[item] /= n

    return samples_dict


def iterate_pagerank(corpus, damping_factor):
    pages_number = len(corpus)
    old_dict = {}
    new_dict = {}

    for page in corpus:
        old_dict[page] = 1 / pages_number

    while True:
        for page in corpus:
            temp = 0
            for linking_page in corpus:
                if page in corpus[linking_page]:
                    temp += old_dict[linking_page] / len(corpus[linking_page])
                if len(corpus[linking_page]) == 0:
                    temp += (old_dict[linking_page]) / len(corpus)
            temp *= damping_factor
            temp += (1 - damping_factor) / pages_number

            new_dict[page] = temp

        difference = max([abs(new_dict[x] - old_dict[x]) for x in old_dict])
        if difference < 0.001:
            break
        else:
            old_dict = new_dict.copy()

    return old_dict


if __name__ == "__main__":
    main()
