"""Configuration file for Nox."""
import tempfile
import nox  # noqa: I003
from nox import Session


def install_with_constraints(session: Session, *args, **kwargs):
    """Installs packages based on poetry lockfile. Acts as a wrapper for session.install()."""
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--with",
            "dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session
def docs(session: Session) -> None:
    """Build the documentation."""
    # session.run("poetry", "install", "--only", "main", external=True)
    install_with_constraints(
        session,
        "mkdocs",
        "mkdocs-material",
        "mkdocs-minify-plugin",
        "pymdown-extensions",
        "mike",
    )
    session.run("make", "docs-dev", external=True)


@nox.session
def docs_production(session: Session) -> None:
    """Build the documentation."""
    # session.run("poetry", "install", "--only", "main", external=True)
    install_with_constraints(
        session,
        "mkdocs",
        "mkdocs-material",
        "mkdocs-minify-plugin",
        "pymdown-extensions",
        "mike",
    )
    session.run("make", "docs-prod", external=True)
