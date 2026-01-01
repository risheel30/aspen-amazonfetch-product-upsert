import re

# Matches the ASIN out of the common amazon product url shapes:
#   /dp/B0XXXXXXXX
#   /gp/product/B0XXXXXXXX
#   /gp/aw/d/B0XXXXXXXX
#   /product/B0XXXXXXXX
# An ASIN is 10 chars, upper alnum. We normalise to upper case so the
# same product reached through different url forms maps to one asin.
_ASIN_RE = re.compile(
    r"/(?:dp|gp/product|gp/aw/d|product)/([A-Za-z0-9]{10})(?:[/?]|$)"
)


def extract_asin(url):
    """Pull the ASIN out of an amazon product url.

    Returns the upper-cased 10 char asin, or None when the url is not a
    product url we recognise. Query strings and trailing path segments
    like /ref=sr_1_1 do not change the result.
    """
    if not url:
        return None
    match = _ASIN_RE.search(url)
    if not match:
        return None
    return match.group(1).upper()
