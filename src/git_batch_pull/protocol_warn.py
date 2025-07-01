import logging

from git_batch_pull.protocol_utils import detect_protocol_mismatch


def warn_on_protocol_mismatch(repo_path, intended_protocol=None):
    """
    Print a warning if the protocol of the remote URL does not match the intended protocol.

    Args:
        repo_path: Path to the local git repository.
        intended_protocol: 'ssh', 'https', or None.
    """
    warning = detect_protocol_mismatch(repo_path, intended_protocol)
    if warning:
        logging.warning(f"{warning}")
