#!/usr/bin/python3
"""Defines the HBnB console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


def fparse(farg):
    curly_braces = re.search(r"\{(.*?)\}", farg)
    brackets = re.search(r"\[(.*?)\]", farg)
    if curly_braces is None:
        if brackets is None:
            return [f.strip(",") for f in split(farg)]
        else:
            lexer = split(farg[:brackets.span()[0]])
            retl = [f.strip(",") for f in lexer]
            retl.append(brackets.group())
            return retl
    else:
        lexer = split(farg[:curly_braces.span()[0]])
        retl = [f.strip(",") for f in lexer]
        retl.append(curly_braces.group())
        return retl


class HBNBCommand(cmd.Cmd):
    """Defines the AirBnB command interpreter.

    Attributes:
        prompt (str): The command prompt.
    """

    prompt = "(hbnb) "
    __classes = {
        "BaseModel",
        "User",
        "State",
        "City",
        "Place",
        "Amenity",
        "Review"
    }

    def emptyline(self):
        """Do nothing upon receiving an empty line."""
        pass

    def default(self, farg):
        """Default behavior for cmd module when input is invalid"""
        fargdict = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }
        fmatch = re.search(r"\.", farg)
        if fmatch is not None:
            fargl = [farg[:fmatch.span()[0]], farg[fmatch.span()[1]:]]
            fmatch = re.search(r"\((.*?)\)", fargl[1])
            if fmatch is not None:
                command = [fargl[1][:fmatch.span()[0]], fmatch.group()[1:-1]]
                if command[0] in fargdict.keys():
                    call = "{} {}".format(fargl[0], command[1])
                    return fargdict[command[0]](call)
        print("*** Unknown syntax: {}".format(farg))
        return False

    def do_quit(self, farg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, farg):
        """EOF signal to exit the program."""
        print("")
        return True

    def do_create(self, farg):
        """Usage: create <class>
        Create a new class instance and print its id.
        """
        fargl = fparse(farg)
        if len(fargl) == 0:
            print("** class name missing **")
        elif fargl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            print(eval(fargl[0])().id)
            storage.save()

    def do_show(self, farg):
        """Usage: show <class> <id> or <class>.show(<id>)
        Display the string representation of a class instance of a given id.
        """
        fargl = fparse(farg)
        objdict = storage.all()
        if len(fargl) == 0:
            print("** class name missing **")
        elif fargl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(fargl) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(fargl[0], fargl[1]) not in objdict:
            print("** no instance found **")
        else:
            print(objdict["{}.{}".format(fargl[0], fargl[1])])

    def do_destroy(self, farg):
        """Usage: destroy <class> <id> or <class>.destroy(<id>)
        Delete a class instance of a given id."""
        fargl = fparse(farg)
        objdict = storage.all()
        if len(fargl) == 0:
            print("** class name missing **")
        elif fargl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(fargl) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(fargl[0], fargl[1]) not in objdict.keys():
            print("** no instance found **")
        else:
            del objdict["{}.{}".format(fargl[0], fargl[1])]
            storage.save()

    def do_all(self, farg):
        """Usage: all or all <class> or <class>.all()
        Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        fargl = fparse(farg)
        if len(fargl) > 0 and fargl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            objl = []
            for obj in storage.all().values():
                if len(fargl) > 0 and fargl[0] == obj.__class__.__name__:
                    objl.append(obj.__str__())
                elif len(fargl) == 0:
                    objl.append(obj.__str__())
            print(objl)

    def do_count(self, farg):
        """Usage: count <class> or <class>.count()
        Retrieve the number of instances of a given class."""
        fargl = fparse(farg)
        count = 0
        for obj in storage.all().values():
            if fargl[0] == obj.__class__.__name__:
                count += 1
        print(count)

    def do_update(self, farg):
        """Usage: update <class> <id> <attribute_name> <attribute_value> or
       <class>.update(<id>, <attribute_name>, <attribute_value>) or
       <class>.update(<id>, <dictionary>)
        Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary."""
        fargl = fparse(farg)
        objdict = storage.all()

        if len(fargl) == 0:
            print("** class name missing **")
            return False
        if fargl[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return False
        if len(fargl) == 1:
            print("** instance id missing **")
            return False
        if "{}.{}".format(fargl[0], fargl[1]) not in objdict.keys():
            print("** no instance found **")
            return False
        if len(fargl) == 2:
            print("** attribute name missing **")
            return False
        if len(fargl) == 3:
            try:
                type(eval(fargl[2])) != dict
            except NameError:
                print("** value missing **")
                return False

        if len(fargl) == 4:
            obj = objdict["{}.{}".format(fargl[0], fargl[1])]
            if fargl[2] in obj.__class__.__dict__.keys():
                valtype = type(obj.__class__.__dict__[fargl[2]])
                obj.__dict__[fargl[2]] = valtype(fargl[3])
            else:
                obj.__dict__[fargl[2]] = fargl[3]
        elif type(eval(fargl[2])) == dict:
            obj = objdict["{}.{}".format(fargl[0], fargl[1])]
            for k, v in eval(fargl[2]).items():
                if (k in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[k]) in {str, int, float}):
                    valtype = type(obj.__class__.__dict__[k])
                    obj.__dict__[k] = valtype(v)
                else:
                    obj.__dict__[k] = v
        storage.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
