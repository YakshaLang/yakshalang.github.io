import os.path
import subprocess

from docbox_generator import docbox


def main():
    path = os.path.abspath(".")
    subprocess.run("css-minify -d ./css/ -o ./docs/assets", shell=True)
    docbox.conv(["--all-headers-in-toc", "--input", "yaksha_lib_docs", "-o", "docs/library-docs.html", "--title",
                 "Yaksha Programming Language"], root=path)
    docbox.conv(["--all-headers-in-toc", "--input", "yaksha_docs", "-o", "docs/documentation.html", "--title",
                 "Yaksha Programming Language"], root=path)
    docbox.conv(["--md", "--input", "yaksha_tutorials", "-o", "docs/tutorials.html", "--title",
                 "Yaksha Programming Language"], root=path)
    docbox.conv(["--md", "--no-number", "--input", "yaksha_proposals", "-o", "docs/yama.html", "--title",
                 "Yaksha Programming Language"], root=path)
    docbox.conv(["--md", "--no-number", "--input", "yaksha_blog", "-o", "docs/blog.html", "--title",
                 "Yaksha Programming Language"], root=path)
    docbox.conv(["--all-headers-in-toc", "--no-number", "--input", "yaksha_demos", "-o", "docs/demos.html", "--title",
                 "Yaksha Programming Language"], root=path)
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
