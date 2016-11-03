from xml.etree.ElementTree import parse
from sys import exit
from Tkinter import Tk
from tkFileDialog import askopenfilename, askdirectory
from tkMessageBox import askyesno
import html2text
from re import search, IGNORECASE, compile, escape, MULTILINE, DOTALL
from datetime import datetime
import os


flag_eHealth = 0
flag_UIM = 1.2

date_time = datetime.now()
month = date_time.month.numerator
q = (month - 1) / 3 + 1
dict_q = {1: 'March',
          2: 'June',
          3: 'September',
          4: 'December'}
quarter = dict_q[q]
year = date_time.year.numerator
filename_Standalone = "SupportSpecifications_%s_%s_Standalone.txt" % (year, quarter)
filename_Bundled = "SupportSpecifications_%s_%s_Bundled.txt" % (year, quarter)

filename_UIM = "SupportSpecifications_%s_%s_DCD%s.txt" % (year, quarter, flag_UIM)


def write_file(folder, file_name, body):
    fs_path = folder + '/' + file_name
    fs = open(fs_path, 'w')
    fs.write(body.encode('utf-8'))
    fs.close()

while True:
    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(title="Choose Input XML", initialdir=os.path.expanduser('~/Desktop'))

    if filename:
        break
    else:
        message_open = askyesno(title="Alert!", message="File cannot be opened! Try again?", default='yes')
        if message_open:
            pass
        else:
            exit()

errors = 0
tree = parse(filename)
root = tree.getroot()
bundle = ''
standalone = ''
result_message = ''
message_strategic = "STRATEGIC CERT:"
items = 0
begin = "\n\n########################################################################################\n"

hr = root.findall('HierarchicalRequirement')
for hr_part in hr:
    items += 1
    flag_Strategic = 0
    flag_Error = 0
    flag_Missing_cert = 0
    flag_Missing_trap = 0
    flag_Missing_uni = 0
    cert_match = 0
    trap_match = 0
    error_message = ''
    missing_message_cert = 'CERT:'
    missing_message_trap = 'TRAP:'
    missing_message_uni = ''
    title = hr_part.get('refObjectName')
    pattern = compile(' +', IGNORECASE)
    title = pattern.sub(' ', title)
    description = hr_part.findall('Description')
    format_ID = hr_part.find('FormattedID').text
    owner = hr_part.findall('Owner')[0].get('refObjectName')
    tags = hr_part.findall('Tags/_tagsNameArray/NamedObject/Name')
    for tag in tags:
        if tag.text == 'Strategic Cert':
            flag_Strategic = 1
    rd_cmt = hr_part.findall('c_RDComments')
    if flag_eHealth:
        cond_part = ["LIST OF AGENTS SUPPORTED:",
                     "LIST OF AGENTS TO BE ADDED:",
                     "DISCOVER MODE",
                     "ENVIRONMENT VARIABLE",
                     "AAG REPORT TECHNOLOGY"]
        cond_traps = ["LIST OF SUPPORTED TRAPS:",
                      "LIST OF TRAPS TO BE ADDED:"]
        cond_uni = ["COMMENTS",
                    "CUSTOMER NEXT STEP"]
    if flag_UIM:
        cond_part = ["LIST OF PREVIOUS SUPPORTED METRIC FAMILY AND VENDOR CERTIFICATION",
                     "LIST OF NEWLY SUPPORTED METRIC FAMILY AND VENDOR CERTIFICATION"]
        cond_traps = []
        cond_uni = ["COMMENT"]
    for cmt in rd_cmt:
        cmt_html = cmt.text
        cmt_text = html2text.html2text(cmt_html, '', 0)
        if True:
            cmt_text = cmt_text.replace("**", '')
            cmt_text = cmt_text.replace("\-", '-')
            pattern = compile(' +')
            cmt_text = pattern.sub(' ', cmt_text)
            cmt_text = cmt_text.replace(" \n", '\n')
            pattern = compile('\n+')
            cmt_text = pattern.sub('\n', cmt_text)
            cmt_text = cmt_text.replace("&gt;", '>')
            cmt_text = cmt_text.replace("&lt;", '<')
            pattern = compile(".*%s" % cond_part[0], IGNORECASE and MULTILINE and DOTALL)
            cmt_text = pattern.sub(cond_part[0], cmt_text)
            pattern = compile(".*LIST OF SUPPORTED TRAPS:", IGNORECASE and MULTILINE and DOTALL)
            cmt_text = pattern.sub('LIST OF SUPPORTED TRAPS:', cmt_text)
            pattern = compile(".*NO CODE CHANGE NEEDED.*", IGNORECASE and MULTILINE)
            need_trim = ['.*CODE CHANGE.*', '.*CHANGE SET.*', '.*github-isl-01.ca.com.*', '.*SHA-1.*', '\\\+', '\\\>',
                         '> ', '\n>']
            for element in need_trim:
                pattern = compile("%s" % element, IGNORECASE)
                cmt_text = pattern.sub('', cmt_text)
            if flag_eHealth:
                if search("PATCH DEPENDENT", cmt_text, IGNORECASE):
                    # pattern = compile("PATCH DEPENDENT.*\n.*", IGNORECASE)
                    # cmt_text = pattern.sub('', cmt_text)
                    error_message += "\tNeed to remove PATCH DEPENDENT\n"
                    flag_Error = 1
                if search("support.concord.com", cmt_text, IGNORECASE):
                    error_message += "\tNeed to change refer link (concord --> ehealth-spectrum)\n"
                    flag_Error = 1
                if search("Support-Concord@ca.com", cmt_text, IGNORECASE):
                    error_message += "\tNeed to change support email (Support-Concord --> TechnicalSupport)\n"
                    flag_Error = 1
                else:
                    pass
            else:
                pass
            for cond in cond_part:
                if search(cond, cmt_text, IGNORECASE):
                    pattern = compile(escape(cond), IGNORECASE)
                    cmt_text = pattern.sub("\n" + cond, cmt_text)
                    p = cond + ".*\n{2,}"
                    pattern = compile(p, DOTALL)
                    cert_match += 1
                else:
                    missing_message_cert = missing_message_cert + "\n" + "Missing " + cond
                    flag_Missing_cert = 1
            if flag_UIM:
                if flag_Missing_cert:
                    error_message = error_message + "\n" + missing_message_cert
            if flag_eHealth:
                if flag_Missing_cert:
                    for cond in cond_traps:
                        if search(cond, cmt_text, IGNORECASE):
                            flag_Missing_cert = 0
                            pattern = compile(escape(cond), IGNORECASE)
                            cmt_text = pattern.sub("\n" + cond, cmt_text)
                            trap_match += 1
                            print trap_match
                            print cmt_text
                        else:
                            missing_message_trap = missing_message_trap + "\n" + "Missing " + cond
                            flag_Missing_trap = 1
                if (flag_Missing_cert == 1) and (cert_match > 0):
                    error_message = error_message + "\n" + missing_message_cert
                if (flag_Missing_trap == 1) and (trap_match > 0):
                    error_message = error_message + "\n" + missing_message_trap
            for cond in cond_uni:
                if search(cond, cmt_text, IGNORECASE):
                    pattern = compile(escape(cond), IGNORECASE)
                    cmt_text = pattern.sub("\n" + cond, cmt_text)
                else:
                    error_message = error_message + "\n" + "Missing " + cond
                    flag_Missing_uni = 1

            if flag_Error == 1 or flag_Missing_cert == 1 or flag_Missing_trap == 1 or flag_Missing_uni == 1:
                errors += 1
                result_message += "---------------------------------------------------------------\n" + \
                                  "Error " + str(errors) + ":" + \
                                  owner + "\n" + \
                                  format_ID + "\n" + \
                                  error_message + "\n"
        else:
            pass
        cmt_text = cmt_text.replace("\"\"", '')
        cmt_text = cmt_text.strip()
        bundle = bundle + begin + format_ID + " " + title + "\n" + cmt_text
        if flag_Strategic == 1:
            message_strategic = message_strategic + "\n\t" + format_ID + " " + title
        else:
            standalone = standalone + begin + format_ID + " " + title + "\n" + cmt_text
uim = quarter + " " + str(year) + " - " + "DEVICE CERTIFICATION DEPLOYER " + str(flag_UIM) + " VERIFICATIONS\n" + bundle
uim = uim.replace("\n\n\n", "\n\n")
uim = uim.replace("\nMF", "\n\nMF")
print uim
bundle = quarter + " " + str(year) + " " + "VERIFICATIONS\n" + bundle
bundle = bundle.replace("\n\n\n", "\n\n")

standalone = quarter + " " + str(year) + " " + "VERIFICATIONS\n" + standalone
standalone = standalone.replace("\n\n\n", "\n\n")

print message_strategic
print "Items: %s" % items
if flag_eHealth:
    log_SupportSpecifications = "TOTAL CERT-Items: " + str(items) + "\n\n" + message_strategic + "\n\n" + result_message
if flag_UIM:
    log_SupportSpecifications = "TOTAL CERT-Items: " + str(items) + "\n\n" + "Error: " + str(errors) + "\n\n" \
                                + result_message

if errors > 0:
    result = askyesno(title=str(errors) + "errors were found!!!",
                      message=result_message + "\n\nSTILL CREATING NEW FILES?\n", default='yes')
else:
    result = True

while result:
    folder = askdirectory(initialdir=os.path.expanduser('~/Desktop'), title="Where to put output")
    if folder:
        if flag_eHealth:
            write_file(folder, filename_Bundled, bundle)
            write_file(folder, filename_Standalone, bundle)
            write_file(folder, 'log_SupportSpecifications.txt', log_SupportSpecifications)
            break
        if flag_UIM:
            write_file(folder, filename_UIM, uim)
            write_file(folder, 'log_SupportSpecifications.txt', log_SupportSpecifications)
            break
    else:
        message_save = askyesno(title="Alert!", message="Cannot save file! Try again?", default='yes')
        if message_save:
            pass
        else:
            exit()
exit()
