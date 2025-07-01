import importlib.metadata
import logging


class PluginBase:
    """
    Base class for plugins. All plugins must inherit from this and implement run().
    """

    def run(self, *args, **kwargs):
        """Run the plugin with the given arguments."""
        raise NotImplementedError


def discover_plugins():
    """
    Discover plugins via entry points.
    Gracefully handle missing/broken plugins.

    Returns:
        dict: Mapping of plugin name to plugin class.
    """
    plugins = {}
    try:
        entry_points = importlib.metadata.entry_points().get("git_batch_pull_plugins", [])
        for entry_point in entry_points:
            try:
                plugin = entry_point.load()
                plugins[entry_point.name] = plugin
                logging.info(f"Loaded plugin: {entry_point.name} from {entry_point.module}")
            except Exception as e:
                logging.warning(
                    f"Failed to load plugin {entry_point.name} from " f"{entry_point.module}: {e}"
                )
    except Exception as e:
        logging.warning(f"Failed to discover plugins: {e}")
    return plugins
