"""Simple script to make a Pokemon PDF book"""
import os
import io
import re
import requests
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from rich import print
from PyPDF2 import PdfFileWriter, PdfFileReader


# Below credit to code-maven, thank you!
# https://code-maven.com/add-image-to-existing-pdf-file-in-python
def add_image(name, id):
    """Function to add image to PDF"""
    in_pdf_file = f"./pdfs/{id}_{name}.pdf"
    out_pdf_file = f"./pdfs/{id}_{name}.pdf"
    img_file = f"./photos/{id}_{name}.png"

    packet = io.BytesIO()
    can = Canvas(packet)
    x_start = 250
    y_start = 660
    can.drawImage(
        img_file, x_start, y_start, width=120, preserveAspectRatio=True, mask="auto"
    )
    can.showPage()
    can.showPage()
    can.showPage()
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    new_pdf = PdfFileReader(packet)

    # read the existing PDF
    existing_pdf = PdfFileReader(open(in_pdf_file, "rb"))
    output = PdfFileWriter()

    for i in range(len(existing_pdf.pages)):
        page = existing_pdf.getPage(i)
        page.mergePage(new_pdf.getPage(i))
        output.addPage(page)

    outputstream = open(out_pdf_file, "wb")
    output.write(outputstream)
    outputstream.close()


BASE = "https://pokeapi.co/api/v2/pokemon"
params = {"offset": 0, "limit": 20}

response = requests.get(BASE, params=params).json()
pokemon = response["results"]

# Grabbing all of the pokemon and URLS
while response["next"]:
    response = requests.get(response["next"]).json()
    pokemon.extend(response["results"])

for item in pokemon:
    single_pokemon = item["url"]
    name = item["name"]
    X_AXIS = 250
    Y_AXIS = 630

    try:
        # Grab single pokemon and save image
        temp_poke = requests.get(single_pokemon).json()
        poke_id = temp_poke["id"]
        image_url = temp_poke["sprites"]["front_default"]
        response = requests.get(image_url)
        with open(f"./photos/{poke_id}_{name}.png", "wb") as f:
            f.write(response.content)

        # Initial build of Pokemon PDFs
        canvas = Canvas(f"./pdfs/{poke_id}_{name}.pdf", pagesize=LETTER)
        canvas.setFont("Times-Roman", 12)
        canvas.drawString(X_AXIS, Y_AXIS + 15, name)
        canvas.drawString(X_AXIS, Y_AXIS - 15, "Abilities:")
        Y_AXIS -= 30

        # Writing abilities to PDF
        for item in temp_poke["abilities"]:
            canvas.drawString(X_AXIS, Y_AXIS, item["ability"]["name"])
            Y_AXIS -= 15
        canvas.drawString(X_AXIS, Y_AXIS - 15, f"Height: {temp_poke['height']}")
        canvas.save()
        add_image(name=name, id=poke_id)
    except:
        print(f"I ran into an issue with {name}!")


# Below credit to geektechstuff to merge all the PDFs
# https://geektechstuff.com/2018/02/17/python-3-merge-multiple-pdfs-into-one-pdf/


# Sets the scripts working directory to the location of the PDFs
os.chdir("./pdfs")

# Get all the PDF filenames
pdf2merge = []
for filename in os.listdir("."):
    if filename.endswith(".pdf"):
        pdf2merge.append(filename)

# Required to sort all pokemon by ID
pdf2merge.sort(key=lambda f: int(re.sub("\D", "", f)))

pdfWriter = PdfFileWriter()

# loop through all PDFs
for filename in pdf2merge:
    # rb for read binary
    pdfFileObj = open(filename, "rb")
    pdfReader = PdfFileReader(pdfFileObj)
    # Opening each page of the PDF
    for pageNum in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(pageNum)
        pdfWriter.addPage(pageObj)

os.chdir("../")
# save PDF to file, wb for write binary
pdfOutput = open("pokemon.pdf", "wb")
# Outputting the PDF
pdfWriter.write(pdfOutput)
pdfOutput.close()
