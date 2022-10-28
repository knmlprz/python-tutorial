import os
import subprocess
from pathlib import Path

PROJECT_DIR = Path(
    r"C:\Users\vital\OneDrive\python\PRZ\knml-python-tutorial-private\2-tex-report-generator"
)
OUTPUT_DIR = PROJECT_DIR.joinpath("results")

RESOURCES_DIR = PROJECT_DIR.joinpath("resources")
SPR_DIRS = (
    RESOURCES_DIR.joinpath("sprawozdanie-1"),
    RESOURCES_DIR.joinpath("sprawozdanie-2"),
    RESOURCES_DIR.joinpath("sprawozdanie-3"),
)

with open(RESOURCES_DIR.joinpath("tex-templates/header.tex"),
          mode="r",
          encoding="UTF-8") as header_file:
    header = header_file.read()

footer = r"\end{document}"


def add_figure(path, caption):
    figure = r"""
    \begin{figure}
        \centering
        \includegraphics[width=0.8\textwidth]{%(path)s}
        \caption{%(figure_caption)s}
    \end{figure}
    """ % {
        "path": path.as_posix(),
        "figure_caption": caption,
    }
    return figure


def create_tex_code(directory, captions, latex_head, latex_tail):
    content = latex_head
    for filename, caption in zip(os.listdir(directory), captions):
        content += add_figure(directory.joinpath(filename), caption)
    content += latex_tail
    return content


def generate_report(output_directory, filename, content):
    filepath = os.path.join(output_directory, os.path.splitext(filename)[0])
    tex_file_path = filepath + ".tex"
    with open(tex_file_path, "w", encoding="UTF-8") as f:
        f.write(content)

    command = [
        "pdflatex",
        "-interaction",
        "nonstopmode",
        "-output-directory",
        output_directory,
        tex_file_path,
    ]
    proc = subprocess.Popen(command)
    proc.communicate()

    retcode = proc.returncode
    os.unlink(filepath + ".log")
    if not retcode == 0:
        os.unlink(filepath + ".pdf")
        raise Exception("Error {} executing command: {}".format(
            retcode, " ".join(command)))


captions = [f"Image {i + 1}" for i, _ in enumerate(os.listdir(SPR_DIRS[2]))]

content = create_tex_code(directory=SPR_DIRS[2],
                          captions=captions,
                          latex_head=header,
                          latex_tail=footer)
generate_report(output_directory=OUTPUT_DIR, filename="cover", content=content)
