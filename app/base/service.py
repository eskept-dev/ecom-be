from abc import ABC, abstractmethod


class BaseService(ABC):

    @abstractmethod
    def perform(self, *args, **kwargs):
        pass
