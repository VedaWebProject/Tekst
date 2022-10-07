from textrig.utils import strings


def test_safe_name():
    assert strings.safe_name("This is some test!") == "this_is_some_test"
    assert strings.safe_name("This    is a      test!") == "this_is_a_test"
    assert strings.safe_name("!  This is a test!") == "this_is_a_test"
    assert strings.safe_name("  These are 34 tests    ") == "these_are_34_tests"
    assert strings.safe_name("How-about-hyphens?") == "how_about_hyphens"
    assert strings.safe_name("Or Ümläüts?") == "or_umlauts"
    assert strings.safe_name("!!!!???????", min_len=3) == "___"
    assert strings.safe_name("!!!!???????") == ""
    assert strings.safe_name("François") == "francois"
    assert strings.safe_name("agníḥ pū́rvebhir ŕ̥ṣibhir") == "agnih_purvebhir_rsibhir"
    assert strings.safe_name("Today's temp is 32°C") == "today_s_temp_is_32_c"
    assert strings.safe_name("Thís is à têst!") == "this_is_a_test"
    assert strings.safe_name(b"foo bar") == "foo_bar"
    assert strings.safe_name(b"fo", min_len=3) == "fo_"
    assert strings.safe_name(b"This is a test!", max_len=8) == "this_is"
    assert strings.safe_name(b"foo barrrr", max_len=8) == "foo_barr"
    assert strings.safe_name("foo bar", delim="+") == "foo+bar"


def test_remove_diacritics():
    assert strings.remove_diacritics("Hörglwàartŝ") == "Horglwaarts"


def test_snake_to_camel_case():
    assert strings.snake_to_camel_case("foo_bar_baz") == "fooBarBaz"
