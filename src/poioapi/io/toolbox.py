# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2013 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

from __future__ import unicode_literals

import sys
import unicodedata
import re
import codecs

import poioapi.io.graf

# UTF-8 byte order mark
utf8_byte_order_mark = "\ufeff"

# Compile necessary regular expression
tier_marker_re = re.compile("^" + r"\\(\S+)(?=($|\s+))")
line_break_re = re.compile(r"(\r\n|\n|\r)+$")
bom_re = re.compile(r"^" + utf8_byte_order_mark)
header_marker_re = re.compile(r"^\\_sh\s+")
date_stamp_marker_re = re.compile(r"^\\_DateStampHasFourDigitYear")
id_marker_re = re.compile(r"^\\id\s+")

# Set the type of string
if sys.version_info[:2] >= (3, 0):
    string_type = str
else:
    string_type = basestring

class ToolboxLine(object):

    ############################################ Static methods

    @staticmethod
    def char_len(string, skip_invisibles=True, use_bytes=True):
        """
        Metho to calculate string length for Toolbox alignment.
        Based on Taras Zakharko's method.

        """
        length = 0
        
        # Go through Unicode characters in the string
        for character in string:

            # Get the length of the current character
            num_bytes = len(character.encode("utf-8"))
            
            # Get the unicode property for the current character
            category = unicodedata.category(character)
            
            # If we don't want to use byte alignment, here we do it:
            if not use_bytes:
                num_bytes = 1
            
            # Do we want to skip invisibles?
            if skip_invisibles and (category == "Mn" or category == "Mc" or \
                    category == "Me"):
                
                # Do exactly nothing as we ignore such characters
                pass
                
            else:
                
                # Advance the rendering position
                length += num_bytes
    
        return length

    ############################################ Constructor

    def __init__(self, *args):
        """
        General constructor
        (with a flexible number of arguments):

        """
        
        self._line_original = ""
        self._line_string = ""
        self._tier_marker = ""
        self._line_contents = ""
        self._line_break = ""
        self._line_tokenized = []
        self._line_whitespace = []
        self.dirty = False

        # Check which constructor is to be used
        
        # Construct line object from line str
        if len(args) == 1 and isinstance(args[0], string_type):
            line = args[0]
            
            # Keep original version of line
            self.line_original = line
            self.line_string = line
                    
        # Construct line contents from sensible parts:
        # tier marker, list of tokens, list of whitespace, line ending
        elif len(args) == 4:

            self._tier_marker = args[0]
            self._line_tokenized = args[1]
            self._line_whitespace = args[2]
            self.line_ending = args[3]

            # If a single whitespace string is provided instead
            # of a list of whitespace separators, use it between
            # all tokens
            if isinstance(self.line_whitespace, string_type):
                
                # Make sure that the whitespace is a valid whitespace
                # separator
                if not re.search(r"^\s+$", self.line_whitespace):
                    raise RuntimeError(
                        """Cannot join tokens of a ToolboxLine with"""
                        """ non-whitespace characters.""")
                
                self._line_whitespace = [self.line_whitespace] * len(
                    self.line_tokenized)
                        
            # Make sure that the supplied arguments
            # are the right kind of objects
            self.validate()

            # Construct the rest of the values
            # Combine tokens and whitespace into line_contents
            self._line_contents = ""
            for index in len(self.line_tokenized):
                token = self.line_tokenized[index]
                whitespace = self.line_whitespace[index]
                
                self._line_contents += whitespace + token

            self.line_string = self.tier_marker + self.line_contents + \
                self.line_break
            self.line_original = self.line_string
            
            # A newly constructed line is not dirty
            self.dirty = False
        
        # Construct line object from explicit arguments
        elif len(args) == 8:
            self._line_original = args[0]
            self._line_string = args[1]
            self._tier_marker = args[2]
            self._line_contents = args[3]
            self._line_break = args[4]
            self._line_tokenized = args[5]
            self._line_whitespace = args[6]
            self.dirty = args[7]
        
        # Wrong set of arguments used
        # Raise an error
        else:
            raise RuntimeError(
                """Cannot create a ToolboxLine object from the arguments you"""
                """ have supplied.""")

    ############################################ Properties

    # TODO: @Jan: Ich hab alle getter/setter in properties umgewandelt.
    # Einige davon sind nicht getestet. Falls möglich, könntest du deine
    # Skripte mit diesem Code testen?
    def line_original():
        doc = "The line_original property."
        def fget(self):
            return self._line_original
        def fset(self, value):
            self._line_original = value
            if self.line_original != self.line_string:
                self.dirty = True
        def fdel(self):
            del self._line_original
        return locals()

    line_original = property(**line_original())

    def line_string():
        doc = "The line_string property."
        def fget(self):
            return self._line_string
        def fset(self, line):
            self._line_string = line
        
            # Search for line ending
            match = line_break_re.search(line)
            if match:
                self._line_break = match.group(1)
            else:
                self._line_break = ""
                
            # Delete line ending from line
            line = line_break_re.sub("", line)
                
            # Search for tier marker
            match = tier_marker_re.search(line)
            if match:
                self._tier_marker = match.group(1)
            else:
                self._tier_marker = ""
                
            # Delete tier marker from line
            line = tier_marker_re.sub("", line)
                
            # Rest of the line is the line contents proper
            self._line_contents = line
                
            # Determine the whitespace in the original version
            # of the line
            self._line_whitespace = re.findall(r"\s+", line)
                
            # Tokenized version of line (split at whitespace)
            self._line_tokenized = line.strip().split()
            
            # Set dirty flag to true if line_original is not
            # equal to the new line_string
            if self.line_original != self.line_string:
                self.dirty = True
            else:
                self.dirty = False
        def fdel(self):
            del self._line_string
        return locals()
    line_string = property(**line_string())

    def tier_marker():
        doc = "The tier_marker property."
        def fget(self):
            return self._tier_marker
        def fset(self, value):
            # Update the attributes containing the whole line
            self.line_string = value + self.line_contents + \
                self.line_break
        def fdel(self):
            del self._tier_marker
        return locals()
    tier_marker = property(**tier_marker())

    def line_contents():
        doc = "The line_contents property."
        def fget(self):
            return self._line_contents
        def fset(self, value):
            self.line_string = self.tier_marker + value + \
                self.line_break
        def fdel(self):
            del self._line_contents
        return locals()
    line_contents = property(**line_contents())

    def line_break():
        doc = "The line_break property."
        def fget(self):
            return self._line_break
        def fset(self, value):
            self.line_string = self.tier_marker + self.line_contents + \
                value
        def fdel(self):
            del self._line_break
        return locals()
    line_break = property(**line_break())

    def line_tokenized():
        doc = "The line_tokenized property."
        def fget(self):
            return self._line_tokenized
        def fset(self, value):
            # Reconstruct the line contents
            self.line_whitespace = [" "] * len(value)
            new_line_contents = " " + " ".join(value)

            # Reconstruct the whole line string
            self.line_string = self.tier_marker + new_line_contents + \
                self.line_break
        def fdel(self):
            del self._line_tokenized
        return locals()
    line_tokenized = property(**line_tokenized())

    def line_whitespace():
        doc = "The line_whitespace property."
        def fget(self):
            return self._line_whitespace
        def fset(self, value):
            # If whitespace is provided as one string
            # use it to join the tokens together
            if isinstance(value, string_type):
                # Make sure that it is valid whitespace
                if not re.search(r"^\s+$", value):
                    raise RuntimeError(
                        "Cannot use non-whitespace string as a token separator"
                        "in a ToolboxLine.")
                
                self._line_whitespace = [value] * len(self.line_tokenized)
            
            elif type(value) == list:
                # Make sure the list of whitespace separators has
                # the correct length (equals the number of tokens)
                if len(value) != len(self.line_tokenized):
                    raise RuntimeError("The ToolboxLine has {0} tokens. "
                        "You only provided {1} whitespace separators.".format(
                            len(self.line_tokenized), len(value)))
                
                # Check that list elements are valid whitespace separators
                for w in value:
                    if not re.search(r"^\s+$", w):
                        raise RuntimeError(
                            "The list of whitespace separators for ToolboxLine"
                            " does not only contain whitespace elements.")
                
                # Build line contents
                new_line_contents = " " + whitespace.join(self.line_tokenized)                
                self.line_string = self.tier_marker + new_line_contents + \
                    self.line_break
        def fdel(self):
            del self._line_whitespace
        return locals()
    line_whitespace = property(**line_whitespace())

    ############################################ Methods

    def validate(self):
        """
        Methods to validate the wellformedness of the basic parts
        of a ToolboxLine

        """

        # Line ending has to be a string and should only consist
        # of the characters \r and \n or alternatively the empty string
        if not isinstance(self.line_ending, string_type):
            raise RuntimeError("Line ending has to be a string.")
            
        if self.line_ending != "" and not line_break_re.search(
                self.line_ending):
            raise RuntimeError(repr(self.line_ending),
                "is not a valid line ending.")

        # Tier marker has to be a nonempty string starting
        # with a "\" that does not contain whitespace
        if not isinstance(self.tier_marker, string_type):
            raise RuntimeError("Tier marker has to be a string.")
            
        if not tier_marker_re.search(self.tier_marker):
            raise RuntimeError("Tier marker is not well-formed:", repr(
                self.tier_marker))
            
        if re.search(r"\s", self.tier_marker):
            raise RuntimeError("Tier marker must not contain whitespace:", repr(
                self.tier_marker))
            
        # line_tokenized has to be a list of strings in which
        # each element must not contain whitespace
        if type(self.line_tokenized) != list:
            raise RuntimeError("Tokenized line has to be a list of strings.")
            
        for token in self.line_tokenized:
                
            if not isinstance(token, string_type):
                raise RuntimeError(
                    "List of tokens has to be a list of strings.")
                
            if re.search(r"\s", token):
                raise RuntimeError(
                    "Token in list of tokens must not contain whitespace:",
                    repr(token))

        # line_whitespace has to be a list of strings in which
        # each element has to consists of only whitespace
        if type(self.line_whitespace) != list:
            raise RuntimeError(
                "Whitespace separator list has to be a list of strings.")
            
        for token in self.line_whitespace:
                
            if not isinstance(token, string_type):
                raise RuntimeError(
                    "Whitespace separator list has to be a list of strings.")
                
            if not re.search(r"^\s+$", token):
                raise RuntimeError(
                    """Element of whitespace separator list does not"""
                    """ only contain whitespace:""", repr(token))
        
        # List of tokens and list of whitespace separators
        # have to have the same lengths
        if len(self.line_tokenized) != len(self.line_whitespace):
            raise RuntimeError(
                """List of tokens and list of whitespace separators have to """
                """have the same length.""")
        
        return True

    def words(self, affixes="-=", compound_marker="-", require_stem=False,
        allow_orphans=True):
        """
        Return a list of words in the line
        combining stems with prefixes and suffixes as well as clitics
        TODO: Deal with affixes directly attached to a word (without whitespace)

        """
        
        # A new list for words
        words = []
        
        # The current word
        cur_word = ""
        
        # Information about the preceding element
        last_element = ""
        
        # Define and compile regular expressions to detect affixes,
        # clitics, and compounds
        prefix_re = re.compile(r"^\S+[" + re.escape(affixes) + "]$")
        suffix_re = re.compile(r"^[" + re.escape(affixes) + "]\S+$")
        compound_re = re.compile(r"^[" + re.escape(compound_marker) + "]$")
        
        # Go through the list of tokens
        for index in range(len(self.line_tokenized)):
            
            # Get the token at the current position
            cur_token = self.line_tokenized[index]
            
            # Test whether the token is an affix or clitic or a compound marker
            if compound_re.search(cur_token):

                # Attach compound marker to preceding stem or suffix
                if last_element == "stem" or last_element == "suffix":
                    cur_word += self.line_whitespace[index]
                    cur_word += cur_token
                
                # TODO: @Jan: when das cur_token nur ein compund_marker ist
                # (also z.B. hat der Benutzer nur ein "-" eingetragen),
                # dann ging das hier schief; deswegen habe ich das "or"
                # eingefügt. Kann das Probleme machen?
                elif (last_element == "" and allow_orphans) or \
                    cur_token == compound_marker:
                    
                    # Start assembling the next word
                    cur_word = cur_token
                
                else:
                    # If the compound marker is preceded by anything other
                    # than a stem, raise an error
                    print(last_element)
                    print(cur_token)
                    raise RuntimeError(
                        "Toolbox line cannot be parsed into words (Yoho!): " + \
                        self.line_string)
                
                # Remember current type of element
                last_element = "compound marker"
                
            elif prefix_re.search(cur_token):
                
                # Start a new word if the preceding element is a stem
                # or a suffix
                if last_element == "stem" or last_element == "suffix":
                    
                    # Save current word
                    words.append(cur_word.strip())
                    
                    # Start assembling the next word
                    cur_word = cur_token
                
                # If the preceding element is a prefix, add the current prefix
                # to the same word
                elif last_element == "prefix":                    
                    cur_word += self.line_whitespace[index]
                    cur_word += cur_token
                
                # If the prefix is the first element, add it to the current word
                # without preceding whitespace
                elif last_element == "":
                    cur_word += cur_token
                
                # If the prefix follows a compound marker,
                # add the prefix to the current word
                else:
                    
                    cur_word += self.line_whitespace[index]
                    cur_word += cur_token
                
                # Remember current type of element
                last_element = "prefix"
            
            elif suffix_re.search(cur_token):
                
                # Add suffix to the current word if the preceding element
                # is a stem or a suffix
                if last_element == "stem" or last_element == "suffix":
                    cur_word += self.line_whitespace[index]
                    cur_word += cur_token
                
                # Suffix can be combined directly with a preceding prefix
                # if require_stem is False
                elif last_element == "prefix" and require_stem is False:
                    cur_word += self.line_whitespace[index]
                    cur_word += cur_token
                
                # If orphan suffixes allowed start a new word
                elif last_element == "" and allow_orphans is True:
                    cur_word = cur_token
                
                # Raise an error if a suffix follows a prefix, a compound
                # marker or is the first element in a word
                else:
                    # If the prefix is preceded by a compound marker
                    # raise an error
                    raise RuntimeError(
                        "Toolbox line cannot be parsed into words: " + \
                        self.line_string)

                # Remember current type of element
                last_element = "suffix"

            # Current token is a stem
            else:

                # Start a new word if the preceding element is a stem
                # or a suffix
                if last_element == "stem" or last_element == "suffix":
            
                    # Save current word
                    words.append(cur_word.strip())
                    
                    # Start assembling the next word
                    cur_word = cur_token
                
                # Add the stem to the current word if the preceding element
                # is a prefix, a compound marker
                elif last_element == "prefix" or \
                        last_element == "compound marker":
                    cur_word += self.line_whitespace[index]
                    cur_word += cur_token
                
                # The stem starts the first word on the line
                elif last_element == "":
                    cur_word = cur_token
   
                # Remember current type of element
                last_element = "stem"

        # Save last word on the list of words
        if cur_word != "":
            
            # Preceding element may not be a prefix or compound marker
            if (last_element == "prefix" or last_element == "compound marker") \
                    and allow_orphans is False:
                raise RuntimeError(
                    "Toolbox line cannot be parsed into words: " \
                    + self.line_string)
            
            else:
                # Add last word to the list of words
                words.append(cur_word.strip())
        
        # Return the list of words
        return words
    
    # How many words does the line contain?
    def number_of_words(self, affixes="-=", compound_marker="-",
            require_stem=False, allow_orphans=True):
        words = self.get_words(affixes=affixes, compound_marker=compound_marker,
            require_stem=require_stem, allow_orphans=allow_orphans)
        return len(words)

    # TODO: @Jan: Die ganzen "hooks" habe ich einfach so übernommen, sind nicht
    # getestet. Nur "repr" habe ich bisserl geändert, damits schöner aussieht.

    # Define useful hooks
    def __eq__(self, other):
        
        # If other is also a ToolboxLine
        if type(other) == ToolboxLine:
            
            # Compare string contents of Toolbox lines
            if self.line_string == other.line_string:
                return True
            else:
                return False
        
        # Compare ToolboxLine to str
        elif isinstance(other, string_type):
            
            # Compare the original string of the ToolboxLine
            # to the other string
            if self.line_string == other:
                return True
            else:
                return False

        else:
            # ToolboxLine object cannot be equal to anything
            # other than another ToolboxLine object or a string
            raise RuntimeError(
                """Cannot compare ToolboxLine to anything other than """
                """another ToolboxLine or a str(ing).""")

    def __ne__(self, other):
        if self.__eq__(other):
            return False
        else:
            return True
    
    def __gt__(self, other):
        # If other is also a ToolboxLine
        if type(other) == ToolboxLine:
            
            # Compare string contents of Toolbox lines
            if self.line_string > other.line_string:
                return True
            else:
                return False
        
        # Compare ToolboxLine to str
        elif isinstance(other, string_type):
            
            # Compare the original string of the ToolboxLine
            # to the other string
            if self.line_string > other:
                return True
            else:
                return False

        else:
            # ToolboxLine object cannot be equal to anything
            # other than another ToolboxLine object or a string
            raise RuntimeError(
                """Cannot compare ToolboxLine to anything otherthan another """
                """ToolboxLine or a str(ing).""")

    def __lt__(self, other):
        # If other is also a ToolboxLine
        if type(other) == ToolboxLine:
            
            # Compare string contents of Toolbox lines
            if self.line_string < other.line_string:
                return True
            else:
                return False
        
        # Compare ToolboxLine to str
        elif isinstance(other, string_type):
            
            # Compare the original string of the ToolboxLine
            # to the other string
            if self.line_string < other:
                return True
            else:
                return False

        else:
            # ToolboxLine object cannot be equal to anything
            # other than another ToolboxLine object or a string
            raise RuntimeError(
                """Cannot compare ToolboxLine to anything other than another """
                """ToolboxLine or a str(ing).""")

    def __ge__(self, other):
        # If other is also a ToolboxLine
        if type(other) == ToolboxLine:
            
            # Compare string contents of Toolbox lines
            if self.line_string > other.line_string or \
                    self.line_string == other.line_string:
                return True
            else:
                return False
        
        # Compare ToolboxLine to str
        elif isinstance(other, string_type):
            
            # Compare the original string of the ToolboxLine
            # to the other string
            if self.line_string > other or self.line_string == other:
                return True
            else:
                return False

        else:
            # ToolboxLine object cannot be equal to anything
            # other than another ToolboxLine object or a string
            raise RuntimeError(
                """Cannot compare ToolboxLine to anything other than """
                """another ToolboxLine or a str(ing).""")

    def __le__(self, other):
        # If other is also a ToolboxLine
        if type(other) == ToolboxLine:
            
            # Compare string contents of Toolbox lines
            if self.line_string < other.line_string or \
                    self.line_string == other.line_string:
                return True
            else:
                return False
        
        # Compare ToolboxLine to str
        elif isinstance(other, string_type):
            
            # Compare the original string of the ToolboxLine
            # to the other string
            if self.line_string < other or self.line_string == other:
                return True
            else:
                return False

        else:
            # ToolboxLine object cannot be equal to anything
            # other than another ToolboxLine object or a string
            raise RuntimeError(
                """Cannot compare ToolboxLine to anything other than """
                """another ToolboxLine or a str(ing).""")

    def __repr__(self):
        # Construct a readable representation of the Toolbox line
        ret = "\nOriginal:\t{0}\nTier marker:\t{1}\nContents:\t{2}\n" + \
            "Line break:\t{3}\nTokenized:\t{4}\nWhitespace:\t{5}\n" + \
            "Line changed?\t{6}\n".format(
                self.line_original, self.tier_marker, self. line_contents,
                self.line_break, self.line_tokenized, self.line_whitespace,
                self.dirty)
        return ret
    
    # Construct a string representation of the line
    def __str__(self):
        return self.line_string
    
    # Return the string length of the line
    def __len__(self):
        return len(self.line_string)
    
    # Hash the ToolboxLine object
    def __hash__(self):
        """
        Combine the current line string with the original line string
        in order to create a "unique" object

        """
        hash_string = self.line_string + self.line_original 
        return hash(hash_string)

class Toolbox:

    def __init__(self, filepath):
        """
        Constructor of the Toolbox object.

        Parameters
        ----------
        filepath : str
            Path to the input file.

        """
        self.filepath = filepath
        self.tiers = set()

    def lines(self):
        # Open input file
        input_file = open(self.filepath, "rb")
        
        # Collect ToolboxLine objects into a list
        toolbox_lines = []
        
        cur_line = ""
        cur_empty_line = ""
        
        # Go through lines in the input file
        for line in input_file:
            # TODO: @Jan: Hier hatte unsere Beispieldatei auf Github (s. auch
            # die Tests) Probleme, da wohl nicht-UTF-8-Zeichen in der Datei
            # vorkamen. Diese ignoriere ich jetzt. Hattest du schon ähnliche
            # Probleme?
            line = line.decode("utf-8", 'ignore')
            
            if line.strip() == "":
                
                cur_empty_line += line
            
            elif re.search(r"^\\", line):
                
                # Save preceding line
                if cur_line != "":
                    toolbox_lines.append(ToolboxLine(cur_line))
                    
                if cur_empty_line != "":
                    toolbox_lines.append(ToolboxLine(cur_empty_line))
                    
                cur_empty_line = ""
                cur_line = line
            
            else:
                
                if cur_empty_line != "":
                    cur_line += cur_empty_line
                    cur_empty_line = ""
                
                cur_line += line
        
        # Process last line
        if cur_line != "":
            toolbox_lines.append(ToolboxLine(cur_line))
            
        if cur_empty_line != "":
            toolbox_lines.append(ToolboxLine(cur_empty_line))
        
        return toolbox_lines

    def records(self, record_marker):
        toolbox_lines = self.lines()

        # List of Toolbox records    
        records = []
        
        # Material before the first record
        header = []
        
        # Record that is currently being assembled
        cur_record = []
        
        # Flag indicating whether the first record has been found
        found_first_record = False
        
        # Go through list of Toolbox lines
        for toolbox_line in toolbox_lines:
            
            # Look for record marker
            if toolbox_line.tier_marker == record_marker:
                
                # If this is the first record, save the previous lines,
                # as header
                if found_first_record is False:
                    records.append(header)
                    header = []
                
                # Otherwise save the current record
                else:
                    if len(cur_record) > 0:   
                        # Save the old record
                        records.append(cur_record)

                # Start a new record
                cur_record = []
                cur_record.append(toolbox_line)
                
                # Set flag to true
                found_first_record = True

                # add record_marker to tier list
                self.tiers.add(record_marker)
            
            # Found line without record marker
            else:
                # Found a header line
                if found_first_record is False:   
                    header.append(toolbox_line)
                
                # Found a record line
                else:                    
                    # Make sure a record marker has been found already
                    if len(cur_record) == 0:
                        raise RuntimeError(
                            "Record line found: {0}."
                            "But no preceding record marker line.".format(
                                toolbox_line))
                        return None
                    
                    else:                        
                        # Add current line to current record
                        cur_record.append(toolbox_line)

                        # add marker to tier list
                        if toolbox_line.tier_marker != "":
                            self.tiers.add(toolbox_line.tier_marker)
        
        # Make sure at least one record has been found
        if found_first_record is False:
            raise RuntimeError("Did not find any records.")
        
        # If the last record has not been added to the list of records,
        # do it now
        if len(cur_record) > 0:            
            records.append(cur_record)

        return records

class Parser(poioapi.io.graf.BaseParser):

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the Toolbox TXT file.

        """

        self.filepath = filepath
        self.record_marker = None
        self._record_ids = []
        self._record_dict = dict()

    def parse(self):
        """This method will parse the input file.

        """
        if not self.record_marker:
            raise(RuntimeError, "No record marker specified. For Toolbox files"
                " you have to set the Toolbox.record_marker (e.g. 'ref').")

        self.toolbox = Toolbox(self.filepath)
        self.records = self.toolbox.records(self.record_marker)
        self.header = self.records.pop(0)
        self._create_records_dict()

    def get_root_tiers(self):
        return [poioapi.io.graf.Tier(self.record_marker)]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == self.record_marker:
            tiers = []
            for t in self.toolbox.tiers:
                if t != self.record_marker:
                    tiers.append(poioapi.io.graf.Tier(t))
            return tiers

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == self.record_marker:
            return [poioapi.io.graf.Annotation(rec_id,
                self._record_dict[rec_id][self.record_marker])
                    for rec_id in self._record_ids]

        elif annotation_parent:
            if tier.name in self._record_dict[annotation_parent.id]:
                return [poioapi.io.graf.Annotation(i, word)
                    for i, word in enumerate(self._record_dict[
                        annotation_parent.id][tier.name])]
        return []

    def tier_has_regions(self, tier):
        return False

    def region_for_annotation(self, annotation):
        return None


    def get_primary_data(self):
        """This method returns the primary data of the Toolbox file.

        Returns
        -------
        primary_data : object
            PrimaryData object.

        """

        primary_data = poioapi.io.graf.PrimaryData()
        primary_data.type = poioapi.io.graf.NONE
        primary_data.filename = "unknown"

        return primary_data

    def _create_records_dict(self):
        for r in self.records:
            record_id = None
            cur_record_dict = dict()
            for line in r:
                if line.tier_marker == self.record_marker:
                    record_id = line.line_contents
                    self._record_ids.append(record_id)
                cur_record_dict[line.tier_marker] = line.words(
                    allow_orphans=True)
            self._record_dict[record_id] = cur_record_dict
