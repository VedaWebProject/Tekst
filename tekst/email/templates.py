"""
This solution is not pretty, but it has its reasoning:

1.  Why are these templates stored in memory?
    Because we'd have 1-3 file read operations for every email sent if we kept
    them in files. The memory footprint of keeping them in memory is negligible
    compared to the performance hit of reading these files every time.
2.  But then why isn't this one big dict literal but instead a sequence of
    operations that add to the template dictionary?
    Because we need a somewhat comfortable way for maintaining humans to read and write
    these multi-line templates without messing up line breaks and other formatting.

Long story short: It is what it is.
"""

from enum import Enum


# **********************************************************************************
# enUS - test
#

_enUS_test_subject = """
Test Email from {platform_name}
"""

_enUS_test_txt = """
Hi there, {first_name} {last_name}!

This is a plain text test email from {platform_name}, just for you!
"""

_enUS_test_html = """
<h1>Hi there, {first_name} {last_name}!</h1>
This is a <b>HTML</b> test email from <i>{platform_name}</i>, just for you!
"""


# **********************************************************************************
# enUS - verify
#

_enUS_verify_subject = """
{platform_name} Email Verification
"""

_enUS_verify_txt = """
Dear {first_name},

please verify your email address for {platform_name} by clicking the following link \
or copying and pasting it into your browser's address bar:

{web_url}/verify/?token={token}

Please note that this verification link \
is only valid for {token_lifetime_minutes} minutes.

See you on {platform_name} ({web_url})!
"""

_enUS_verify_html = """
Dear {first_name},
<br/>
<br/>
please verify your email address for {platform_name} by clicking the following link \
or copying and pasting it into your browser's address bar:
<br/>
<br/>
<a href="{web_url}/verify/?token={token}">
    {web_url}/verify/?token={token}
</a>
<br/>
<br/>
Please note that this verification link \
is only valid for {token_lifetime_minutes} minutes.
<br/>
<br/>
See you on <a href="{web_url}">{platform_name}</a>!
"""


EMAIL_TEMPLATES = {
    "enUS": {
        "test": {
            "subject": _enUS_test_subject,
            "txt": _enUS_test_txt,
            "html": _enUS_test_html,
        },
        "verify": {
            "subject": _enUS_verify_subject,
            "txt": _enUS_verify_txt,
            "html": _enUS_verify_html,
        },
    }
}


class TemplateIdentifier(Enum):
    TEST = "test"
    VERIFY = "verify"
