"""Generate original synthetic stills. Run from backend with python -m evaluation.generate."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

IMAGES = Path(__file__).parent / "images"


def plaza():
    image = Image.new("RGB", (512, 320), "#96bdd1")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 145, 511, 319), fill="#858484")
    for x in range(0, 512, 64):
        draw.rectangle((x, 79, x + 59, 151), fill="#baa794")
        draw.rectangle((x + 21, 110, x + 40, 151), fill="#4d5962")
    return image


def fire(image, x, y):
    draw = ImageDraw.Draw(image)
    draw.rectangle((x - 52, y + 24, x + 53, y + 42), fill="#45392e")
    draw.polygon([(x-51,y+24),(x-65,y-7),(x-40,y-49),(x-31,y-17),
                  (x-3,y-106),(x+11,y-56),(x+26,y-80),(x+51,y-25),
                  (x+58,y+8),(x+45,y+24)], fill="#e64912")
    draw.polygon([(x-27,y+24),(x-33,y-4),(x-4,y-47),(x+8,y-14),
                  (x+24,y-35),(x+36,y+24)], fill="#ffbd36")


def main():
    IMAGES.mkdir(exist_ok=True)
    clear_fire = plaza()
    fire(clear_fire, 255, 223)
    clear_fire.save(IMAGES / "clear-fire.png")

    second_fire = plaza()
    fire(second_fire, 158, 208)
    fire(second_fire, 352, 231)
    second_fire.save(IMAGES / "two-fires.png")

    plaza().save(IMAGES / "empty-plaza.png")
    people = plaza()
    draw = ImageDraw.Draw(people)
    for x, color in [(185, "#293754"), (255, "#33513d"), (334, "#854d67")]:
        draw.ellipse((x - 13, 158, x + 13, 184), fill="#846046")
        draw.rounded_rectangle((x - 16, 185, x + 16, 229), radius=7, fill=color)
        draw.line((x - 8, 226, x - 12, 258), fill="#26272b", width=8)
        draw.line((x + 8, 226, x + 12, 258), fill="#26272b", width=8)
    people.save(IMAGES / "three-people.png")

    ImageEnhance.Brightness(clear_fire.filter(ImageFilter.GaussianBlur(5))).enhance(0.27).save(
        IMAGES / "dim-fire.png"
    )
    ambiguous = plaza()
    fire(ambiguous, 255, 223)
    ImageDraw.Draw(ambiguous).rectangle((153, 149, 365, 282), fill="#4d5758")
    ambiguous.filter(ImageFilter.GaussianBlur(3)).save(IMAGES / "obscured-glow.png")


if __name__ == "__main__":
    main()
