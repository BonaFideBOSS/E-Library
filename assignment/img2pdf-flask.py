from flask import Flask, send_file
import img2pdf
import requests
from io import BytesIO

app = Flask(__name__)


def images_to_pdf(image_urls):
    pdf_bytes = BytesIO()
    images = []
    for url in image_urls:
        response = requests.get(url)
        images.append(BytesIO(response.content))
    pdf_bytes.write(img2pdf.convert(images))
    pdf_bytes.seek(0)
    return pdf_bytes


@app.route("/")
def convert_images_to_pdf():
    image_urls = [
        "https://i.ibb.co/8xLJTHs/shah-rukh-khan-and-daniel-day-lewis.jpg",
        "https://i.ibb.co/ygtTty3/A-house-with-green-grass-and-a-tree.jpg",
    ]

    pdf_bytes = images_to_pdf(image_urls)
    response = send_file(pdf_bytes, as_attachment=True, download_name="images.pdf")
    return response


if __name__ == "__main__":
    app.run()
