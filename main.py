import os
import subprocess
import argparse
from git import Repo, GitCommandError
from datetime import datetime, timedelta
from graphviz import Digraph
import configparser

def generate_graphviz_code(repo_path, output_file_path, date_threshold):
    print(f"Generating Graphviz code for repository at {repo_path}")
    try:
        repo = Repo(repo_path)
        commits = list(repo.iter_commits())

        dot = Digraph(comment='Git Repository')
        for commit in commits:
            commit_date = datetime.fromtimestamp(commit.committed_date)
            if commit_date > date_threshold:
                files_and_dirs = "\n".join(commit.stats.files.keys())
                dot.node(commit.hexsha, f"{commit.hexsha}\n{files_and_dirs}")
                for parent in commit.parents:
                    dot.edge(parent.hexsha, commit.hexsha)

        dot.save(output_file_path)
        print(f"Graphviz code generated at {output_file_path}")
    except Exception as e:
        print(f"Error generating Graphviz code: {e}")

def visualize_graphviz(output_file_path):
    print(f"Visualizing graph using Graphviz at {output_file_path}")
    try:
        output_image_path = output_file_path.replace(".dot", ".png")
        result = subprocess.run(["dot", "-Tpng", output_file_path, "-o", output_image_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            print(f"Graph visualized and saved as {output_image_path}")
    except Exception as e:
        print(f"Error visualizing graph: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate and visualize commit graph using Graphviz.")
    parser.add_argument("config_file", help="Path to the configuration file.")

    args = parser.parse_args()
    config_file = args.config_file

    config = configparser.ConfigParser()
    config.read(config_file)

    repo_path = config['DEFAULT']['RepoPath']
    output_file_path = config['DEFAULT']['OutputFilePath']
    date_str = config['DEFAULT']['Date']
    date_threshold = datetime.strptime(date_str, "%Y-%m-%d")

    # Проверка существования директории
    if not os.path.exists(repo_path):
        try:
            # Клонирование репозитория
            print(f"Cloning repository from {repo_path}")
            Repo.clone_from(repo_path, repo_path)
        except GitCommandError as e:
            print(f"Error cloning repository: {e}")
            return

    # Проверка, что директория является Git-репозиторием
    if not os.path.exists(os.path.join(repo_path, ".git")):
        print(f"The directory {repo_path} is not a Git repository.")
        return

    # Генерация Graphviz кода
    generate_graphviz_code(repo_path, output_file_path, date_threshold)

    # Визуализация графа
    visualize_graphviz(output_file_path)

if __name__ == "__main__":
    main()