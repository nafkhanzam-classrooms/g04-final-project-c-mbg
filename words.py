import random


def load_words():

    try:

        with open(
            "words.txt",
            "r",
            encoding="utf-8"
        ) as file:

            return [
                word.strip()
                for word in file.readlines()
                if word.strip()
            ]

    except:

        return [
            "kucing", "mobil", "rumah", "ayam", "sepeda", "komputer", 
            "meja", "kursi", "ikan", "burung", "pohon", "bunga", 
            "matahari", "bintang", "awan", "gunung", "pantai", "laut",
            "perahu", "pesawat", "buku", "pensil", "kunci", "pintu",
            "kulkas", "apel", "pisang", "anjing", "kelinci", "gitar"
        ]


WORDS = load_words()


def get_random_word():

    return random.choice(
        WORDS
    )