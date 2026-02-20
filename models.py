from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import hashlib


class User:
    def __init__(self, username, password):
        self._username = username  # Encapsulated
        self._password_hash = self._hash_password(password)

    def _hash_password(self, password):  # Encapsulation
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        return self._password_hash == self._hash_password(password)

    @property
    def username(self):
        return self._username


class Item(ABC):
    def __init__(self, name, description, category, date, location, user_id, image_path):
        self._name = name
        self._description = description
        self._category = category
        self._date = datetime.strptime(date, "%Y-%m-%d")
        self._location = location
        self._status = "lost" if isinstance(self, LostItem) else "found"
        self._user_id = user_id
        self._image_path = image_path

    @abstractmethod
    def match(self, other_item):
        return self._category.lower() == other._category.lower() and \
            self._location.lower() == other._location.lower()

    @property
    def name(self):
        return self._name

    @property
    def category(self):
        return self._category

    @property
    def location(self):
        return self._location

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value


class LostItem(Item):
    def __init__(self, name, description, category, date, location, user_id, image_path):
        super().__init__(name, description, category, date, location, user_id, image_path)

    def match(self, other):
        return (
            self._category.lower() == other._category.lower() and
            self._location.lower() == other._location.lower()
        )


class FoundItem(Item):
    def __init__(self, name, description, category, date, location, user_id, image_path):
        super().__init__(name, description, category, date, location, user_id, image_path)

    def match(self, other_item):
        if isinstance(other_item, LostItem):
            return other_item.match(self)
        return False

class Claim:
    def __init__(self, item_id, claimant_id, status="claimed", claim_date=None):
        self._item_id = item_id
        self._claimant_id = claimant_id
        self._status = status
        self._claim_date = claim_date

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value