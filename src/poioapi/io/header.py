# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2012 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://www.cidles.eu/ltll/poio>
# For license information, see LICENSE.TXT
""" This module is to create the header file.
This file will contain the files that belongs to
each raw file with the respective elements.
"""

import datetime
import random

from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

class CreateHeaderFile:
    """
    Class responsible to create the header file
    that will contain the other resource files
    to the parsing parse.

    The header is created with ISO GrAF standards.

    """

    def __init__(self, basedirname):
        """Class's constructor.

        Parameters
        ----------
        basedirname : str
            Base path of the file to manipulate, without extension.

        """

        self.basedirname = basedirname
        self.annotation_list = []
        self.annotation_list_attributes = []
        self.version = '1.0.0'
        self.filename = ''
        self.primaryfile = ''
        self.dataType = 'text'

        # Can be tokens, bytes, words, etc...
        self.unit = 'words'
        self.unitcount = 0

        # Attributes of the Source Description
        self.title = ''

        # Can be web, contributor, distributor, etc...
        self.sourcetype = 'Contributor'
        self.sourcename = 'Cont'
        self.author = ''
        self.authorsex = ''
        self.authorage = ''
        self.distributor = ''
        self.publisher = 'self'
        self.pubAddress = ''
        self.eAddress = ''
        self.eAddress_type = 'email'
        self.pubDate = ''
        self.idno_type = 'ISBN' # Could be ISBN, LCD, etc...
        self.idno = '9164784' # It's required
        self.pubName_type = 'ebook' # Could be newspaper, ebook, etc..
        self.pubName = ''
        self.documentation = ''

        # The list of settings
        self.settings_list = []

        # The list of participants
        self.participants_list = []

        # The list of languages
        self.language_list = []

        # Text class attributes
        self.catRef = 'PT' # Required
        self.domain = ''
        self.subdomain = ''
        self.subject = 'Revitatilization'

        # The changes list
        self.changes_list = []

    def create_header(self):
        """Creates an xml file with all the comments of the
        Annotation Tree file.

        The languages codes should be in the ISO 639-1:2002,
        Code for the representation of names of languages —
        Part 1: Alpha-2 code.
        ISO 639-2:1998, Code for the representation of
        names and languages — Part 2: Alpha-3 code.

        The Date time must be code ISO 8601.

        See Also
        --------
        add_annotation
        add_change
        add_language
        add_participant
        add_setting

        """

        # Get the actual date hour time
        now = datetime.datetime.now()

        # Start the Header file
        element_tree = Element('documentHeader',
                {"xmlns":"http://www.xces.org/ns/GrAF/1.0/",
                 "xmlns:xlink":"http://www.w3.org/1999/xlink",
                 "docID":"POIO-"+str(random.randint(1, 1000000)),
                 "version":self.version,
                 "date.created":now.strftime("%Y-%m-%d")})

        # Branch fileDesc
        fileDesc = SubElement(element_tree,
            'fileDesc')
        fileName = SubElement(fileDesc, 'fileName')
        fileName.text = self.filename
        SubElement(fileDesc, 'extent',  {"unit":self.unit,
                                               "count":str(self.unitcount)})

        # Required
        sourceDesc = SubElement(fileDesc, "sourceDesc")
        if self.title != '':
            fileName = SubElement(sourceDesc, 'title')
            fileName.text = self.title

        if self.author != '':
            author = SubElement(sourceDesc, "author", {"age":self.authorage,
                                                       "sex":self.authorsex})
            author.text = self.author

        # Required
        source = SubElement(sourceDesc, "source", {"type":self.sourcetype})
        source.text = self.sourcename

        if self.distributor != '':
            distributor = SubElement(sourceDesc, "distributor")
            distributor.text = self.distributor

        # Required if there's no name the value should be self
        publisher = SubElement(sourceDesc, "publisher")
        publisher.text = self.publisher

        if self.pubAddress != '':
            pubAddress = SubElement(sourceDesc, "pubAddress")
            pubAddress.text = self.pubAddress

        # It's required but not mandatory
        if self.eAddress != '':
            eAddress = SubElement(sourceDesc, "eAddress",
                    {"type":self.eAddress_type})
            eAddress.text = self.eAddress

        # Should use the ISO 8601 format YYYY-MM-DD
        self.pubDate = now.strftime("%Y-%m-%d")
        SubElement(sourceDesc, "pubDate", {"iso8601":self.pubDate})

        # Required
        idno = SubElement(sourceDesc, "idno", {"type":self.idno_type})
        idno.text = self.idno

        if self.pubName != '':
            pubName = SubElement(sourceDesc, "pubName", {"type":self.pubName_type})
            pubName.text = self.pubName

        if self.documentation != '':
            documentation = SubElement(sourceDesc, "documentation")
            documentation.text = self.documentation

        # Branch profileDesc
        profileDesc = SubElement(element_tree, "profileDesc")

        # Not required
        if len(self.language_list) > 0:
            langUsage = SubElement(profileDesc, "langUsage")

            for lang in self.language_list:
                SubElement(langUsage, "language", {"iso639":lang[0]}) # Use ISO 639

        # Required at least the subject
        textClass = SubElement(profileDesc, "textClass", {"catRef":"PT"})
        subject = SubElement(textClass, "subject")
        subject.text = self.subject

        if self.domain != '':
            domain = SubElement(textClass, "domain")
            domain.text = self.domain

        if self.subdomain != '':
            subdomain = SubElement(textClass, "subdomain")
            subdomain.text = self.subdomain

        # Required at least one person
        if len(self.participants_list) > 0:
            particDesc = SubElement(profileDesc, "particDesc") # Required

            for part in self.participants_list:
                person = SubElement(particDesc, "person",
                        {"id":part[1], "age":part[2], "sex":part[3],
                         "role":part[4]}) # Required
                person.text = part[0]

        # Maybe it's possible to use the tag to do the
        # description of the data hierarchy and it's
        # not required
        if len(self.settings_list) >  0:
            settingDesc = SubElement(profileDesc, "settingDesc")

            for sett in self.settings_list:
                setting = SubElement(settingDesc, "setting", {"who":sett[0]})

                time = SubElement(setting, "time")
                time.text = sett[1]

                activity = SubElement(setting, "activity")
                activity.text = sett[2]

                locale = SubElement(setting, "locale")
                locale.text = sett[3]

        # Branch dataDesc required in PoioAPI case
        dataDesc = SubElement(element_tree, "dataDesc") #Required
        primaryData = SubElement(dataDesc, "primaryData",
                {"loc":self.primaryfile,"f.id":self.dataType}) #Required
        annotations = SubElement(primaryData, "annotations")

        for ann in self.annotation_list:
            annotation = SubElement(annotations, "annotation",
                    {"loc":ann[0],"f.id":ann[1]}) # Required

            # Add the annotations attributes
            if len(self.annotation_list_attributes) is not 0:
                for attributes in self.annotation_list_attributes:
                    if attributes[0]==ann[1]:
                        if attributes[1]=='linguistic_type':
                            linguistic_node = SubElement(annotation,
                                "linguistic_type")

                        for attribute in attributes[2]:
                            node_name = attribute.split(' - ')[0]
                            node_value = attribute.split(' - ')[1]
                            node_child = Element(node_name.lower())
                            node_child.text = node_value
                            if attributes[1]=='linguistic_type':
                                linguistic_node.append(node_child)
                            else:
                                annotation.append(node_child)

        # Branch revisionDesc isn't required
        if len(self.changes_list) > 0:
            revisionDesc = SubElement(dataDesc, "revisionDesc")

            for cha in self.changes_list:
                change = SubElement(revisionDesc, "change")

                changeDate = SubElement(change, "changeDate")
                changeDate.text = cha[0]

                respName = SubElement(change, "respName")
                respName.text = cha[1]

                item = SubElement(change, "item")
                item.text = cha[2]

        # Write and indent file
        filepath = self.basedirname + '.hdr'
        file = open(filepath,'wb')
        doc = minidom.parseString(tostring(element_tree))
        file.write(doc.toprettyxml(indent='  ', encoding='utf-8'))
        file.close()

    def add_annotation(self, loc, fid):
        """This method is responsible to add the
        annotations to the list of annotations.

        The annotations list in this class will
        represents the documents associated with
        the primary data document that this header
        will describe.

        Parameters
        ----------
        loc : str
            Relative path or PID of the annotation document.
        fid : str
            File type via reference to definition in the resource header.

        """

        self.annotation_list.append((loc, fid))

    def add_annotation_attributes(self, parent, type, values_list):
        """This method is responsible to add the
        annotations attribute values to a list.

        Parameters
        ----------
        parent : str
            Referes to what annotation the attributes belong.
        type : str
            The type of attribues.
        type : array-like
            Array that contains the values of the attributes.

        """

        self.annotation_list_attributes.append((parent, type, values_list))

    def add_change(self, changedate, responsible, item):
        """This method is responsible to add the
        annotations to the list of changes.

        The changes list in this class will
        represents the information about a
        particular change made to the document.

        Parameters
        ----------
        changedate : str
            Date of the change in ISO 8601 format.
        responsible : str
            Identification of the person responsible for the change.
        item : str
            Description of the change.

        """

        self.annotation_list.append(changedate, responsible, item)

    def add_language(self, language_code):
        """This method is responsible to add the
        annotations to the list of languages.

        The language list in this class will
        represents the language(s) that the
        primary data use.

        Parameters
        ----------
        language_code : str
            ISO 639 code(s) for the language(s) of the primary data.

        """

        self.annotation_list.append(language_code)

    def add_participant(self, name, id, age, sex, role):
        """This method is responsible to add the
        annotations to the list of participants.

        The parcipant list in this class will
        represents participants in an interaction
        with the data manipulated in the files pointed
        by the header.

        A participant is a person in this case and it's
        important and required to give the id.

        Parameters
        ----------
        name : str
            ISO 639 code(s) for the language(s) of the primary data.
        id : str
            Identifier for reference from annotation documents.
        age : int
            Age of the speaker.
        role : str
            Role of the speaker in the discourse.
        sex : str
            One of male, female, unknown.

        """

        self.annotation_list.append(name, id, age, sex, role)

    def add_setting(self, who, time, activity, locale):
        """This method is responsible to add the
        annotations to the list of settings.

        The setting list in this class will
        represents the setting or settings
        within which a language interaction takes
        place, either as a prose description or a
        series of setting elements.

        A setting is a particular setting in which
        a language interaction takes place.

        Parameters
        ----------
        who : str
            Reference to person IDs involved in this interaction.
        time : str
            Time of the interaction.
        activity : str
            What a participant in a language interaction is doing
            other than speaking.
        locale : str
            Place of the interaction, e.g. a room, a restaurant,
            a park bench.

        """

        self.annotation_list.append(who, time, activity, locale)