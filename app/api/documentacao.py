"""Exemplos de erro reutilizados na documentação OpenAPI."""

from typing import Any

ERROS: dict[int, dict[str, Any]] = {
    400: {
        "description": "Regra de negócio inválida",
        "content": {
            "application/json": {
                "example": {
                    "erro": {
                        "codigo": "PERIODO_INVALIDO",
                        "mensagem": "A data inicial não pode ser posterior à data final.",
                    }
                }
            }
        },
    },
    401: {
        "description": "Autenticação ausente ou inválida",
        "content": {
            "application/json": {
                "example": {
                    "erro": {
                        "codigo": "NAO_AUTORIZADO",
                        "mensagem": "Token inválido ou expirado.",
                    }
                }
            }
        },
    },
    404: {
        "description": "Recurso não encontrado",
        "content": {
            "application/json": {
                "example": {
                    "erro": {
                        "codigo": "RECURSO_NAO_ENCONTRADO",
                        "mensagem": "Recurso não encontrado.",
                    }
                }
            }
        },
    },
    409: {
        "description": "Conflito com os dados atuais",
        "content": {
            "application/json": {
                "example": {
                    "erro": {
                        "codigo": "RECURSO_EM_CONFLITO",
                        "mensagem": "A operação não pode ser concluída.",
                    }
                }
            }
        },
    },
    422: {
        "description": "Dados enviados são inválidos",
        "content": {
            "application/json": {
                "example": {
                    "erro": {
                        "codigo": "DADOS_INVALIDOS",
                        "mensagem": "Confira os dados enviados.",
                        "detalhes": [
                            {"campo": "quantidade", "mensagem": "O valor deve ser maior que zero."}
                        ],
                    }
                }
            }
        },
    },
    500: {
        "description": "Erro interno sem exposição de detalhes técnicos",
        "content": {
            "application/json": {
                "example": {
                    "erro": {
                        "codigo": "ERRO_INTERNO",
                        "mensagem": "Ocorreu um erro interno. Tente novamente mais tarde.",
                    }
                }
            }
        },
    },
}


def respostas(*status_codes: int) -> dict[int, dict[str, Any]]:
    return {status_code: ERROS[status_code] for status_code in status_codes}


RESPOSTAS_COMUNS = respostas(422, 500)
