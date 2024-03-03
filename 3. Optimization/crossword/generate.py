import sys
import copy

from crossword import *


class CrosswordCreator:
    def __init__(self, crossword):
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        domain_copy = copy.deepcopy(self.domains)

        for variable in domain_copy:
            length = variable.length
            for word in domain_copy[variable]:
                if len(word) != length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        xoverlap, yoverlap = self.crossword.overlaps[x, y]

        revision_made = False

        domains_copy = copy.deepcopy(self.domains)

        if xoverlap:
            for xword in domains_copy[x]:
                matched_value = False
                for yword in self.domains[y]:
                    if xword[xoverlap] == yword[yoverlap]:
                        matched_value = True
                        break
                if matched_value:
                    continue
                else:
                    self.domains[x].remove(xword)
                    revision_made = True

        return revision_made

    def ac3(self, arcs=None):
        if not arcs:
            queue = []
            for variable1 in self.domains:
                for variable2 in self.crossword.neighbors(variable1):
                    if self.crossword.overlaps[variable1, variable2] is not None:
                        queue.append((variable1, variable2))

        while len(queue) > 0:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbour in self.crossword.neighbors(x):
                    if neighbour != y:
                        queue.append((neighbour, x))
            return True

    def assignment_complete(self, assignment):
        for variable in self.domains:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        words = [*assignment.values()]
        if len(words) != len(set(words)):
            return False

        for variable in assignment:
            if variable.length != len(assignment[variable]):
                return False

        for variable in assignment:
            for neighbour in self.crossword.neighbors(variable):
                if neighbour in assignment:
                    x, y = self.crossword.overlaps[variable, neighbour]
                    if assignment[variable][x] != assignment[neighbour][y]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        word_dict = {}

        neighbours = self.crossword.neighbors(var)

        for word in self.domains[var]:
            eliminated = 0
            for neighbour in neighbours:
                if neighbour in assignment:
                    continue
                else:
                    xoverlap, yoverlap = self.crossword.overlaps[var, neighbour]
                    for neighbour_word in self.domains[neighbour]:
                        if word[xoverlap] != neighbour_word[yoverlap]:
                            eliminated += 1
            word_dict[word] = eliminated

        sorted_dict = {
            k: v for k, v in sorted(word_dict.items(), key=lambda item: item[1])
        }

        return [*sorted_dict]

    def select_unassigned_variable(self, assignment):
        choice_dict = {}

        for variable in self.domains:
            if variable not in assignment:
                choice_dict[variable] = self.domains[variable]

        sorted_list = [
            v for v, k in sorted(choice_dict.items(), key=lambda item: len(item[1]))
        ]

        return sorted_list[0]

    def backtrack(self, assignment):
        if len(assignment) == len(self.domains):
            return assignment

        variable = self.select_unassigned_variable(assignment)

        for value in self.domains[variable]:
            assignment_copy = assignment.copy()
            assignment_copy[variable] = value
            if self.consistent(assignment_copy):
                result = self.backtrack(assignment_copy)
                if result is not None:
                    return result
        return None


def main():
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
