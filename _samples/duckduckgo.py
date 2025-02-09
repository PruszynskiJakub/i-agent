from duckduckgo_search import DDGS
results = DDGS().text('site:wikipedia.org newton', region='wt-wt', safesearch='off', timelimit='y', max_results=10)
print(results)