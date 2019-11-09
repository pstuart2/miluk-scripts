import os
import datetime

from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from pathlib import Path

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "c:/Workspace/miluk/resources/SPINS-platypi-38e22f94c8e5.json"

project = Path('c:/Workspace/miluk')
output = project / Path('./resources/output')
slips = project / Path('./resources/slips')

# slip = slips / Path('Slip1.10.4 - matsi just right then precisely.png')
# slip = slips / Path('Slip1.11.1 - hamaq see.png')

TOP_LEFT = 0
TOP_RIGHT = 1
BOTTOM_RIGHT = 2
BOTTOM_LEFT = 3

FILE_SKIP = 10
FILE_LIMIT = 5

NEW_LINE_THRESHOLD = 20
SLANT_THRESHOLD = 5


def setup():
    print('Setup')
    os.makedirs(output, exist_ok=True)


def run():
    print('Run')

    count = 0

    for slip in slips.iterdir():
        count = count + 1

        if count < FILE_SKIP:
            continue

        if count >= FILE_SKIP + FILE_LIMIT:
            break

        print(f'{count} {slip}')
        source_img = Image.open(slip)

        detect_text(slip, source_img)

        datetime_object = datetime.datetime.now()
        file = slip.stem + '_' + datetime_object.strftime("%Y-%m-%d%H_%M_%S") + slip.suffix
        source_img.save(output / file, "PNG")
        del source_img


def detect_text(path, source_img):
    """Detects text in the file."""
    from google.cloud import vision
    import io

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.document_text_detection(image=image)

    last_top = -1
    last_bottom = -1

    for page in response.full_text_annotation.pages:

        for block in page.blocks:
            # print('\nBlock confidence: {}\n'.format(block.confidence))

            for paragraph in block.paragraphs:
                if has_negative(paragraph.bounding_box.vertices):
                    continue

                write_block_box(source_img, paragraph.bounding_box.vertices, '#ff9999', 4)

                for word in paragraph.words:
                    write_block_box(source_img, word.bounding_box.vertices, '#9999ff')
                    last_top, last_bottom = check_and_break(source_img, word.bounding_box.vertices, last_top,
                                                            last_bottom)


def write_block_box(source_image, vertices, fill, width=1):
    # print(f'Fill: {fill}')
    # print(f'TOP_LEFT {vertices[TOP_LEFT].x}, {vertices[TOP_LEFT].y}')
    # print(f'TOP_RIGHT {vertices[TOP_RIGHT].x}, {vertices[TOP_RIGHT].y}')
    # print(f'BOTTOM_RIGHT {vertices[BOTTOM_RIGHT].x}, {vertices[BOTTOM_RIGHT].y}')
    # print(f'BOTTOM_LEFT {vertices[BOTTOM_LEFT].x}, {vertices[BOTTOM_LEFT].y}')

    draw = ImageDraw.Draw(source_image)

    draw.line((vertices[TOP_LEFT].x, vertices[TOP_LEFT].y, vertices[TOP_RIGHT].x, vertices[TOP_RIGHT].y), fill=fill,
              width=width)
    draw.line((vertices[TOP_RIGHT].x, vertices[TOP_RIGHT].y, vertices[BOTTOM_RIGHT].x, vertices[BOTTOM_RIGHT].y),
              fill=fill, width=width)
    draw.line((vertices[BOTTOM_RIGHT].x, vertices[BOTTOM_RIGHT].y, vertices[BOTTOM_LEFT].x, vertices[BOTTOM_LEFT].y),
              fill=fill, width=width)
    draw.line((vertices[TOP_LEFT].x, vertices[TOP_LEFT].y, vertices[BOTTOM_LEFT].x, vertices[BOTTOM_LEFT].y), fill=fill,
              width=width)

    del draw


def check_and_break(source_image, vertices, last_top, last_bottom):
    current_top = get_most_top(vertices)
    current_bottom = get_most_bottom(vertices)

    print(f'------------')
    print(f'last_top: {last_top}, last_bottom: {last_bottom}')
    print(f'current_top: {current_top}, current_bottom: {current_bottom}')

    if last_top == -1:
        return current_top, current_bottom

    slant = get_slant(vertices)
    print(f'Slant = {slant}')

    if slant >= SLANT_THRESHOLD:
        print(f'Slant within threshold')
        last_bottom = current_bottom
        return last_top, last_bottom

    if current_top >= last_bottom or last_bottom - current_top <= NEW_LINE_THRESHOLD:
        print('Moved down a row')
        cl = current_top - last_bottom
        print(f'current_top - last_bottom = {cl}')
        cl2 = cl / 2
        print(f'cl / 2 = {cl2}')
        mid = cl2 + last_bottom
        if mid < last_bottom:
            mid = last_bottom

        draw_line(source_image, (0, mid, source_image.width, mid), fill='#239B56')
        last_top = current_top
        last_bottom = current_bottom
    else:
        if current_bottom > last_bottom:
            print('Moved slightly down')
            last_bottom = current_bottom

    return last_top, last_bottom


def get_most_top(vertices):
    if vertices[TOP_LEFT].y < vertices[TOP_RIGHT].y:
        return vertices[TOP_LEFT].y

    return vertices[TOP_RIGHT].y


def get_most_bottom(vertices):
    if vertices[BOTTOM_LEFT].y > vertices[BOTTOM_RIGHT].y:
        return vertices[BOTTOM_LEFT].y

    return vertices[BOTTOM_RIGHT].y


def has_negative(vertices):
    return vertices[TOP_LEFT].x < 0 or vertices[TOP_LEFT].x < 0


def draw_line(source_image, line, fill, width=1):
    print(f'LINE: {line[1]}')
    draw = ImageDraw.Draw(source_image)

    draw.line(line, fill=fill, width=width)

    del draw


def get_slant(vertices):
    return vertices[BOTTOM_RIGHT].y - vertices[BOTTOM_LEFT].y


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
