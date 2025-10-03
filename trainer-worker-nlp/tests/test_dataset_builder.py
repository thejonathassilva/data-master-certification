from app.services.dataset_builder import DatasetBuilder

class IntentsRepoFake:
    def list_active_by_subject(self, sid):
        return [
            {"name":"INT_A","examples":["Meu cartão não chegou","Perdi meu cartão"]},
            {"name":"INT_B","examples":["Quero aumentar limite"]},
        ]

class EntitiesRepoFake:
    def list_by_subject(self, sid):
        return [
            {"name":"CARTAO","patterns":[r"cart[aã]o"],"gazetteer":["limite"]},
        ]

def test_build_subject_dataset_generates_entities():
    ds = DatasetBuilder(IntentsRepoFake(), EntitiesRepoFake())
    train, dev = ds.build_subject_dataset("S1")
    all_samples = train + dev
    assert any(any(ent[0]=="CARTAO" for ent in s["entities"]) for s in all_samples)
    intents = {s["intent"] for s in all_samples}
    assert intents == {"INT_A","INT_B"}
