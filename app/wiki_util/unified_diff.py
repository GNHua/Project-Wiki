# This piece of code is writen by Isaac Turner.
# https://gist.github.com/noporpoise/16e731849eb1231e86d78f9dfeca3abc

import re
import difflib

_hdr_pat = re.compile("^@@ -(\d+),?(\d+)? \+(\d+),?(\d+)? @@$")
_no_eol = "\ No newline at end of file"


def apply_patch(s, patch, revert=False):
    """
    Apply unified diff patch to string s to recover newer string.
    If revert is True, treat s as the newer string, recover older string.

    Usage:
        str_after = apply_patch(str_before, patch)
        str_before = apply_patch(str_after, patch, revert=True)
    """
    s = s.splitlines(True)
    p = patch.splitlines(True)
    t = ''
    i = sl = 0
    (midx, sign) = (1, '+') if not revert else (3, '-')
    while i < len(p) and p[i].startswith(("---", "+++")):
        i += 1  # skip header lines
    while i < len(p):
        m = _hdr_pat.match(p[i])
        if not m:
            raise Exception("Cannot process diff")
        i += 1
        l = int(m.group(midx))-1 + (m.group(midx+1) == '0')
        t += ''.join(s[sl:l])
        sl = l
        while i < len(p) and p[i][0] != '@':
            if i+1 < len(p) and p[i+1][0] == '\\':
                line = p[i][:-1]
                i += 2
            else:
                line = p[i]
                i += 1
            if len(line) > 0:
                if line[0] == sign or line[0] == ' ':
                    t += line[1:]
                sl += (line[0] != sign)
    t += ''.join(s[sl:])
    return t


def make_patch(a, b):
    """
    Get unified string diff between two strings. Trims top two lines.
    Returns empty string if strings are identical.

    Usage:
        diff = make_patch(str_before, str_after)
    """
    diffs = difflib.unified_diff(a.splitlines(True), b.splitlines(True), n=0)
    try:
        _, _ = next(diffs), next(diffs)
    except StopIteration: 
        pass
    return ''.join([d if d[-1] == '\n' else d+'\n'+_no_eol+'\n' for d in diffs])
    
###############################################################################


def apply_patches(s, patches, revert=False):
    for patch in patches:
        s = apply_patch(s, patch, revert)
    return s

