"""Hermes directory-plugin entry point."""
def register(ctx):
    from .src.hermes_market.plugin import register as register_tools
    return register_tools(ctx)
