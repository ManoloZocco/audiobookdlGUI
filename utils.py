# utils.py

# ...existing code...
def transform_storytel_url(url: str) -> str:
    """
    Trasforma url Storytel eliminando eventuali query string
    e convertendo quelli con '/podcasts/' in formato '/books/'.
    """
    url = url.split('?')[0]  # rimuove query string
    if "/podcasts/" in url:
        last_segment = url.rstrip('/').split('/')[-1]
        url = f"https://www.storytel.com/it/books/{last_segment}"
    return url
# ...existing code...
```

```python
# gui.py

# ...existing code...
from utils import transform_storytel_url

# ...existing code...

# Rimuovi la funzione locale e utilizza quella comune da utils.py
# ...existing code...
# url = url.split('?')[0]  # rimuove query string
# if "/podcasts/" in url:
#     last_segment = url.rstrip('/').split('/')[-1]
#     url = f"https://www.storytel.com/it/books/{last_segment}"
# ...existing code...
url = transform_storytel_url(url)
# ...existing code...
