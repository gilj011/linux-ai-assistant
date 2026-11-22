"""
Testes unitarios para o ActionParser.
"""

import unittest
from src.action_parser import ActionParser, ProposedAction


class TestActionParser(unittest.TestCase):

    def test_extract_write_file_action(self):
        sample = """
Aqui estao as instrucoes.
```kored-action
{
  "action": "write_file",
  "path": "~/instrucoes.txt",
  "content": "Linha 1\\nLinha 2",
  "explanation": "Arquivo de correcao"
}
```
Voce pode aprovar.
"""
        actions = ActionParser.extract_actions(sample)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action.action_type, "write_file")
        self.assertEqual(action.path, "~/instrucoes.txt")
        self.assertIn("Linha 1", action.content)

        clean = ActionParser.strip_action_blocks(sample)
        self.assertNotIn("kored-action", clean)
        self.assertIn("Aqui estao as instrucoes.", clean)

    def test_extract_run_command_action(self):
        sample = """
Sugiro rodar o comando:
```kored-action
{
  "action": "run_command",
  "command": "systemctl restart nginx",
  "explanation": "Reinicia o servidor web"
}
```
"""
        actions = ActionParser.extract_actions(sample)
        self.assertEqual(len(actions), 1)
        action = actions[0]
        self.assertEqual(action.action_type, "run_command")
        self.assertEqual(action.command, "systemctl restart nginx")
        self.assertEqual(action.explanation, "Reinicia o servidor web")

    def test_no_actions(self):
        sample = "Apenas uma conversa sem blocos de acao."
        actions = ActionParser.extract_actions(sample)
        self.assertEqual(len(actions), 0)


if __name__ == "__main__":
    unittest.main()
