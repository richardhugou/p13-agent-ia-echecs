"""Point d'entrée du backend — remplacé par l'app FastAPI à l'étape 1 (healthcheck)."""


def ping() -> str:
    """Sonde minimale utilisée par le pipeline CI en attendant l'app FastAPI."""
    return "pong"


if __name__ == "__main__":
    print(ping())
