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
each raw file with the respective elements of a 
data hierarchy.
"""

from xml.dom.minidom import Document

import os
import codecs
import datetime
import random

class CreateHeaderFile:
    """
    Class responsible to create the header file
    that will contain the other resource files
    to the parsing process.

    The header is created with ISO GrAF standards.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath
        self.annotation_list = []
        self.version = '1.0.0'
        self.filename = ''
        self.primaryfile = ''

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

        # Start the Header file
        doc = Document()

        doc_header = doc.createElement("documentHeader") # Required
        doc_header.setAttribute("xmlns", "http://www.xces.org"
                                         "/ns/GrAF/1.0/") # Required
        doc_header.setAttribute("xmlns:xlink", "http://www.w3.org"
                                               "/1999/xlink") # Required
        docID = random.randint(1, 1000000)
        doc_header.setAttribute("docID", "POIO-"+str(docID)) # Required
        doc_header.setAttribute("version", self.version) # Required
        now = datetime.datetime.now()
        doc_header.setAttribute("date.created",
            now.strftime("%Y-%m-%d")) # Required
        doc.appendChild(doc_header)

        # Branch fileDesc
        fileDesc = doc.createElement("fileDesc")
        fileName = doc.createElement("fileName")
        value = doc.createTextNode(self.filename)
        fileName.appendChild(value)
        extent = doc.createElement("extent") # Required
        extent.setAttribute("unit",self.unit) # Required
        extent.setAttribute("count",str(self.unitcount)) # Required

        # Required
        sourceDesc = doc.createElement("sourceDesc")
        if self.title != '':
            title = doc.createElement("title")
            value = doc.createTextNode(self.title)
            title.appendChild(value)
            sourceDesc.appendChild(title)

        if self.author != '':
            author = doc.createElement("author")
            author.setAttribute("age",self.authorage)
            author.setAttribute("sex",self.authorsex)
            value = doc.createTextNode(self.author)
            author.appendChild(value)
            sourceDesc.appendChild(author)

        # Required
        source = doc.createElement("source") # Required
        source.setAttribute("type",self.sourcetype) # Required
        value = doc.createTextNode(self.sourcename) # Required
        source.appendChild(value)
        sourceDesc.appendChild(source)

        if self.distributor != '':
            distributor = doc.createElement("distributor")
            value = doc.createTextNode(self.distributor)
            distributor.appendChild(value)
            sourceDesc.appendChild(distributor)

        # Required if there's no name the value should be self
        publisher = doc.createElement("publisher")
        value = doc.createTextNode(self.publisher)
        publisher.appendChild(value)
        sourceDesc.appendChild(publisher)

        if self.pubAddress != '':
            pubAddress = doc.createElement("pubAddress")
            value = doc.createTextNode(self.pubAddress)
            pubAddress.appendChild(value)
            sourceDesc.appendChild(pubAddress)

        # It's required but not mandatory
        if self.eAddress != '':
            eAddress = doc.createElement("eAddress") # Required
            eAddress.setAttribute("type",self.eAddress_type) # Required
            value = doc.createTextNode(self.eAddress) # Required
            eAddress.appendChild(value)
            sourceDesc.appendChild(eAddress)

        # Should use the ISO 8601 format YYYY-MM-DD
        pubDate = doc.createElement("pubDate")
        self.pubDate = now.strftime("%Y-%m-%d")
        pubDate.setAttribute("iso8601",self.pubDate)
        sourceDesc.appendChild(pubDate)

        # Required
        idno = doc.createElement("idno") # Required
        idno.setAttribute("type",self.idno_type) # Required
        value = doc.createTextNode(self.idno) # Required
        idno.appendChild(value)
        sourceDesc.appendChild(idno)

        if self.pubName != '':
            pubName = doc.createElement("pubName")
            pubName.setAttribute("type",self.pubName_type)
            value = doc.createTextNode(self.pubName)
            pubName.appendChild(value)
            sourceDesc.appendChild(pubName)

        if self.documentation != '':
            documentation = doc.createElement("documentation")
            value = doc.createTextNode(self.documentation)
            documentation.appendChild(value)
            sourceDesc.appendChild(documentation)

        fileDesc.appendChild(fileName)
        fileDesc.appendChild(extent)
        fileDesc.appendChild(sourceDesc)
        doc_header.appendChild(fileDesc)

        # Branch profileDesc
        profileDesc = doc.createElement("profileDesc")

        # Not required
        if len(self.language_list) > 0:
            langUsage = doc.createElement("langUsage")

            for lang in self.language_list:
                language = doc.createElement("language") # Use ISO 639
                language.setAttribute("iso639",lang[0])
                langUsage.appendChild(language)

                profileDesc.appendChild(langUsage)

        # Required at least the subject
        textClass = doc.createElement("textClass")  # Required
        textClass.setAttribute("catRef","PT") # Required the catRef
        subject = doc.createElement("subject")
        value = doc.createTextNode(self.subject)
        subject.appendChild(value)
        textClass.appendChild(subject)

        if self.domain != '':
            domain = doc.createElement("domain")
            value = doc.createTextNode(self.domain)
            domain.appendChild(value)
            textClass.appendChild(domain)

        if self.subdomain != '':
            subdomain = doc.createElement("subdomain")
            value = doc.createTextNode(self.subdomain)
            subdomain.appendChild(value)
            textClass.appendChild(subdomain)

        profileDesc.appendChild(textClass)

        # Required at least one person
        if len(self.participants_list) > 0:
            particDesc = doc.createElement("particDesc") # Required

            for part in self.participants_list:
                person = doc.createElement("person") # Required
                person.setAttribute("id",part[1]) # Required the id attribut
                person.setAttribute("age",part[2])
                person.setAttribute("sex",part[3])
                person.setAttribute("role",part[4])
                value = doc.createTextNode(part[0])
                person.appendChild(value)

                particDesc.appendChild(person)

            profileDesc.appendChild(particDesc)

        # Maybe it's possible to use the tag to do the
        # description of the data hierarchy and it's
        # not required
        if len(self.settings_list) >  0:
            settingDesc = doc.createElement("settingDesc")

            for sett in self.settings_list:
                setting = doc.createElement("setting")
                setting.setAttribute("who",sett[0])

                time = doc.createElement("time")
                value = doc.createTextNode(sett[1])
                time.appendChild(value)
                setting.appendChild(time)

                activity = doc.createElement("activity")
                value = doc.createTextNode(sett[2])
                activity.appendChild(value)
                setting.appendChild(activity)

                locale = doc.createElement("locale")
                value = doc.createTextNode(sett[3])
                locale.appendChild(value)
                setting.appendChild(locale)

                settingDesc.appendChild(setting)

            profileDesc.appendChild(settingDesc)

        doc_header.appendChild(profileDesc)

        # Branch dataDesc required in PoioAPI case
        dataDesc = doc.createElement("dataDesc") # Required
        primaryData = doc.createElement("primaryData") # Required
        primaryData.setAttribute("loc",self.primaryfile) # Required
        primaryData.setAttribute("f.id","text") # Required
        dataDesc.appendChild(primaryData)
        annotations = doc.createElement("annotations")

        for ann in self.annotation_list:
            annotation = doc.createElement("annotation") # Required
            annotation.setAttribute("loc",ann[0]) # Required
            annotation.setAttribute("f.id",ann[1]) # Required
            annotations.appendChild(annotation)

        dataDesc.appendChild(annotations)
        doc_header.appendChild(dataDesc)

        # Branch revisionDesc isn't required
        if len(self.changes_list) > 0:
            revisionDesc = doc.createElement("revisionDesc")

            for cha in self.changes_list:
                change = doc.createElement("change")
                changeDate = doc.createElement("changeDate")
                value = doc.createTextNode(cha[0])
                changeDate.appendChild(value)
                change.appendChild(changeDate)
                respName = doc.createElement("respName")
                value = doc.createTextNode(cha[1])
                respName.appendChild(value)
                change.appendChild(respName)
                item = doc.createElement("item")
                value = doc.createTextNode(cha[2])
                item.appendChild(value)
                change.appendChild(item)

                revisionDesc.appendChild(change)

            doc_header.appendChild(revisionDesc)

        # Start XML file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-header.hdr')
        f = codecs.open(file,'w','utf-8')

        # Write the content in XML file
        f.write(doc.toprettyxml(indent="  "))

        #Close XML file
        f.close()

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
