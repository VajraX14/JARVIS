import unittest

import jarvis


class ParseCommandTests(unittest.TestCase):
    def test_open_google(self):
        self.assertEqual(
            jarvis.parse_command("Jarvis, open Google!"),
            ("open_url", "https://www.google.com"),
        )

    def test_open_youtube(self):
        self.assertEqual(
            jarvis.parse_command("open youtube"),
            ("open_url", "https://www.youtube.com"),
        )

    def test_wikipedia_topic(self):
        self.assertEqual(
            jarvis.parse_command("Wikipedia for Ada Lovelace"),
            ("wikipedia", "Ada Lovelace"),
        )

    def test_wiki_alias(self):
        self.assertEqual(jarvis.parse_command("wiki Saturn"), ("wikipedia", "Saturn"))

    def test_web_search(self):
        self.assertEqual(
            jarvis.parse_command("search for orbital mechanics"),
            ("web_search", "orbital mechanics"),
        )

    def test_time_with_apostrophe(self):
        self.assertEqual(jarvis.parse_command("what's the time"), ("time", ""))

    def test_exit_command_is_exact(self):
        self.assertEqual(jarvis.parse_command("goodbye"), ("exit", ""))
        self.assertNotEqual(jarvis.parse_command("goodbye everyone")[0], "exit")
        self.assertNotEqual(jarvis.parse_command("I will say bye later")[0], "exit")

    def test_empty_command(self):
        self.assertEqual(jarvis.parse_command("   "), ("empty", ""))

    def test_unknown_command_does_not_exit(self):
        self.assertEqual(jarvis.parse_command("play some jazz")[0], "unknown")


class ExecuteCommandTests(unittest.TestCase):
    def test_exit_speaks_and_stops(self):
        messages = []
        keep_running = jarvis.execute_command("bye", speaker=messages.append)
        self.assertFalse(keep_running)
        self.assertEqual(messages, ["Goodbye."])

    def test_unknown_command_keeps_running(self):
        messages = []
        keep_running = jarvis.execute_command(
            "play some jazz", speaker=messages.append
        )
        self.assertTrue(keep_running)
        self.assertIn("help", messages[0].lower())

    def test_open_google_uses_browser_callback(self):
        messages = []
        opened = []
        keep_running = jarvis.execute_command(
            "open google",
            speaker=messages.append,
            open_url=opened.append,
        )
        self.assertTrue(keep_running)
        self.assertEqual(opened, ["https://www.google.com"])


if __name__ == "__main__":
    unittest.main()
