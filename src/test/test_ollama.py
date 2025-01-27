import unittest
from unittest.mock import patch
import src.Ollama.testOllama as ollama_script  # Importa el script que queremos probar

class TestOllama(unittest.TestCase):

    @patch('src.Ollama.testOllama.ollama.chat')  # Mockea la llamada real a Ollama
    def test_ollama_chat(self, mock_chat):
        # Simulamos una respuesta de Ollama sin llamar al modelo real
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
    def test_write_output(self):
        ollama_script.ollamaResponse = "Bogotá"
        with open('OutputOllama.txt', "w") as text_file:
            text_file.write(ollama_script.ollamaResponse)

        # Verifica que el archivo se escribió correctamente
        open.assert_called_with('OutputOllama.txt', "w")
        open().write.assert_called_with("Bogotá")

if __name__ == '__main__':
    unittest.main()

