import hashlib

class AdDeduplicator:
    def __init__(self):
        self.seen_hashes = set()

    def _generate_hash(self, ad):
        unique_str = f"{ad.link}-{ad.title}-{ad.address}"
        return hashlib.md5(unique_str.encode()).hexdigest()

    def is_duplicate(self, ad):
        return self._generate_hash(ad) in self.seen_hashes

    def add(self, ad):
        self.seen_hashes.add(self._generate_hash(ad))