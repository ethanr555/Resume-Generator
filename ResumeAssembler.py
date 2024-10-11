import sys
import json
import subprocess

def GenerateResumeLatexScript(portfolioJson, maxlineCount: int):
    def AddCareerEntry(title: str, company: str, dateRange: str, items):
        linecount = 1
        currentString = "\\textbf{" + title + ", " + company + "}"\
            + "\n" + "\\hspace{\\fill} \\textbf{" + dateRange + "}"\
            + "\n" + "\\begin{itemize}"
        for item in items:
            currentString = currentString + "\n\\item " + item
            linecount += 1

        currentString = currentString +  "\n" + "\\end{itemize}"
        return ( currentString, linecount )

    def AddEducationEntry(collegeName: str, degrees):
        linecount = 1
        currentString = "\\noindent \\textbf{" + collegeName + "}"\
            + "\n" + "\\begin{itemize}"
        for degree in degrees:
            currentString = currentString + "\n\item " + degree["DegreeTitle"] + ", " + degree["DegreeMajor"]
            currentString = currentString +  "\n" + "\\hspace{\\fill} " + degree["Date"]
            linecount += 1

        currentString = currentString + "\n" + "\\end{itemize}"
        return ( currentString, linecount )

    def AddProjectEntry(title: str, dateRange: str, items):
        linecount = 1
        currentString = "\\textbf{" + title + "}"\
            + "\n" + "\\hspace{\\fill} \\textbf{" + dateRange + "}"\
            + "\n" + "\\begin{itemize}"
        for item in items:
            currentString = currentString + "\t" + "\\item " + item
            linecount += 1

        currentString = currentString + "\n" + "\\end{itemize}"
        return ( currentString, linecount )

    def GenerateCommaItem(items, title):
        currentString = "\\item " + "\\textbf{" + title + ":} "
        for i in range(len(items)):
            currentString = currentString + items[i]
            if i < len(items)- 1:
                currentString = currentString + ", "
        return currentString

    def GenerateSkillSection(languages = {}, frameworks = {}, tools = {}, technical = {}, platforms = {}):
        #Generate skill section of resume here
        #Generate the header information for the section
        currentString = "\\subsection*{Skills}" + "\n" + "\\hrule height 2pt" + "\n" + "\\vspace{6pt}" + "\n" + "\\begin{itemize}"\
            + "\n\t" + GenerateCommaItem(languages, "Languages")\
            + "\n\t" + GenerateCommaItem(frameworks, "Frameworks")\
            + "\n\t" + GenerateCommaItem(tools, "Development Tools")\
            + "\n\t" + GenerateCommaItem(technical, "Technical")\
            + "\n\t" + GenerateCommaItem(platforms, "Platforms") + "\n" + "\end{itemize}"
        return ( currentString, 6 )
    
    def GenerateHeader(name = "", linkedIn = "", website = "", github = "", email = ""):
        currentString = "\\documentclass{article}" + "\n" + "\\usepackage{hyperref}"\
            + "\n" + "\\usepackage[top=0.5in,left=0.5in,right=0.5in,bottom=0.5in]{geometry}"\
            + "\n" + "\\pagenumbering{gobble}" + "\n" + "\\begin{document}"\
            \
            +  "\n" + "\\section*{" + name + "}" + "\n" + "\\hrule height 2pt"\
            +  "\n" + "\\vspace{6pt}" + "\n" + "\\scriptsize" + f"\n"\
            +  email + " $|$ "\
            + website + " $|$ "\
            + linkedIn + " $|$ "\
            + github + ""\
            +  "\n" + "\\footnotesize"
        return ( currentString, 5 )

    #Pregen
    portfolioBio = portfolioJson["Bio"]
    headerResult = GenerateHeader(portfolioBio["Name"], portfolioBio["LinkedIn"], portfolioBio["Website"], portfolioBio["Github"], portfolioBio["Email"])
    careerResults = []
    for career in portfolioJson["Career"]:
        careerResults.append(AddCareerEntry(career["Title"], career["CompanyName"], career["Date"], career["DescriptionItems"]))
    eduResults = []
    for edu in portfolioJson["Education"]:
        eduResults.append(AddEducationEntry(edu["UniversityName"], edu["Degrees"]))
    projectResults = []
    for project in portfolioJson["Projects"]:
        projectResults.append(AddProjectEntry(project["Name"], project["Date"], project["DescriptionItems"]))
    portfolioSkills = portfolioJson["Skills"]
    skillsResult = GenerateSkillSection(portfolioSkills["Languages"], portfolioSkills["Frameworks"], portfolioSkills["Tools"], portfolioSkills["Technical"], portfolioSkills["Platforms"])
    


    # Header Generation
    documentStrings = []
    totalLineCount = 0
    documentStrings.append(headerResult[0])
    totalLineCount += headerResult[1]

    # Experience section
    documentStrings.append((f"\n" + "\\subsection*{Experience}" + f"\n" + "\\hrule height 2pt" + f"\n" + "\\vspace{6pt}"))
    totalLineCount += 1   
    for career in careerResults:
        documentStrings.append(f"\n" + career[0])
        totalLineCount += career[1]

    # Education section
    documentStrings.append( f"\n" + "\\subsection*{Education}" + f"\n" + "\\hrule height 2pt" + f"\n" + "\\vspace{6pt}")
    totalLineCount += 1
    for edu in eduResults:
        documentStrings.append( f"\n" + edu[0])
        totalLineCount += edu[1]

    # Project section
    documentStrings.append( "\n" + "\\subsection*{Projects}" + "\n" + "\\hrule height 2pt" + "\n" + "\\vspace{6pt}")
    totalLineCount += 1

    #Calculate skill total with totalLineCount to see how much space can be given to projects
    remainingLineCount = maxlineCount - (totalLineCount + skillsResult[1])

    #Now generate project section with this limit
    projectLineRunningTotal = 0
    for project in projectResults:
        if project[1] + projectLineRunningTotal >= remainingLineCount:
            break
        else:
            documentStrings.append("\n" + project[0])
            projectLineRunningTotal += project[1]
        
    # Skills section
    documentStrings.append( f"\n" + skillsResult[0])
    documentStrings.append( f"\n" + "\\end{document}")
    return "".join(documentStrings)


def main():

    #Get Portfolio json
    portfolio = {}
    with open(sys.argv[1]) as portfolioFile:
      portfolio = json.load(portfolioFile)  
    
    MAXLINES = 50

    documentString = GenerateResumeLatexScript(portfolio, MAXLINES)

    with open("generated.tex", 'w') as texFile:
        texFile.write(documentString)
    print(documentString)

    subprocess.run(["pdflatex","--jobname=resume","generated.tex"])

main()