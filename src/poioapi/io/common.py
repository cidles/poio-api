# -*- coding: utf-8 -*-
#
# Poio Tools for Linguists
#
# Copyright (C) 2009-2014 Poio Project
# Author: António Lopes <alopes@cidles.eu>
# URL: <http://media.cidles.eu/poio/>
# For license information, see LICENSE.TXT

"""This module contains the common utilities between
the remain modules, such as the gloss list, pos list
and the tag set.
"""


class Gloss():
    gloss_list = ["AGR", "ST", "STR", "W", "CONS", "ANIM", "HUM", "INANIM", "ADD",
                  "ASP", "CESSIVE", "CMPL", "CON", "CONT", "CUST", "DUR", "DYN", "EGR",
                  "FREQ", "HAB", "INCEP", "INCH", "INCOMPL", "INGR", "INTS", "IPFV", "ITER",
                  "PFV", "PNCT", "PROG", "PRSTV", "REP", "RESLT", "SEMF", "STAT", "NCOMPL",
                  "PRF", "FV", "IV", "ABES", "ABL", "ABS", "ACC", "ADES", "ALL", "BEN",
                  "case marker - underspecified", "COMIT", "CONTL", "DAT", "DEL", "DEST",
                  "ELAT", "EQT", "ERG", "ESS", "GEN", "ILL", "INESS", "INSTR", "LAT", "MALF",
                  "NOM", "OBL", "PERL", "POSS", "PRTV", "TER", "VIAL", "VOC", "ORN", "CLITcomp",
                  "CLITadv", "CLITdet", "CLITn", "CLITp", "CLITpron", "CLITv", "ATV", "FAM", "INFOC",
                  "RFTL", "TPID", "UNID", "APPROX", "DIST", "DIST2", "DXS", "MEDIAL", "PROX", "AD",
                  "ADJ>ADV", "ADJ>N", "ADJ>V", "AUG", "DIM", "INCORP", "KIN", "N>ADJ", "N>ADV", "NMLZ",
                  "N>N", "NUM>N", "N>V", "PTCP>ADJ", "QUAL", "V>ADJ", "V>ADV", "vbl", ">Vitr", "V>N",
                  ">Vtr", "V>Nagt", "V>Ninstr", "ACAUS", "APASS", "APPL", "CAUS", "PASS", "ASRT",
                  "DECL", "EXCL", "IMP", "IMP1", "IMP2", "IND", "INTR", "MAVM", "PROH", "Q", "RPS",
                  "COMM", "FEM", "MASC", "NEUT", "COMPL", "DO", "ICV", "OBJ", "OBJ2", "objcogn", "OBJind",
                  "OM", "SBJ", "SC", "SM", "AFFMT", "CNTV", "COND", "CONJ", "CONTP", "EVID", "IRR", "JUSS",
                  "MOD", "OPT", "RLS", "SBJV", "OBLIG", "POT", "MNR", "MO", "CL", "CL1", "CL10", "CL11",
                  "CL12", "CL13", "CL14", "CL15", "CL16", "CL17", "CL18", "CL2", "CL20", "CL21", "CL22",
                  "CL23", "CL3", "CL4", "CL5", "CL6", "CL7", "CL8", "CL9", "Npref", "landmark", "DU",
                  "PL", "SG", "x", "DISTRIB", "1excl", "1incl", "1PL", "1SG", "2PL", "2SG",
                  "3B", "3PL", "3Pobv", "3Pprox", "3SG", "3Y", "4", "AREAL", "PLassc", "FT", "H", "!H",
                  "L", "MT", "RT", "NEGPOL", "POSPOL", "DEF", "INDEF", "SGbare", "SPECF", "PART", "2HML", "2HON",
                  "HON", "TTL", "AGT", "EXP", "GOAL", "PSSEE", "PSSOR", "PT", "SRC", "TH", "CIRCM", "CTed", "DIR",
                  "ENDPNT", "EXT", "INT", "LINE", "LOC", "PATH", "PRL", "SPTL", "STARTPNT", "VIAPNT", "DM", "MU",
                  "PS", "ANT", "AOR", "AUX", "FUT", "FUTclose", "FUTim", "FUTnear", "FUTrel", "FUTrm", "NF", "NFUT",
                  "NPAST", "PAST", "PASThst", "PASTim", "PASTpast", "PASTrel", "PASTrm", "PRES", "PRET", "FOC",
                  "TOP", "CNJ", "CLF", "CV", "GER", "GERDV", "INF", "itr", "PRED", "PTCP", "SUPN", "Vstem", "ACTV",
                  "?", "ABB", "ABSTR", "ADJstem", "ADV>ADJ", "ASS", "ASSOC", "ATT", "CMPR", "CO-EV", "CONSEC",
                  "CONTR", "COP", "DEG", "DEM", "DIR-SP", "EMPH", "EXPLET", "GNR", "IND-SP", "K1", "K2", "LOCREL",
                  "NEG", "Nstem", "oBEN", "PPOSTstem", "PRIV", "QUOT", "RECP", "REDP", "REFL", "REL", "RP-SP",
                  "sBEN", "SLCT", "SUP"]

    gloss_map = {"1": "CL1", "2": "CL2", "3": "CL3", "5": "CL5", "6": "CL6", "7": "CL7",
                       "8": "CL8", "9": "CL9", "14": "CL14", "15": "CL15", "16": "CL16",
                       "17": "CL17", "18": "CL18", "NPST": "NPAST", "EMP": "EMPH", "EXCLAM": "EXCL",
                       "COM": "COMIT", "PERF": "PFV", "CLAS": "CLF"}

    gloss_miss_list = []

    def _validate_gloss(self, gloss_value, extra_gloss_map=None):
        """
            This function validates the gloss value
            in a gloss list from the TC gloss list.
            """

        valid_glosses = []
        gloss_value = gloss_value.replace("-", "")

        # split gloss values
        for gl in gloss_value.split("."):
            for gloss in self.gloss_list:
                if gl.upper() == gloss.upper():
                    valid_glosses.append(gloss)

            if gl in self.gloss_map.keys():
                valid_glosses.append(self.gloss_map[gl])
            elif extra_gloss_map and gl in extra_gloss_map:
                valid_glosses.append(extra_gloss_map[gl])

        if valid_glosses:
            return valid_glosses
        else:
            if gloss_value not in self.gloss_miss_list:
                self.gloss_miss_list.append(gloss_value)

            return None


class POS():
    pos_list = ["PNposs", "N", "V", "PN", "ADVm", "Np", "PREP", "CN", "PRT", "COMP", "AUX", "CONJS", "QUANT",
                "NMASC", "NNO", "NNEUT", "COP", "ART", "MOD", "PPOST", "ADJ", "DEM", "ADJC", "PNrefl", "DET", "Wh",
                "Vtr", "Vitr", "PROposs", "P", "Vdtr", "CARD", "NDV", "CL", "ADVplc", "V3", "PRTposs", "V4",
                "ADVtemp", "V2", "NUM", "REL", "EXPL", "CONJC", "Vmod", "Vlght", "PNana", "PROint", "PNrel",
                "VtrOBL", "COPident", "PRTpred", "Nspat", "ORD", "PTCP", "CONJ", "PRTint", "Vneg", "PREPtemp",
                "PREPdir", "NFEM", "PRtinf", "Ncomm", "Nbare", "Vcon", "PRTv", "PRTn", "ADVneg", "Vpre", "NUMpart",
                "ADJS", "PRTexist", "CLFnum", "CLFnom", "CIRCP", "V1", "PREP/PROspt", "PRTprst", "Vvector", "PNdem",
                "Nrel", "IPHON", "ADV", "VitrOBL", "Vimprs", "Vrefl", "PNabs", "Vbid", "Vvec", "INTRJCT"]

    pos_map = {"prn": "PN", "interj": "INTRJCT", "CVB": "V", "pron": "PN", "part": "PRT", "intj": "INTRJCT",
               "name": "Np", "encl": "CL", "pred": "COP"}

    pos_miss_list = []

    def _validate_pos(self, pos_value, extra_pos_map=None):
        """
        This function validates the pos value
        in a pos list from the TC pos list.
        """

        value = None

        if "-" not in pos_value:
            for pos in self.pos_list:
                if pos_value.upper() == pos.upper():
                    value = pos
                    continue

            if pos_value in self.pos_map.keys():
                value = self.pos_map[pos_value]
            elif extra_pos_map and pos_value in extra_pos_map.keys():
                value = extra_pos_map[pos_value]

            if value is None:
                if pos_value not in self.pos_miss_list:
                    self.pos_miss_list.append(pos_value)

        return value
