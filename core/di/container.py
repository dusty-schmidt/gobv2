"""
Lightweight dependency injection container for the gob ecosystem
"""

from typing import Dict, Type, Any, TypeVar, Generic, Callable, Optional
import inspect

T = TypeVar('T')


class Container:
    """Simple dependency injection container"""

    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}

    def register(self, interface: Type[T], implementation: Type[T] = None,
                 factory: Callable[[], T] = None, singleton: bool = True) -> None:
        """
        Register a service with the container

        Args:
            interface: The interface/abstract class
            implementation: The concrete implementation class
            factory: A factory function that returns the service
            singleton: Whether to cache the instance
        """
        if factory:
            self._factories[interface] = factory
        elif implementation:
            if singleton:
                self._singletons[interface] = None  # Will be created on first access
                self._services[interface] = implementation
            else:
                self._services[interface] = implementation
        else:
            raise ValueError("Must provide either implementation or factory")

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a pre-created instance"""
        self._singletons[interface] = instance

    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service from the container"""
        # Check for singleton instances first
        if interface in self._singletons and self._singletons[interface] is not None:
            return self._singletons[interface]

        # Check for factories
        if interface in self._factories:
            instance = self._factories[interface]()
            if interface in self._singletons:
                self._singletons[interface] = instance
            return instance

        # Check for registered services
        if interface in self._services:
            implementation = self._services[interface]
            if inspect.isclass(implementation):
                # Auto-inject dependencies for the constructor
                instance = self._create_instance(implementation)
                if interface in self._singletons:
                    self._singletons[interface] = instance
                return instance
            else:
                return implementation

        raise ValueError(f"No registration found for {interface}")

    def _create_instance(self, cls: Type[T]) -> T:
        """Create an instance of a class with dependency injection"""
        # Get the constructor signature
        init_signature = inspect.signature(cls.__init__)
        parameters = init_signature.parameters

        # Skip 'self' parameter
        kwargs = {}
        for param_name, param in parameters.items():
            if param_name == 'self':
                continue

            # Try to resolve the parameter type
            if param.annotation != inspect.Parameter.empty:
                try:
                    kwargs[param_name] = self.resolve(param.annotation)
                except ValueError:
                    # If we can't resolve, check if it has a default
                    if param.default == inspect.Parameter.empty:
                        raise ValueError(f"Cannot resolve dependency {param.annotation} for {cls}")
                    # Use default value
                    pass
            elif param.default == inspect.Parameter.empty:
                raise ValueError(f"Parameter {param_name} has no type annotation and no default")

        return cls(**kwargs)

    def has_registration(self, interface: Type) -> bool:
        """Check if an interface is registered"""
        return (interface in self._services or
                interface in self._factories or
                interface in self._singletons)


# Global container instance
_container = None


def get_container() -> Container:
    """Get the global container instance"""
    global _container
    if _container is None:
        _container = Container()
        _initialize_container(_container)
    return _container


def _initialize_container(container: Container) -> None:
    """Initialize the container with default services"""
    from ..config.models import GlobalConfig
    from ..brain.storage import StorageAbstraction
    from ..brain.brain import CommunalBrain, BrainConfig

    # Register configuration
    config = GlobalConfig()
    container.register_instance(GlobalConfig, config)

    # Register storage
    def create_storage():
        return StorageAbstraction(config.storage)

    container.register(StorageAbstraction, factory=create_storage)

    # Register communal brain
    def create_brain():
        brain_config = BrainConfig(storage=config.storage)
        return CommunalBrain(brain_config)

    container.register(CommunalBrain, factory=create_brain)