import os
import pytest

from oakland.util import *

def test_remove_multiple_spaces():
    assert False

def test_parse_org():
    assert False

def test_remove_tags():
    tag_text = "<foo>bar</foo>"
    tagless_text = "bar"

    assert remove_tags(tag_text) == tagless_text
    
