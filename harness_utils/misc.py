import re
import shutil
import tempfile

def sed_inplace(filename, pattern, repl) -> None:
    '''
    Perform of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    See https://stackoverflow.com/a/31499114
    '''
    pattern_compiled = re.compile(pattern)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))

    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)