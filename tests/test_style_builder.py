import sys, os, pytest
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from style_builder import StyleBuilder


def test_augmentation_adds_top_coexisting_tags():
    defaults = ["rock", "metal", "blues"]
    co = {"rock": {"metal": 0.9, "blues": 0.8}}
    sb = StyleBuilder(defaults, co)
    adds = sb.augment(["rock"])
    assert {a["tag"] for a in adds} == {"metal", "blues"}


def test_choose_excludes_from_gravity_map():
    defaults = ["rock", "metal", "pop"]
    co = {"rock": {"pop": 0.9}, "metal": {"pop": 0.8}}
    sb = StyleBuilder(defaults, co)
    excludes = sb.choose_excludes(["rock", "metal"], [])
    assert "pop" in excludes

def test_build_generates_description_and_excludes():
    defaults = ["rock", "metal", "pop"]
    co = {"rock": {"metal": 0.9, "pop": 0.8}, "metal": {"pop": 0.7}}
    sb = StyleBuilder(defaults, co)
    desc, excludes = sb.build("rock, no pop")
    assert "rock" in desc
    assert "pop" in excludes
