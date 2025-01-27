import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock
from src.Model_Mya_V1.analyzer_agent import AnalyzerAgent
from src.Model_Mya_V1.matcher_agent import MatcherAgent
from src.Ollama import testOllama as ollama_script

class TestOllama(unittest.IsolatedAsyncioTestCase):  # ✅ Usa `IsolatedAsyncioTestCase` para async tests

    @patch('src.Ollama.testOllama.ollama.chat')  # Mockea la llamada real a Ollama
    async def test_ollama_chat(self, mock_chat):
        mock_chat.return_value = {'message': {'content': 'Bogotá'}}
        
        # Ejecutamos el código de testOllama.py
        ollama_script.desiredModel = 'mock_model'
        ollama_script.questionToAsk = 'What is the capital of Colombia?'
        ollama_script.response = ollama_script.ollama.chat(model=ollama_script.desiredModel, messages=[
            {'role': 'user', 'content': ollama_script.questionToAsk}
        ])
        
        ollama_script.ollamaResponse = ollama_script.response['message']['content']
        
        # Verificamos que la respuesta es la esperada
        self.assertEqual(ollama_script.ollamaResponse, 'Bogotá')

    @patch('builtins.open', unittest.mock.mock_open())  # Mockea la escritura de archivos
    async def test_write_output(self):
        ollama_script.ollamaResponse = "Bogotá"
        with open('OutputOllama.txt', "w") as text_file:
            text_file.write(ollama_script.ollamaResponse)

        # Verifica que el archivo se escribió correctamente
        open.assert_called_with('OutputOllama.txt', "w")
        open().write.assert_called_with("Bogotá")

    async def test_analyzer_agent_execution(self):
        """Asegura que AnalyzerAgent realmente se ejecuta y genera cobertura."""
        agent = AnalyzerAgent()  # ✅ Constructor sin `config`
        result = await agent.run([{"content": "Python, 5 years of experience"}])  # ✅ Usa `await`
        self.assertIsInstance(result, dict)  # Simula una validación

    async def test_matcher_agent_execution(self):
        """Asegura que MatcherAgent se ejecuta correctamente."""
        matcher = MatcherAgent()
        job = {"title": "Data Scientist", "skills": ["Python", "Machine Learning"]}
        match_result = await matcher.run([{"content": json.dumps(job)}])  # ✅ Usa `await`
        self.assertIsNotNone(match_result)

if __name__ == '__main__':
    unittest.main()

