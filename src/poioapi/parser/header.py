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
each raw file with the respective morphemes, words,
clause units, utterances, wfw and the graids.
"""

from xml.dom.minidom import Document
from poioapi import annotationtree
from poioapi import data

import os
import pickle
import codecs
import datetime

class CreateHeaderFile:
    """
    Class responsible to create the header file
    that will contain the other resource files
    to the parsing process.

    """

    def __init__(self, filepath):
        """Class's constructor.

        Parameters
        ----------
        filepath : str
            Path of the file to manipulate.

        """

        self.filepath = filepath

    def create_header(self):
        """Creates an xml file with all the comments of the
        Annotation Tree file.

        ISO 639-1:2002, Code for the representation of
        names of languages — Part 1: Alpha-2 code.
        ISO 639-2:1998, Code for the representation of
        names and languages — Part 2: Alpha-3 code.

        Date time code ISO 8601.

        See Also
        --------
        poioapi.data : Here you can find more about the data
        hierarchies.

        """

        # Initialize the variable
        annotation_tree = annotationtree.AnnotationTree(data.GRAID)

        # Getting the label in data hierarchy
        cmt = data.DataStructureTypeGraid.data_hierarchy[3]
        utt = data.DataStructureTypeGraid.data_hierarchy[0]

        # Open the file
        file = open(self.filepath, "rb")
        annotation_tree.tree = pickle.load(file)

        doc = Document()

        doc_header = doc.createElement("documentHeader") # Required
        doc_header.setAttribute("xmlns", "http://www.xces.org"
                                         "/ns/GrAF/1.0/") # Required
        doc_header.setAttribute("xmlns:xlink", "http://www.w3.org"
                                               "/1999/xlink") # Required
        doc_header.setAttribute("docID", "CIDLeS-0001") # Required
        doc_header.setAttribute("version", "1.0.1") # Required
        now = datetime.datetime.now()
        doc_header.setAttribute("date.created",
            now.strftime("%Y-%m-%d")) # Required
        doc.appendChild(doc_header)

        # Branch fileDesc
        fileDesc = doc.createElement("fileDesc")
        fileName = doc.createElement("fileName")
        value = doc.createTextNode("Base name of the primary data file")
        fileName.appendChild(value)
        extent = doc.createElement("extent") # Required
        extent.setAttribute("count","100") # Required
        extent.setAttribute("unit","800") # Required

        sourceDesc = doc.createElement("sourceDesc")
        title = doc.createElement("title")
        value = doc.createTextNode("Minderico")
        title.appendChild(value)
        sourceDesc.appendChild(title)

        author = doc.createElement("author")
        value = doc.createTextNode("AntonioLopes")
        author.appendChild(value)
        sourceDesc.appendChild(author)

        source = doc.createElement("source") # Required
        source.setAttribute("type","publisher") # Required
        value = doc.createTextNode("AntonioLopes") # Required
        source.appendChild(value)
        sourceDesc.appendChild(source)

        distributor = doc.createElement("distributor")
        value = doc.createTextNode("CIDLeS distributor")
        distributor.appendChild(value)
        sourceDesc.appendChild(distributor)

        publisher = doc.createElement("publisher")
        value = doc.createTextNode("self")
        publisher.appendChild(value)
        sourceDesc.appendChild(publisher)

        pubAddress = doc.createElement("pubAddress")
        value = doc.createTextNode("Rua das escolas")
        pubAddress.appendChild(value)
        sourceDesc.appendChild(pubAddress)

        eAddress = doc.createElement("eAddress") # Required
        eAddress.setAttribute("type","email") # Required
        value = doc.createTextNode("alopes@cidles.eu") # Required
        eAddress.appendChild(value)
        sourceDesc.appendChild(eAddress)

        pubDate = doc.createElement("pubDate")
        value = doc.createTextNode("2012-01-01")
        pubDate.appendChild(value)
        sourceDesc.appendChild(pubDate)

        idno = doc.createElement("idno") # Required
        value = doc.createTextNode("ISBN:9933") # Required
        idno.appendChild(value)
        sourceDesc.appendChild(idno)

        pubName = doc.createElement("pubName")
        pubName.setAttribute("type","newspaper")
        value = doc.createTextNode("Jornal de Minde")
        pubName.appendChild(value)
        sourceDesc.appendChild(pubName)

        # Maybe it's possible to use the tag to do the
        # description of the data hierarchy
        documentation = doc.createElement("documentation")
        value = doc.createTextNode("The data can be found in the street")
        documentation.appendChild(value)
        sourceDesc.appendChild(documentation)

        fileDesc.appendChild(fileName)
        fileDesc.appendChild(extent)
        fileDesc.appendChild(sourceDesc)
        doc_header.appendChild(fileDesc)

        # Branch profileDesc
        profileDesc = doc.createElement("profileDesc")
        langUsage = doc.createElement("langUsage")
        language = doc.createElement("language") # Use ISO 639
        language.setAttribute("iso639","por")
        langUsage.appendChild(language)
        language = doc.createElement("language") # Use ISO 639
        language.setAttribute("iso639","pt")
        langUsage.appendChild(language)
        language = doc.createElement("language") # Use ISO 639
        language.setAttribute("iso639","ice")
        langUsage.appendChild(language)

        textClass = doc.createElement("textClass")  # Required
        textClass.setAttribute("catRef","PT") # Required the catRef
        subject = doc.createElement("subject")
        value = doc.createTextNode("Revitalization of Minderico")
        subject.appendChild(value)
        textClass.appendChild(subject)
        domain = doc.createElement("domain")
        value = doc.createTextNode("Library")
        domain.appendChild(value)
        textClass.appendChild(domain)
        subdomain = doc.createElement("subdomain")
        value = doc.createTextNode("Books")
        subdomain.appendChild(value)
        textClass.appendChild(subdomain)

        particDesc = doc.createElement("particDesc") # Required
        person = doc.createElement("person") # Required
        person.setAttribute("id","vf") # Required the id attribut
        person.setAttribute("age","30")
        person.setAttribute("role","Linguist")
        person.setAttribute("sex","F")
        value = doc.createTextNode("Vera Ferreira")
        person.appendChild(value)
        particDesc.appendChild(person)
        person = doc.createElement("person")
        person.setAttribute("id","pb") # Required the id attribut
        person.setAttribute("age","30")
        person.setAttribute("role","Linguist")
        person.setAttribute("sex","M")
        value = doc.createTextNode("Peter Bouda")
        person.appendChild(value)
        particDesc.appendChild(person)

        # Maybe it's possible to use the tag to do the
        # description of the data hierarchy
        settingDesc = doc.createElement("settingDesc")

        setting = doc.createElement("setting")
        setting.setAttribute("who","Peter Bouda")
        settingDesc.appendChild(setting)

        time = doc.createElement("time")
        value = doc.createTextNode("4 p.m.")
        time.appendChild(value)
        settingDesc.appendChild(time)

        activity = doc.createElement("activity")
        value = doc.createTextNode("Writing")
        activity.appendChild(value)
        settingDesc.appendChild(activity)

        locale = doc.createElement("locale")
        value = doc.createTextNode("Minde")
        locale.appendChild(value)
        settingDesc.appendChild(locale)

        profileDesc.appendChild(langUsage)
        profileDesc.appendChild(textClass)
        profileDesc.appendChild(particDesc)
        profileDesc.appendChild(settingDesc)
        doc_header.appendChild(profileDesc)

        # Branch dataDesc
        dataDesc = doc.createElement("dataDesc") # Required
        primaryData = doc.createElement("primaryData") # Required
        primaryData.setAttribute("loc","e.g. rawfile.txt") # Required
        primaryData.setAttribute("f.id","text") # Required
        dataDesc.appendChild(primaryData)
        annotations = doc.createElement("annotations")
        annotation = doc.createElement("annotation") # Required
        annotation.setAttribute("loc","file-morpheme.xml") # Required
        annotation.setAttribute("f.id","morpheme") # Required
        annotations.appendChild(annotation)
        dataDesc.appendChild(annotations)
        doc_header.appendChild(dataDesc)

        # Branch revisionDesc
        revisionDesc = doc.createElement("revisionDesc")
        change = doc.createElement("change")
        changeDate = doc.createElement("changeDate")
        value = doc.createTextNode("2012-02-12")
        changeDate.appendChild(value)
        respName = doc.createElement("respName")
        value = doc.createTextNode("ALopes")
        respName.appendChild(value)
        item = doc.createElement("item")
        value = doc.createTextNode("Change a wfw of ö to ã")
        item.appendChild(value)
        change.appendChild(changeDate)
        change.appendChild(respName)
        change.appendChild(item)
        revisionDesc.appendChild(change)
        doc_header.appendChild(revisionDesc)

        # Start XML file
        basename = self.filepath.split('.pickle')
        file = os.path.abspath(basename[0] + '-header.xml')
        f = codecs.open(file,'w','utf-8')

        # Write the content in XML file
        f.write(doc.toprettyxml(indent="  "))

        #Close XML file
        f.close()