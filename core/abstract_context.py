import abc

class AbstractContext(abc.ABC):
    @property
    @abc.abstractmethod
    def interfaces(self) -> dict:
        pass

    @property
    @abc.abstractmethod
    def databases(self) -> dict:
        pass

    @property
    @abc.abstractmethod
    def payment_methods(self) -> dict:
        pass

    @property
    @abc.abstractmethod
    def credentials(self) -> dict:
        pass
