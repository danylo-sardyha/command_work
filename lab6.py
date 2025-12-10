import logging
import os
import xml.etree.ElementTree as ET


class FileNotFound(Exception):
    pass


class FileCorrupted(Exception):
    pass


def logged(exc_type, mode="console"):
    logger = logging.getLogger("xml_logger")
    logger.setLevel(logging.ERROR)
    if not logger.handlers:
        handler = (
            logging.FileHandler("log.txt", encoding="utf-8")
            if mode == "file"
            else logging.StreamHandler()
        )
        logger.addHandler(handler)

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except exc_type as e:
                logger.error(f"[{func.__name__}] {e}")
                raise
        return wrapper
    return decorator


class XMLFileManager:
    def __init__(self, path):
        self.path = path

        if not os.path.exists(path):
            raise FileNotFound("Файл не знайдено")

        try:
            self.tree = ET.parse(path)
            self.root = self.tree.getroot()
        except:
            raise FileCorrupted("XML пошкоджено")

    @logged(FileCorrupted, mode="console")
    def read(self):
        try:
            return ET.tostring(self.root, encoding="unicode")
        except:
            raise FileCorrupted("Не вдалося прочитати XML")

    @logged(FileCorrupted, mode="file")
    def write(self, root_tag, data: dict):
        try:
            new_root = ET.Element(root_tag)

            for tag, value in data.items():
                child = ET.SubElement(new_root, tag)
                child.text = str(value)

            self.tree = ET.ElementTree(new_root)
            self.tree.write(self.path, encoding="utf-8", xml_declaration=True)
            self.root = new_root

        except:
            raise FileCorrupted("Помилка запису XML")


    @logged(FileCorrupted, mode="file")
    def append(self, film_tag, film_data: dict):
        """
        film_data: {
            "title": "...",
            "year": "2014",
            "rating": "8.6"
        }
        """

        try:
            new_film = ET.SubElement(self.root, film_tag)

            for tag, value in film_data.items():
                child = ET.SubElement(new_film, tag)
                child.text = str(value)
            films = list(self.root)
            def get_rating(elem):
                r = elem.find("rating")
                try:
                    return float(r.text)
                except:
                    return -9999   # мінімальний рейтинг для неправильних даних

            films.sort(key=get_rating, reverse=True)

            new_root = ET.Element(self.root.tag)
            for f in films:
                new_root.append(f)

            self.root = new_root
            self.tree = ET.ElementTree(new_root)
            self.tree.write(self.path, encoding="utf-8", xml_declaration=True)

        except:
            raise FileCorrupted("Не вдалося додати та відсортувати фільм")


if __name__ == "__main__":
    try:
        path = os.path.join(os.path.dirname(__file__), "lab6.xml")
        xml = XMLFileManager(path)

        print("До змін:")
        print(xml.read())

        xml.append("film4", {
            "title": "Avatar",
            "year": "2009",
            "rating": "7.8"
        })

        print("\nПісля додавання і сортування:")
        print(xml.read())

    except Exception as e:
        print("Помилка:", e)