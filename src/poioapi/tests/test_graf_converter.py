import poioapi.io.graf

class SimpleParser(poioapi.io.graf.BaseParser):

    utterance_tier = ["this is a test" , "this is another test"]
    word_tier = [ ['this', 'is', 'a', 'test'], ['this', 'is', 'another', 'test'] ]
    graid_tier = [ 'a','b','c','d', 'e', 'f', 'g', 'h']

    tiers = [ "utterance", "word", "graid" ]

    def __init__(self):
        pass
        #print('ok')

    def get_root_tiers(self, tiers=None):
        return [poioapi.io.graf.Tier("utterance")]

    def get_child_tiers_for_tier(self, tier):
        if tier.name == "utterance":
            return [poioapi.io.graf.Tier("word")]
        if tier.name == "word":
            return [poioapi.io.graf.Tier("graid")]

        return None

    def get_annotations_for_tier(self, tier, annotation_parent=None):
        if tier.name == "utterance":
            return [poioapi.io.graf.Annotation(i, v) for i, v in enumerate(self.utterance_tier)]

        if tier.name == "word":
            return [poioapi.io.graf.Annotation(2 + 4*annotation_parent.id + i, v) for i, v in enumerate(self.word_tier[annotation_parent.id])]

        if tier.name == "graid":
            return [poioapi.io.graf.Annotation(annotation_parent.id+10, self.graid_tier[annotation_parent.id-2])]

        return []

    def tier_has_regions(self, tier):
        return False

    def region_for_annotation(self, annotation):
        pass

class TestGrAFConverter:

    def setup(self):
        parser = SimpleParser()
        self.converter = poioapi.io.graf.GrAFConverter(parser)

    def test_convert(self):
        self.converter.convert()
        print('ok')
