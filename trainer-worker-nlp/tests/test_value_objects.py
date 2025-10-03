import pytest
from app.domain.value_objects import SubjectId, ChannelName, Version, Confidence
from pydantic import BaseModel

class M(BaseModel):
    subject_id: SubjectId
    channel: ChannelName
    version: Version
    conf: Confidence

def test_subject_id_non_empty():
    m = M(subject_id=" S1 ", channel="pf", version="v1", conf=0.5)
    assert m.subject_id == "S1"

def test_channel_normalization_upper():
    m = M(subject_id="S1", channel=" pf ", version="v2", conf="0.7")
    assert m.channel == "PF"

def test_version_pattern_and_normalize():
    m = M(subject_id="S1", channel="PF", version="V10", conf=1)
    assert m.version == "v10"

def test_confidence_range():
    with pytest.raises(ValueError):
        M(subject_id="S1", channel="PF", version="v1", conf=1.1)
    with pytest.raises(ValueError):
        M(subject_id="S1", channel="PF", version="v1", conf=-0.01)
    m = M(subject_id="S1", channel="PF", version="v3", conf="0.0")
    assert m.conf == 0.0
