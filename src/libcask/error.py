class ContainerError(Exception):
    pass


class AlreadyRunning(ContainerError):
    pass


class NotRunning(ContainerError):
    pass


class AlreadyExists(ContainerError):
    pass


class AttributeInvalid(ContainerError):
    pass


class NoSuchContainer(ContainerError):
    pass


class NoSuchImage(ContainerError):
    pass


class InvalidImage(ContainerError):
    pass
