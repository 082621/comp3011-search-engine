import pytest
from unittest.mock import patch, MagicMock
from io import StringIO


# ── Helpers ───────────────────────────────────────────────────────────────────

def run_with_inputs(*inputs):
    """Run main.run() with a sequence of simulated user inputs."""
    from src.main import run
    input_str = "\n".join(inputs) + "\n"
    with patch("builtins.input", side_effect=inputs):
        with patch("sys.stdout", new_callable=StringIO) as mock_out:
            try:
                run()
            except StopIteration:
                pass
            return mock_out.getvalue()


# ── load command ──────────────────────────────────────────────────────────────

class TestLoadCommand:
    def test_load_missing_index_shows_error(self):
        with patch("os.path.exists", return_value=False):
            output = run_with_inputs("load", "quit")
        assert "Error" in output or "error" in output.lower() or "No index" in output

    def test_load_existing_index_succeeds(self, tmp_path):
        import json
        index_data = {"good": {"https://example.com/": {"frequency": 1, "positions": [0]}}}
        index_file = tmp_path / "index.json"
        index_file.write_text(json.dumps(index_data))

        with patch("src.main.INDEX_PATH", str(index_file)):
            output = run_with_inputs("load", "quit")
        assert "loaded" in output.lower()


# ── print command ─────────────────────────────────────────────────────────────

class TestPrintCommand:
    def test_print_without_word_shows_usage(self):
        output = run_with_inputs("print", "quit")
        assert "Usage" in output

    def test_print_word_not_in_index_shows_message(self, tmp_path):
        import json
        index_file = tmp_path / "index.json"
        index_file.write_text(json.dumps({}))
        with patch("src.main.INDEX_PATH", str(index_file)):
            output = run_with_inputs("load", "print zzzzz", "quit")
        assert "not found" in output.lower()

    def test_print_existing_word_shows_entry(self, tmp_path):
        import json
        index_data = {"good": {"https://example.com/": {"frequency": 2, "positions": [0, 3]}}}
        index_file = tmp_path / "index.json"
        index_file.write_text(json.dumps(index_data))
        with patch("src.main.INDEX_PATH", str(index_file)):
            output = run_with_inputs("load", "print good", "quit")
        assert "good" in output
        assert "frequency" in output


# ── find command ──────────────────────────────────────────────────────────────

class TestFindCommand:
    def test_find_without_query_shows_usage(self):
        output = run_with_inputs("find", "quit")
        assert "Usage" in output

    def test_find_word_with_results(self, tmp_path):
        import json
        index_data = {"good": {"https://example.com/": {"frequency": 1, "positions": [0]}}}
        index_file = tmp_path / "index.json"
        index_file.write_text(json.dumps(index_data))
        with patch("src.main.INDEX_PATH", str(index_file)):
            output = run_with_inputs("load", "find good", "quit")
        assert "https://example.com/" in output

    def test_find_word_no_results(self, tmp_path):
        import json
        index_file = tmp_path / "index.json"
        index_file.write_text(json.dumps({}))
        with patch("src.main.INDEX_PATH", str(index_file)):
            output = run_with_inputs("load", "find zzzzz", "quit")
        assert "No pages found" in output

    def test_find_multi_word_query(self, tmp_path):
        import json
        index_data = {
            "good": {"https://example.com/": {"frequency": 1, "positions": [0]}},
            "friends": {"https://example.com/": {"frequency": 1, "positions": [1]}},
        }
        index_file = tmp_path / "index.json"
        index_file.write_text(json.dumps(index_data))
        with patch("src.main.INDEX_PATH", str(index_file)):
            output = run_with_inputs("load", "find good friends", "quit")
        assert "https://example.com/" in output


# ── unknown command ───────────────────────────────────────────────────────────

class TestUnknownCommand:
    def test_unknown_command_shows_error(self):
        output = run_with_inputs("foobar", "quit")
        assert "Unknown command" in output

    def test_empty_input_is_ignored(self):
        output = run_with_inputs("", "quit")
        assert "Goodbye" in output


# ── quit command ──────────────────────────────────────────────────────────────

class TestQuitCommand:
    def test_quit_exits(self):
        output = run_with_inputs("quit")
        assert "Goodbye" in output

    def test_exit_alias_works(self):
        output = run_with_inputs("exit")
        assert "Goodbye" in output

    def test_q_alias_works(self):
        output = run_with_inputs("q")
        assert "Goodbye" in output