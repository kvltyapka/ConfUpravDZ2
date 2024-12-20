import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
from main import generate_graphviz_code, visualize_graphviz, main
from git import Repo
from datetime import datetime, timedelta

class TestGraphFunctions(unittest.TestCase):

    def setUp(self):
        # Создаем временную директорию для репозитория
        self.temp_dir = tempfile.mkdtemp()
        self.temp_repo_path = os.path.join(self.temp_dir, 'temp_repo')
        os.makedirs(self.temp_repo_path, exist_ok=True)
        self.repo = Repo.init(self.temp_repo_path)

        # Создаем коммиты для тестирования
        with open(os.path.join(self.temp_repo_path, 'testfile.txt'), 'w') as f:
            f.write('Test content')
        self.repo.index.add(['testfile.txt'])
        self.repo.index.commit('Initial commit')

    def tearDown(self):
        # Удаляем временную директорию
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_temp_repo(self):
        # Проверяем, что временный репозиторий создается и удаляется корректно
        self.assertTrue(os.path.exists(self.temp_repo_path))
        self.assertTrue(os.path.isdir(self.temp_repo_path))

    @patch('builtins.open', new_callable=mock_open)
    @patch('main.Repo.iter_commits')
    def test_generate_graphviz_code(self, mock_iter_commits, mock_file):
        # Путь к файлу-результату в виде кода
        output_file_path = os.path.join(self.temp_dir, "graph.dot")

        # Дата коммитов в репозитории (например, за последние 30 дней)
        date_threshold = datetime.now() - timedelta(days=30)

        # Создаем мок-объект для коммитов
        mock_commit = MagicMock()
        mock_commit.committed_date = datetime.now().timestamp()
        mock_commit.hexsha = 'abc123'
        mock_commit.stats.files = {'file1.txt': {}, 'file2.txt': {}}
        mock_iter_commits.return_value = [mock_commit]

        # Генерация Graphviz кода
        generate_graphviz_code(self.temp_repo_path, output_file_path, date_threshold)

        mock_file.assert_called()
        written_content = ''.join(call[0][0] for call in mock_file().write.call_args_list)
        self.assertIn('digraph', written_content)

    @patch('subprocess.run')
    def test_visualize_graphviz(self, mock_subprocess_run):
        # Путь к файлу-результату в виде кода
        output_file_path = os.path.join(self.temp_dir, "graph.dot")

        # Визуализация графа
        visualize_graphviz(output_file_path)

        mock_subprocess_run.assert_called_once_with(
            ['dot', '-Tpng', output_file_path, '-o', output_file_path.replace(".dot", ".png")],
            capture_output=True,
            text=True
        )

if __name__ == '__main__':
    unittest.main()