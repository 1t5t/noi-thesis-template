import os
import re
import shutil
import pdfplumber
from pdfminer.pdfparser import PDFSyntaxError

# Ignore the following directories when compiling
ignore_directory = [".vscode"]

# noithesis.cls path
cls_file_path = "./noithesis.cls"

# subfile_list is the input of main.tex
subfile_list_tex_path = "./subfile_list.tex"
subfile_list = open(subfile_list_tex_path, "w", encoding="utf-8")

# Correct page numbering for subfiles
page_number = 1

# log file
log_file_path = "./log.txt"
log = open(log_file_path, "w", encoding='utf-8')

# Tools

"""Output Function"""
tabnum = 0
def addTab():
    """Add a \\t for all following output in stdout"""
    global tabnum
    tabnum += 1
def delTab():
    global tabnum
    """Delete a \\t for all following output in stdout"""
    tabnum -= 1
def myPrint(str):
    str = tabnum*'\t' + str
    print(str)
    log.write(str + "\n")
    log.flush()

class MultipleInfoError(Exception):
    pass
class NoInfoError(Exception):
    pass

def findInfo(file, str, info_index: int = 1):
	"""Find the information inside \\title{}, \\author{} and so on.
 str contains a regex, info_index indicates the group number of the info"""
	res = None
	for line in file:
		match = re.search(str, line)
		if match:
			if res != None:
				raise MultipleInfoError
			assert res == None
			res = match.group(info_index)
	if res == None:
		raise NoInfoError
	return res

def compileCommand(filename):
    """Generate compile command (xelatex, bibtex)"""
    xelatex = ["xelatex",
              "-synctex=1",
              "-interaction=nonstopmode",
              "-file-line-error",
              "-shell-escape",
              filename]
    bibtex = ["bibtex", filename[:-4]]
    return xelatex, bibtex

def runCommand(command, check=True):
    import subprocess
    command_log = "Run command ["
    for item in command:
        command_log += "\"" + item + "\","
    myPrint(command_log + "]")
    return subprocess.run(command, check = check, stdout=open('nul', "w"))

def purge(reg):
    for file in os.listdir("."):
        if os.path.isfile(os.path.join(".", file)) and re.search(reg, file):
            os.remove(os.path.join(".", file))

def cleanCompile():
    """Clean up all temporary files during compliation"""
    purge(".*\.aux")
    purge(".*\.bbl")
    purge(".*\.blg")
    purge(".*\.out")
    purge(".*\.thm")

def runCompile(filename: str):
    """Run latex compiling."""
    myPrint("Compile file " + filename)
    addTab()
    xelatex, bibtex = compileCommand(filename)
    runCommand(xelatex)
    bibtex_result = runCommand(bibtex, check=False)
    runCommand(xelatex)
    if bibtex_result.returncode == 0:
        runCommand(xelatex)
    cleanCompile()
    delTab()

def appendSubfileList(pdf_directory, title, author):
    """Add an item into subfile_list.tex"""
    subfile_list.write("\\includepdf[pages=-,addtotoc={{1,section,1,{0}~~{1},a}}]{{{2}}}\n".format(title, author, pdf_directory.replace('\\','/')))
    subfile_list.flush()

def getPDFPage(pdf_path):
    """get the number of pages in pdf_path"""
    try:
        f = pdfplumber.open(pdf_path)
        page = len(f.pages)
    except PDFSyntaxError:
        page = 0
    return page

myPrint("Start compiling subfiles")
for dir in os.listdir("."):
    if os.path.isdir(dir) and dir not in ignore_directory:
        dir = os.path.join("." , dir)
        myPrint("Find directory " + dir)
        addTab()
        shutil.copyfile(cls_file_path, os.path.join(dir, "noithesis.cls"))
        for filename in os.listdir(path = dir):
            directory = os.path.join(dir, filename)
            if filename.endswith(".tex") and os.path.isfile(directory):
                myPrint("Find file " + directory)
                addTab()
                # Check whether the tex file is the main file(compilable file) by finding string \begin{document}
                document_index = -1
                file = []
                with open(directory, encoding="utf-8") as f:
                    file = f.readlines()
                    for index, line in enumerate(file):
                        if line.find(r"\begin{document}") != -1:
                            if document_index != -1:
                                raise MultipleInfoError
                            document_index = index
                
                if document_index != -1:
                    # Modify page number counter
                    if file[document_index + 1].find(r"\setcounter{page}{") != -1:
                        del file[document_index + 1]
                    file.insert(document_index + 1, "\\setcounter{{page}}{{{}}}\n".format(page_number))
                    with open(directory, "w", encoding="utf-8") as f:
                        f.writelines(file)
                    
                    # Find title & author
                    title = findInfo(file, r"\\title\s*{\s*(.*)\s*}")
                    author = findInfo(file, r"\\author\s*{\s*(.*)\s*}")
                    # Delete school, only keep the name
                    truncated_author = ""
                    for _char in reversed(author):
                        if '\u4e00' <= _char <= '\u9fa5':
                            truncated_author = _char + truncated_author
                        else:
                            break
                    myPrint("Info: {}, {}".format(title, truncated_author))
                    
                    # Append subfile list
                    pdf_directory = directory[:-4]+".pdf"
                    appendSubfileList(pdf_directory, title, truncated_author)
                    
                    # Compile
                    current_place = os.getcwd()
                    os.chdir(dir)
                    runCompile(filename)
                    os.chdir(current_place)
                    
                    # Update page_number
                    page_number += getPDFPage(pdf_directory)
                else:
                    myPrint("Not a compilable file, ignored.")
                delTab()
        delTab()
subfile_list.close()
runCompile("main.tex")
log.close()