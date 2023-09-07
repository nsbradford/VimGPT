import logging

from _typeshed import Incomplete
from pynvim.api import Nvim as Nvim
from pynvim.api import NvimError as NvimError
from pynvim.msgpack_rpc import (
    ErrorResponse as ErrorResponse,
)
from pynvim.msgpack_rpc import (
    child_session as child_session,
)
from pynvim.msgpack_rpc import (
    socket_session as socket_session,
)
from pynvim.msgpack_rpc import (
    stdio_session as stdio_session,
)
from pynvim.msgpack_rpc import (
    tcp_session as tcp_session,
)
from pynvim.plugin import (
    Host as Host,
)
from pynvim.plugin import (
    autocmd as autocmd,
)
from pynvim.plugin import (
    command as command,
)
from pynvim.plugin import (
    decode as decode,
)
from pynvim.plugin import (
    encoding as encoding,
)
from pynvim.plugin import (
    function as function,
)
from pynvim.plugin import (
    plugin as plugin,
)
from pynvim.plugin import (
    rpc_export as rpc_export,
)
from pynvim.plugin import (
    shutdown_hook as shutdown_hook,
)
from pynvim.util import VERSION as VERSION
from pynvim.util import Version as Version

def start_host(session: Incomplete | None = ...) -> None: ...
def attach(
    session_type,
    address: Incomplete | None = ...,
    port: Incomplete | None = ...,
    path: Incomplete | None = ...,
    argv: Incomplete | None = ...,
    decode: Incomplete | None = ...,
): ...
def setup_logging(name) -> None: ...

class NullHandler(logging.Handler):
    def emit(self, record) -> None: ...
