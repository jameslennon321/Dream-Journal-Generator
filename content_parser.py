import os
import random

TEMPLATE_PATH = os.path.join(".", "templates")


class TemplateComponent:
    def __init__(self):
        self.sections = {}

    def add_entry(self, section, entry):
        if section not in self.sections:
            self.sections[section] = []
        self.sections[section].append(entry)


class DreamTemplate:
    def __init__(self):
        self.components = {}

    def load(self):
        for i in os.listdir(TEMPLATE_PATH):
            if i.endswith(".txt"):
                self._load_template_file(i)

    def _load_template_file(self, filename):
        full_filename = os.path.join(TEMPLATE_PATH, filename)

        current_section = ""
        component = TemplateComponent()

        with open(full_filename, "r") as openfile:
            lines = openfile.readlines()
            for line in lines:
                if len(line) <= 1:
                    continue
                if line[0] == "#":
                    section_name = line[1:len(line) - 1]
                    current_section = section_name
                else:
                    component.add_entry(current_section, line[0:len(line) - 1])
        self.components[filename.split(".")[0]] = component

    def _pick_random_component(self, query):
        parts = query.split("#")
        if len(parts) > 2:
            raise ValueError('Bad query string', query)

        if parts[0] not in self.components:
            raise ValueError('Component not found', parts[0])
        comp = self.components[parts[0]]

        section_name = "" if len(parts) == 1 else parts[1]
        if section_name not in comp.sections:
            raise ValueError('Section not found', section_name)
        values = comp.sections[section_name]
        if len(values) < 1:
            return False
        return self.parse_entry(random.sample(values, 1)[0])

    def parse_entry(self, entry):
        result = ""

        pos = entry.find("{")
        endpos = -1
        if pos == -1:
            return entry

        while pos != -1:
            result += entry[endpos + 1:pos]
            endpos = entry.find("}", pos + 1)
            cmd = entry[pos + 1:endpos]
            val = self.parse_command(cmd)
            result += val
            pos = entry.find("{", endpos)

        return result

    def parse_command(self, cmd):
        paren1 = cmd.find("(")
        paren2 = cmd.find(")", paren1)

        if paren1 == -1 or paren2 == -1:
            raise ValueError('Bad command string', cmd)

        fxn = cmd[0:paren1]
        args = cmd[paren1 + 1:paren2].split(",")
        if fxn == "load":
            return self._load_component(args)
        elif fxn == "enum":
            return self._enum(args)

    def _load_component(self, args):
        new = False
        if len(args) == 1 or True:
            return self._pick_random_component(args[0])
        raise NotImplementedError('Reused values not implemented')

    def _enum(self, args):
        if len(args) != 1:
            raise ValueError("Only one argument should be supplied to enum!", args)

        options = args[0].split("|")
        return self.parse_entry(random.sample(options, 1)[0])
