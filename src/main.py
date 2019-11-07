import os
from pathlib import Path

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "c:/Workspace/miluk/resources/SPINS-platypi-38e22f94c8e5.json"

project = Path('c:/Workspace/miluk')
slips = project/Path('./resources/slips')
slip1 = 'Slip1.2.6 - see.png'


def setup():
    print('Setup')


def run():
    print('Run')
    detect_text(slips/slip1)


def detect_text(path):
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

                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    print('Word text: {} (confidence: {})'.format(
                        word_text, word.confidence))

                    for symbol in word.symbols:
                        print('\tSymbol: {} (confidence: {})'.format(
                            symbol.text, symbol.confidence))


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
