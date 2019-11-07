import os
import datetime

from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from pathlib import Path

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "c:/Workspace/miluk/resources/SPINS-platypi-38e22f94c8e5.json"

project = Path('c:/Workspace/miluk')
output = project / Path('./resources/output')
slips = project / Path('./resources/slips')

slip1 = 'Slip1.2.6 - see.png'


def setup():
    print('Setup')
    os.makedirs(output, exist_ok=True)


def run():
    print('Run')
    slip = slips / slip1
    source_img = Image.open(slip)

    detect_text(slip, source_img)

    datetime_object = datetime.datetime.now()
    file = 'output_' + datetime_object.strftime("%Y-%m-%d%H_%M_%S") + '.png'
    source_img.save(output / file, "PNG")


def detect_text(path, source_img):
    """Detects text in the file."""
    from google.cloud import vision
    import io

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)

    for page in response.full_text_annotation.pages:

        for block in page.blocks:
            print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                print('Paragraph confidence: {}'.format(
                    paragraph.confidence))
                write_block_box(source_img, paragraph.bounding_box.vertices, '#ff9999', 4)

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))
                    write_block_box(source_img, word.bounding_box.vertices, '#9999ff')

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))


def write_block_box(source_image, vertices, fill, width=1):
    print('write_block', vertices[1])
    draw = ImageDraw.Draw(source_image)

    draw.line((vertices[0].x, vertices[0].y, vertices[1].x, vertices[1].y), fill=fill, width=width)
    draw.line((vertices[1].x, vertices[1].y, vertices[2].x, vertices[2].y), fill=fill, width=width)
    draw.line((vertices[2].x, vertices[2].y, vertices[3].x, vertices[3].y), fill=fill, width=width)
    draw.line((vertices[0].x, vertices[0].y, vertices[3].x, vertices[3].y), fill=fill, width=width)

    del draw


def destroy():
    print("> Clean up")


if __name__ == '__main__':  # Program start from here
    setup()
    try:
        run()
    except KeyboardInterrupt:
        pass
    finally:
        destroy()
