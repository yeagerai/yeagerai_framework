import abc
import inspect
import importlib.util
import os
import typing
from typing_extensions import final
from yeagerai.core.abstract_context import AbstractContext


class AbstractComponent(abc.ABC):
    to_implement_methods: typing.List[str] = ["__init__", "execute"]

    @abc.abstractmethod
    async def execute(self, args: typing.Any, context: AbstractContext) -> typing.Any:
        """Execute functionality of the Component. This is where the actual component behaviour goes."""
        raise NotImplementedError("Please Implement this method")

    @classmethod
    @final
    def module_path(cls) -> str:
        module_name = cls.__module__
        if module_name:
            module_spec = importlib.util.find_spec(module_name)
            if module_spec is not None:
                module_file = module_spec.origin
                if module_file:
                    module_path = os.path.abspath(os.path.dirname(module_file))
                    return module_path
                else:
                    raise FileNotFoundError(f"Module without file for class {cls}")
            else:
                raise ImportError(f"Module not found: {module_name}")
        else:
            raise FileNotFoundError(f"Module not found for class {cls}")

    @classmethod
    @final
    def component_requirements_path(cls) -> str:
        return os.path.join(cls.module_path(), "requirements.txt")

    @classmethod
    @final
    def check_component_requirements(cls) -> None:
        if not os.path.isfile(cls.component_requirements_path()):
            raise FileNotFoundError(
                "requirements.txt not found on ",
                cls.component_requirements_path(),
            )

    @classmethod
    @final
    def component_dockerfile_path(cls) -> str:
        return os.path.join(cls.module_path(), "Dockerfile")

    @classmethod
    @final
    def check_component_dockerfile(cls) -> None:
        if not os.path.isfile(cls.component_dockerfile_path()):
            raise FileNotFoundError(
                "Dockerfile not found on ",
                cls.component_dockerfile_path(),
            )

    @classmethod
    @final
    def component_configuration_path(cls) -> str:
        return os.path.join(cls.module_path(), "configuration.yml")

    @classmethod
    @final
    def check_component_configuration(cls) -> None:
        if not os.path.isfile(cls.component_configuration_path()):
            raise FileNotFoundError(
                "configuration.yml not found on ",
                cls.component_configuration_path(),
            )

    @classmethod
    @final
    def component_card_path(cls) -> str:
        return os.path.join(cls.module_path(), "component_card.md")

    @classmethod
    @final
    def check_component_card(cls) -> None:
        if not os.path.isfile(cls.component_card_path()):
            raise FileNotFoundError(
                "component_card.md not found on ",
                cls.component_card_path(),
            )

    @classmethod
    @final
    def component_unit_tests_path(cls) -> str:
        return os.path.join(cls.module_path(), "t_component.py")

    @classmethod
    @final
    def check_has_unit_tests(cls) -> None:
        if not os.path.isfile(cls.component_unit_tests_path()):
            raise FileNotFoundError(
                "t_component.py not found on ",
                cls.component_unit_tests_path(),
            )

    @classmethod
    def check_init_is_typed(cls) -> None:
        signature = inspect.signature(cls)

        for arg in signature.parameters.values():
            if arg.name == "self":
                continue
            if arg.annotation is arg.empty:
                raise TypeError(f"Error {arg.name} has no annotation")
        return

    @classmethod
    def check_is_module(cls) -> None:
        cls_path = os.path.abspath(
            os.path.join(os.path.abspath(inspect.getfile(cls)), os.pardir)
        )
        if not os.path.isfile(os.path.join(cls_path, "__init__.py")):
            raise FileNotFoundError(
                f"Couldn't found {os.path.join(cls_path, '__init__.py')}, \
    module structure is required"
            )

    @classmethod
    def test_cls(cls) -> None:
        if "__init__" in cls.to_implement_methods:
            cls.check_init_is_typed()
        cls.check_component_card()
        cls.check_component_configuration()
        cls.check_component_dockerfile()
        cls.check_component_requirements()
        cls.check_is_module()
        cls.check_has_unit_tests()
