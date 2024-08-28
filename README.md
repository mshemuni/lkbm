# Pardus

Pradus is a python package used for orchestrate a low level system fleet.

It has almost no dependency on client side. The only needed thing is an `ssh` server and a sudo user to connect to the
client.

## Models:

### Connections:
Connection is an object that allows one to create ssh connections and run commands on a remote client.

```mermaid
classDiagram
    class ModelConnector {
        *run(command: str) -> None
        *sudo_run(command: str) -> None
    }
    class SSHConnector {
        run(command: str) -> None
        sudo_run(command: str) -> None
    }

    ModelConnector <|-- SSHConnector
```


### Services:
Services is an object that allows one to alter services on remote client.

```mermaid
classDiagram
    class ModelService {
        list() -> None
        start(service: str) -> None
        stop(service: str) -> None
        restart(service: str) -> None
        enable(service: str) -> None
        disable(service: str) -> None
        logs(service: str) -> List[Dict[str, Union[str, datetime]]]
    }
    
    class Service {
        __init__(connector: ModelConnector,  sudo_passwd: Optional[str] = None, logger: Optional[Logger] = None) -> None
        list() -> None
        start(service: str) -> None
        stop(service: str) -> None
        restart(service: str) -> None
        enable(service: str) -> None
        disable(service: str) -> None
        logs(service: str) -> List[Dict[str, Union[str, datetime]]]
    }

    class ModelServiceList {
        from_connections(connections: List[ModelConnector], logger: Optional[Logger] = None) -> Self:
        list() -> None
        start(service: str) -> None
        stop(service: str) -> None
        restart(service: str) -> None
        enable(service: str) -> None
        disable(service: str) -> None
        logs(service: str) -> List[Dict[str, Union[str, datetime]]]
    }

    class ServiceList {
        __init__(services: List[Service], logger: Optional[Logger] = None) -> None
        from_connections(connections: List[ModelConnector], logger: Optional[Logger] = None) -> Self:
        list() -> None
        start(service: str) -> None
        stop(service: str) -> None
        restart(service: str) -> None
        enable(service: str) -> None
        disable(service: str) -> None
        logs(service: str) -> List[Dict[str, Union[str, datetime]]]
    }

    ModelService <|-- Service
    ModelServiceList <|-- ServiceList
```



### Config:
Config is an object that allows one to alter configuration files on remote client.

```mermaid
classDiagram
    class ModelConfig {
        __setitem__(self, key: str, value: Dict[str, str]) -> None
        __delitem__(self, key: str) -> None
        update(self, *args, **kwargs) -> None
    }
    
    class Config {
        __init__(self, connector: ModelConnector, path: Union[str, Path], create: bool = False, backup: bool = False, force: bool = False, sudo_passwd: Optional[str] = None, logger: Optional[Logger] = None) -> None
        __setitem__(self, key: str, value: Dict[str, str]) -> None
        def __delitem__(self, key: str) -> None
        clear(self) -> None
        update(self, *args, **kwargs) -> None
        touch(self) -> None
        exist(self, the_file: Optional[Union[str, Path]] = None) -> bool
        create_backup(self) -> None
        read(self) -> str
        __update(self) -> None
    }

    class ModelConfigList {
        __setitem__(self, key: str, value: Dict[str, str]) -> None
        __delitem__(self, key: str) -> None
        update(self, *args, **kwargs) -> None
    }

    class ConfigList {
        __init__(self, configs: List[Config], logger: Optional[Logger] = None)
        __setitem__(self, key: str, value: Dict["str", "str"]) -> None
        __delitem__(self, key) -> None
        from_connections(cls, connections: List[ModelConnector], files: Union[Union[str, Path], List[Union[str, Path]]], sudo_passwds: Optional[Union[str, List[str]]] = None, logger: Optional[Logger] = None) -> Self
        update(self, *args, **kwargs) -> None
        length(self) -> int
        take_element(self, index: int) -> None
        get_element(self, key: Union[int, slice]) -> Union[Config, Self]
        clear(self) -> None
    }
    
    class ConfigRaw {
        __init__(self, connector: ModelConnector, path: Union[str, Path], create: bool = False, backup: bool = False, force: bool = False, sudo_passwd: Optional[str] = None, logger: Optional[Logger] = None) -> None
        __str__(self) -> str
        __len__(self) -> int
        data(self) -> str
        data(self, data) -> None
        read(self) -> str
        exist(self, the_file: Optional[Union[str, Path]] = None) -> bool
        create_backup(self) -> None
        touch(self) -> None
        __update(self) -> None
    }

    ModelConfig <|-- Config
    ModelConfigList <|-- ConfigList
```





### Apt:
Apt is an object that allows one to install/remove, etc. on remote client.

```mermaid
classDiagram
    class ModelApt {
        repositories(self) -> List[Dict[str, str]]
        add_repository(self, repository: str) -> None
        upgrade(self, package_name: Optional[str] = None) -> None
        list(self, installed: bool = False, upgradeable: bool = False) -> List[Dict[str, str]]
        install(self, package_name: Union[str, List[str]]) -> None
        reinstall(self, package_name: Union[str, List[str]]) -> None
        remove(self, package_name: Union[str, List[str]]) -> None
        purge(self, package_name: Union[str, List[str]]) -> None
        search(self, package_name: str) -> List[Dict[str, str]]
        show(self, package_name: str) -> Dict[Union[str, None], Any]
    }
    
    class Apt {
        __init__(self, connector: ModelConnector, sudo_passwd: Optional[str] = None, logger: Optional[Logger] = None) -> None
        repositories(self) -> List[Dict[str, Any]]
        add_repository(self, repository: str) -> None
        update(self) -> None
        list(self, installed: bool = False, upgradeable: bool = False) -> List[Dict[str, str]]
        install(self, package_name: Union[str, List[str]]) -> None
        reinstall(self, package_name: Union[str, List[str]]) -> None
        remove(self, package_name: Union[str, List[str]]) -> None
        purge(self, package_name: Union[str, List[str]]) -> None
        search(self, package_name: str) -> List[Dict[str, str]]
        show(self, package_name: str) -> Dict[Union[str, None], Any]
    }
    class ModelAptList {
        __iter__(self) -> Iterator[Apt]
        __getitem__(self, key: Union[int, slice]) -> Union[Apt, Self]
        __delitem__(self, key) -> None
        __len__(self) -> int
        from_connections(cls, connections: List[ModelConnector], logger: Optional[Logger] = None) -> Self
        repositories(self) -> Dict[Apt, List[Dict[str, str]]]
        add_repository(self, repository: str) -> None
        update(self) -> None
        upgrade(self, package_name: Optional[str] = None) -> None
        list(self, installed: bool = False, upgradeable: bool = False) -> Dict[Apt, List[Dict[str, str]]]
        install(self, package_name: Union[str, List[str]]) -> None
        reinstall(self, package_name: Union[str, List[str]]) -> None
        remove(self, package_name: Union[str, List[str]]) -> None
        search(self, package_name: str) -> Dict[Apt, List[Dict[str, str]]]
        show(self, package_name: str) -> Dict[Apt, Dict[Union[str, None], Any]]
    }
    
    class AptList {
        __init__(self, apts: List[Apt], logger: Optional[Logger] = None) -> None
        from_connections(cls, connections: List[ModelConnector], logger: Optional[Logger] = None) -> Self
        repositories(self) -> Dict[Apt, List[Dict[str, str]]]
        add_repository(self, repository: str) -> None
        update(self) -> None
        upgrade(self, package_name: Optional[str] = None) -> None
        list(self, installed: bool = False, upgradeable: bool = False) -> Dict[Apt, List[Dict[str, str]]]
        install(self, package_name: Union[str, List[str]]) -> None
        reinstall(self, package_name: Union[str, List[str]]) -> None
        remove(self, package_name: Union[str, List[str]]) -> None
        purge(self, package_name: Union[str, List[str]]) -> None
        search(self, package_name: str) -> Dict[Apt, List[Dict[str, str]]]
        show(self, package_name: str) -> Dict[Apt, Dict[Union[str, None], Any]]
    }

    ModelApt <|-- Apt
    ModelAptList <|-- AptList
```

## Example:

### Connection:

Creating an ssh connection.

```python
from pardus import SSHConnector
from logging import getLogger

ssh_connection = SSHConnector("address", 22, "username", "password")

```

### Services:

Service object creation.

```python
from pardus import SSHConnector, Service
from logging import getLogger

ssh_connection = SSHConnector("address", 22, "username", "password")
services = Service(ssh_connection)

```

### Config:

Config object creation.

```python
from pardus import SSHConnector, Config
from logging import getLogger

ssh_connection = SSHConnector("address", 22, "username", "password")
config = Config(ssh_connection, "/etc/samba/smb.conf")

```

### Apt:

Apt object creation.

```python
from pardus import SSHConnector, Apt

ssh_connection = SSHConnector("address", 22, "username", "password")
apt = Apt(ssh_connection)

```
