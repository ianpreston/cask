class ContainerError(Exception):
    pass


class AlreadyRunning(ContainerError):
    pass


class NotRunning(ContainerError):
    pass
