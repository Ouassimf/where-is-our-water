class Waterbody:
    """Common base class for all waterbodies"""

    def __init__(self, name, bounding_box):
        self.name = name
        self.bounding_box = bounding_box

    def display_waterbody(self):
        print("Name : ", self.name, ", Box: ", self.bounding_box)

    def save_waterbody(self):
        print("Saved" + self.name)

    def delete_waterbody(self):
        print("Deleted" + self.name)
