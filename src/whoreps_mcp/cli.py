"""The `whoreps-mcp` command.

Bare invocation runs the MCP server over stdio (what an MCP host launches).
Subcommands (`lookup`, `districts`, ...) are added as later milestones land and
are handy for trying the data path from a terminal.
"""

from __future__ import annotations

import typer

from whoreps_mcp import __version__

app = typer.Typer(
    name="whoreps-mcp",
    help="Address -> your elected officials, as an MCP server.",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def _default(ctx: typer.Context) -> None:
    # No subcommand -> behave as the MCP server (stdio), so `whoreps-mcp` just works.
    if ctx.invoked_subcommand is None:
        from whoreps_mcp.server import run_stdio

        run_stdio()


@app.command()
def serve() -> None:
    """Run the MCP server over stdio (same as bare `whoreps-mcp`)."""
    from whoreps_mcp.server import run_stdio

    run_stdio()


@app.command()
def version() -> None:
    """Print the whoreps-mcp version."""
    typer.echo(f"whoreps-mcp {__version__}")


if __name__ == "__main__":
    app()
