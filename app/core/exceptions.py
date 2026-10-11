class RegraDeNegocioErro(Exception):
    def __init__(
        self,
        codigo: str,
        mensagem: str,
        status_code: int = 400,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.codigo = codigo
        self.mensagem = mensagem
        self.status_code = status_code
        self.headers = headers
        super().__init__(mensagem)


class RecursoNaoEncontradoErro(RegraDeNegocioErro):
    def __init__(self, recurso: str) -> None:
        super().__init__(
            codigo="RECURSO_NAO_ENCONTRADO",
            mensagem=f"Recurso não encontrado: {recurso}.",
            status_code=404,
        )


class ConflitoErro(RegraDeNegocioErro):
    def __init__(self, codigo: str, mensagem: str) -> None:
        super().__init__(codigo=codigo, mensagem=mensagem, status_code=409)


class NaoAutorizadoErro(RegraDeNegocioErro):
    def __init__(self, mensagem: str) -> None:
        super().__init__(
            codigo="NAO_AUTORIZADO",
            mensagem=mensagem,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )
