import os.path
import subprocess

from docbox import docbox


def main():
    path = os.path.abspath(".")
    subprocess.run("css-minify -d ./css/ -o ./docs/assets", shell=True)
    docbox.conv(["--input", "yaksha_home", "-o", "docs/index.html", "--title",
                 "Yaksha Programming Language", "--no-number"], root=path)
    docbox.conv(["--all-headers-in-toc", "--input", "yaksha_lib_docs", "-o", "docs/library-docs.html", "--title",
                 "Yaksha Programming Language"], root=path)
    docbox.conv(["--all-headers-in-toc", "--input", "yaksha_docs", "-o", "docs/documentation.html", "--title",
                 "Yaksha Programming Language"], root=path)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
