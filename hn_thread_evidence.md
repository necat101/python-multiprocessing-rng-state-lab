# HN Thread Evidence

Thread ID: 26767441  
Title: A common mistake when NumPy's RNG with PyTorch  
Author: sunils34  
URL: https://news.ycombinator.com/item?id=26767441  
Linked article: https://tanelp.github.io/posts/a-bug-that-plagues-thousands-of-open-source-ml-projects/

Evidence captured via:

```
hackernews get-item --id 26767441
```

followed by recursive fetch of all child comments.

Sanitized public fields stored in `hn_comments_sanitized.json` (item id, author, parent id, timestamp, type, title, url, text).

Relevant commenters summarized in README.md:

- _coveredInBees – worker seeding easy to get wrong even in official tutorials; custom worker_init_fn
- nurpax – worker-specific seed exposed by PyTorch
- shoyer – against hidden mutable global RNG state; prefer explicit generator state
- warsheep – explicit generator can still have state copied by fork
- acdha – fork as optimization makes RNG initialization easy to misunderstand / tutorials omit
- OskarS – some programmers treat pseudorandom values as fresh external randomness
- timzaman – Python, NumPy, Torch, distributed workers may each need deliberate seeding
- jeeeb – ordinary unit tests may miss a problem appearing only with worker processes
- _delirium – distinguished fork-based behavior from Windows spawn behavior
- ynik – macOS changed its multiprocessing default; favored explicit cross-platform start-method choices
- rurban – reseeding workers while preserving reproducibility
- anon_tor_12345 – challenged article's clickbait framing and unsupported "over 95%" prevalence claim

The thread does not prove that every NumPy program duplicates random sequences, that every PyTorch DataLoader currently has the historical behavior described by the article, that explicit generator objects cannot be copied, that spawn automatically makes poorly seeded code correct, that different sequences are statistically independent merely because they differ, that repeated augmentations necessarily damage model quality, that one deterministic multiprocessing experiment measures production training behavior, or that the article's repository-wide percentage has been independently reproduced.

Full comment text available in `hn_comments_sanitized.json`.
