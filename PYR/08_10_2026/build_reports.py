"""Build and execute independent Python/R notebooks, then render their outputs."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import subprocess
import textwrap
import zipfile

ROOT = Path(__file__).resolve().parent
TMP = ROOT / 'tmp' / 'pdfs'
TMP.mkdir(parents=True, exist_ok=True)
R_SCRIPT = Path('C:/Program Files/R/R-4.6.1/bin/Rscript.exe')
cells = {'Python': [], 'R': []}

def md(lang, text):
    cells[lang].append({'cell_type': 'markdown', 'metadata': {}, 'source': text.strip()})

def code(lang, text):
    cells[lang].append({'cell_type': 'code', 'metadata': {}, 'source': textwrap.dedent(text).strip(),
                        'execution_count': None, 'outputs': []})

for lang in cells:
    md(lang, f'''# Radimsky - Palmer Penguins - {lang}
Practical work, Lab02. Source: the unchanged penguins.csv supplied with the assignment.
In Colab, upload the same penguins.csv into the notebook working directory.
The notebook was verified from start to finish in a fresh local process; the outputs below are real.
To meet the submission instructions, also execute it in Colab using Restart session and run all.
''')

md('Python', '## Part 1 - Inspect the dataset\nEach row represents one penguin observation. species and island are categorical variables; bill_length_mm measures bill length in mm and body_mass_g measures body mass in g. year is the numeric observation year, rather than a continuous body measurement.')
code('Python', '''
import pandas as pd
import numpy as np
from pathlib import Path
import hashlib
import sys
pd.set_option('display.width', 100)
pd.set_option('display.max_columns', 8)
source = Path('penguins.csv')
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
penguins = pd.read_csv(source, na_values=['NA'])
original = penguins.copy(deep=True)
print('Python:', sys.version.split()[0], '| pandas:', pd.__version__)
print(penguins.head(6).to_string(index=False))
print('Dimensions:', penguins.shape)
print('Types:\\n', penguins.dtypes.to_string())
print('Missing values:\\n', penguins.isna().sum().to_string())
assert penguins.shape == (344, 8)
print('PASS: 344 rows, 8 columns')
''')
md('R', '## Part 1 - Inspect the dataset\nEach row represents one penguin observation. species and island are categorical variables. bill_length_mm is bill length in mm, and body_mass_g is body mass in g. year is the numeric observation year.')
code('R', '''
options(width = 100)
source_file <- "penguins.csv"
source_hash <- unname(tools::md5sum(source_file))
penguins <- read.csv(source_file, na.strings = "NA", stringsAsFactors = FALSE)
original <- penguins
cat(R.version.string, "\\n")
print(head(penguins, 6), row.names = FALSE)
cat("Dimensions:", dim(penguins), "\\n")
print(vapply(penguins, function(x) paste(class(x), collapse = "/"), character(1)))
str(penguins)
print(colSums(is.na(penguins)))
stopifnot(identical(dim(penguins), c(344L, 8L)))
cat("PASS: 344 rows, 8 columns\\n")
''')
for lang in cells:
    md(lang, '''### Python/R comparison - inferred types
Python pandas reads flipper_length_mm and body_mass_g as float64 because ordinary NumPy integers cannot represent NaN. R reads these whole-number measurements as integer even with NA. year is int64 in Python and integer in R. Text columns are str in the pandas version used here and character in R; categorical meaning does not automatically imply a category/factor type. Decimal bill measurements are float64/double. Both implementations have identical dimensions and missing-value counts.''')

for lang in cells:
    md(lang, '## Part 2 - Select rows and columns\nObservations 5 through 10 refer to positions in the original file. Labels p01-p06 are illustrative and are not actual penguin identifiers.')
code('Python', '''
cols = ['species', 'island', 'flipper_length_mm']
selected = penguins.loc[:, cols].copy()
vector = penguins['flipper_length_mm']
one_column = penguins[['flipper_length_mm']]
print('Selection:', selected.shape)
print('1D:', type(vector).__name__, vector.shape, 'size:', vector.size)
print('Table:', type(one_column).__name__, one_column.shape, 'size:', one_column.size)
positions = selected.iloc[4:10]
print(positions.to_string(index=False))
assert selected.shape == (344, 3) and positions.shape == (6, 3)
assert vector.ndim == 1 and one_column.ndim == 2
small = selected.iloc[:6].copy()
small.index = [f'p{i:02d}' for i in range(1, 7)]
assert small.index.is_unique
print('Selection by labels:\\n', small.loc[['p02', 'p05']].to_string())
reverse = small.iloc[::-1]
print('Reversed table:\\n', reverse.to_string())
print('First row by position:\\n', reverse.iloc[[0]].to_string())
print('p01 by label:\\n', reverse.loc[['p01']].to_string())
assert reverse.index[0] == 'p06'
assert reverse.loc[['p01']].equals(small.loc[['p01']])
print('PASS: dimensions, unique labels and selections')
''')
code('R', '''
cols <- c("species", "island", "flipper_length_mm")
selected <- penguins[, cols, drop = FALSE]
vector <- penguins[["flipper_length_mm"]]
one_column <- penguins[, "flipper_length_mm", drop = FALSE]
cat("Selection:", dim(selected), "\\n")
cat("1D:", class(vector), "typeof:", typeof(vector), "length:", length(vector), "\\n")
cat("Table:", class(one_column), "dim:", dim(one_column), "\\n")
positions <- selected[5:10, , drop = FALSE]
print(positions, row.names = FALSE)
stopifnot(identical(dim(selected), c(344L, 3L)),
          identical(dim(positions), c(6L, 3L)), length(vector) == 344L,
          identical(dim(one_column), c(344L, 1L)))
small <- head(selected, 6)
rownames(small) <- sprintf("p%02d", 1:6)
stopifnot(!anyDuplicated(rownames(small)))
print(small[c("p02", "p05"), , drop = FALSE])
reverse <- small[6:1, , drop = FALSE]
print(reverse)
cat("First row by position:\\n")
print(reverse[1, , drop = FALSE])
cat("p01 by label:\\n")
print(reverse["p01", , drop = FALSE])
stopifnot(rownames(reverse)[1] == "p06",
          identical(reverse["p01", , drop = FALSE], small["p01", , drop = FALSE]))
cat("PASS: dimensions, unique labels and selections\\n")
''')
for lang in cells:
    md(lang, 'After reversing the rows, p06 occupies the first position, while p01 still identifies the original first row. Positional selection follows order; label selection follows identity. Python positions start at 0 and the slice endpoint is excluded; R positions start at 1. In R, preserve a table with drop = FALSE or with penguins["flipper_length_mm"].')

for lang in cells:
    md(lang, '## Part 3 - Filter observations\nEach filter starts independently from penguins. Missing measurements are explicitly excluded. For readability, the first ten retained rows are displayed; complete results are stored in f1, f2 and f3. Checks cover every retained row.')
code('Python', '''
mask1 = penguins.flipper_length_mm.notna() & (penguins.flipper_length_mm >= 210)
mask2 = ((penguins.species == 'Gentoo') & penguins.body_mass_g.notna()
         & (penguins.body_mass_g >= 5000))
mask3 = ((penguins.island.isin(['Biscoe', 'Dream']))
         & penguins.bill_length_mm.notna() & (penguins.bill_length_mm < 45))
f1 = penguins.loc[mask1].copy()
f2 = penguins.loc[mask2].copy()
f3 = penguins.loc[mask3].copy()
for label, result, relevant in [
    ('F1', f1, ['species', 'island', 'flipper_length_mm']),
    ('F2', f2, ['species', 'body_mass_g']),
    ('F3', f3, ['island', 'bill_length_mm'])]:
    print(label, 'count:', len(result))
    print(result[relevant].head(10).to_string(index=False))
assert f1.flipper_length_mm.notna().all() and (f1.flipper_length_mm >= 210).all()
assert (f2.species == 'Gentoo').all() and f2.body_mass_g.notna().all()
assert (f2.body_mass_g >= 5000).all()
assert f3.island.isin(['Biscoe', 'Dream']).all()
assert f3.bill_length_mm.notna().all() and (f3.bill_length_mm < 45).all()
filter_counts = [len(f1), len(f2), len(f3)]
print('PASS: every retained row meets the conditions', filter_counts)
''')
code('R', '''
mask1 <- !is.na(penguins$flipper_length_mm) & (penguins$flipper_length_mm >= 210)
mask2 <- (penguins$species == "Gentoo") & !is.na(penguins$body_mass_g) &
         (penguins$body_mass_g >= 5000)
mask3 <- ((penguins$island == "Biscoe") | (penguins$island == "Dream")) &
         !is.na(penguins$bill_length_mm) & (penguins$bill_length_mm < 45)
f1 <- penguins[mask1, , drop = FALSE]
f2 <- penguins[mask2, , drop = FALSE]
f3 <- penguins[mask3, , drop = FALSE]
cat("F1 count:", nrow(f1), "\\n")
print(head(f1[, c("species", "island", "flipper_length_mm")], 10), row.names = FALSE)
cat("F2 count:", nrow(f2), "\\n")
print(head(f2[, c("species", "body_mass_g")], 10), row.names = FALSE)
cat("F3 count:", nrow(f3), "\\n")
print(head(f3[, c("island", "bill_length_mm")], 10), row.names = FALSE)
stopifnot(all(!is.na(f1$flipper_length_mm)), all(f1$flipper_length_mm >= 210),
          all(f2$species == "Gentoo"), all(!is.na(f2$body_mass_g)),
          all(f2$body_mass_g >= 5000), all(f3$island %in% c("Biscoe", "Dream")),
          all(!is.na(f3$bill_length_mm)), all(f3$bill_length_mm < 45))
filter_counts <- c(nrow(f1), nrow(f2), nrow(f3))
cat("PASS: every retained row meets the conditions:", filter_counts, "\\n")
''')
md('R', '### Logical mask containing NA\nDirect indexing inserts an unknown row for each NA in the mask. subset() retains only TRUE and drops NA. The corrected mask explicitly excludes NA; na.rm = TRUE is not used as a substitute for checking an incorrect filter.')
code('R', '''
mass_mask <- penguins$body_mass_g >= 5000
direct <- penguins[mass_mask, , drop = FALSE]
via_subset <- subset(penguins, body_mass_g >= 5000)
correct_mask <- !is.na(mass_mask) & mass_mask
corrected <- penguins[correct_mask, , drop = FALSE]
unknown_rows <- rowSums(is.na(direct)) == ncol(direct)
cat("NA entries in the mask:", sum(is.na(mass_mask)), "\\n")
cat("Direct indexing:", nrow(direct), "; all-NA rows:", sum(unknown_rows), "\\n")
print(direct[unknown_rows, , drop = FALSE])
cat("subset:", nrow(via_subset), "; corrected mask:", nrow(corrected), "\\n")
stopifnot(!anyNA(correct_mask), identical(corrected, via_subset),
          nrow(direct) == nrow(corrected) + sum(is.na(mass_mask)))
cat("PASS: the explicitly corrected mask matches subset()\\n")
''')
for lang in cells:
    md(lang, 'In Python, comparing float NaN with a threshold returns False; in R, comparing NA returns NA. Both workflows therefore explicitly require a known measurement. With this handling, all three filter counts agree between Python and R; this agreement is also checked when building the reports.')

for lang in cells:
    md(lang, '## Part 4 - Build a working table\nThe conversion is vectorized: grams / 1000. Species is sorted ascending, mass descending, and missing masses last within each species. When both sorting keys tie, an explicit auxiliary position key preserves the original order. This auxiliary key is not retained in working.')
code('Python', '''
working = penguins[['species', 'island', 'flipper_length_mm', 'body_mass_g']].copy()
working['body_mass_kg'] = working.body_mass_g / 1000
working['_source_row'] = np.arange(len(working))
working = working.sort_values(
    ['species', 'body_mass_g', '_source_row'], ascending=[True, False, True],
    na_position='last').drop(columns='_source_row').reset_index(drop=True)
print(working.head(10).to_string(index=False))
known = working.body_mass_g.notna()
assert np.allclose(working.loc[known, 'body_mass_kg'],
                   working.loc[known, 'body_mass_g'] / 1000, rtol=0, atol=1e-12)
assert len(working) == len(penguins)
assert working.body_mass_g.isna().sum() == penguins.body_mass_g.isna().sum()
assert penguins.shape[1] == 8 and working.shape[1] == 5
assert working.species.is_monotonic_increasing
for _, group in working.groupby('species', sort=False):
    assert group.body_mass_g.dropna().is_monotonic_decreasing
    assert group.body_mass_g.isna().is_monotonic_increasing
pd.testing.assert_frame_equal(penguins, original)
print('PASS: conversion (atol=1e-12), sorting, 344 rows, 5 columns,',
      working.body_mass_g.isna().sum(), 'missing masses; original unchanged')
''')
code('R', '''
working <- penguins[, c("species", "island", "flipper_length_mm", "body_mass_g")]
working$body_mass_kg <- working$body_mass_g / 1000
ord <- order(working$species, -working$body_mass_g, seq_len(nrow(working)),
             na.last = TRUE, method = "radix")
working <- working[ord, , drop = FALSE]
rownames(working) <- NULL
print(head(working, 10), row.names = FALSE)
known <- !is.na(working$body_mass_g)
stopifnot(all(abs(working$body_mass_kg[known] - working$body_mass_g[known]/1000) < 1e-12),
          nrow(working) == nrow(penguins),
          sum(is.na(working$body_mass_g)) == sum(is.na(penguins$body_mass_g)),
          ncol(penguins) == 8L, ncol(working) == 5L,
          identical(working$species, sort(working$species)), identical(penguins, original))
for (sp in unique(working$species)) {
    masses <- working$body_mass_g[working$species == sp]
    stopifnot(all(diff(masses[!is.na(masses)]) <= 0),
              all(diff(as.integer(is.na(masses))) >= 0))
}
cat("PASS: conversion (tol=1e-12), sorting, 344 rows, 5 columns,",
    sum(is.na(working$body_mass_g)), "missing masses; original unchanged\\n")
''')

for lang in cells:
    md(lang, '## Part 5 - Export and verify\nExports omit row labels and write missing values as literal NA. We check dimensions, column names, types, missing values and all values, using a tolerance of 1e-12 for numerical comparisons. Separate filenames allow both languages to keep their exports in the same directory.')
code('Python', '''
def verify_restored(restored):
    print('Dimensions:', restored.shape)
    print('Types:\\n', restored.dtypes.to_string())
    print('Missing values:\\n', restored.isna().sum().to_string())
    assert restored.shape == working.shape
    assert restored.columns.tolist() == working.columns.tolist()
    assert restored.isna().equals(working.isna())
    for column in working:
        if pd.api.types.is_numeric_dtype(working[column]):
            assert pd.api.types.is_numeric_dtype(restored[column])
            assert np.allclose(working[column], restored[column],
                               rtol=0, atol=1e-12, equal_nan=True)
        else:
            pd.testing.assert_series_equal(working[column], restored[column])
    assert restored.dtypes.equals(working.dtypes)
    print('PASS: dimensions, names, types, missing values and all values')

working.to_csv('working_python.csv', index=False, na_rep='NA')
restored = pd.read_csv('working_python.csv', na_values=['NA'])
verify_restored(restored)
working.to_csv('working_python_semicolon.csv', index=False, sep=';',
               decimal=',', na_rep='NA')
restored_semicolon = pd.read_csv('working_python_semicolon.csv', sep=';',
                                 decimal=',', na_values=['NA'])
verify_restored(restored_semicolon)
''')
code('Python', '''
try:
    wrong = pd.read_csv('working_python_semicolon.csv')
    print('Incorrect import - dimensions:', wrong.shape)
    print('Columns:', wrong.columns.tolist())
    print(wrong.head(3).to_string())
    assert wrong.shape != working.shape or wrong.columns.tolist() != working.columns.tolist()
except (pd.errors.ParserError, ValueError) as error:
    print('Expected parser error:', type(error).__name__, str(error)[:250])
# The correction uses the same parameters as the successful import above.
corrected_import = pd.read_csv('working_python_semicolon.csv', sep=';',
                               decimal=',', na_values=['NA'])
verify_restored(corrected_import)
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
pd.testing.assert_frame_equal(penguins, original)
print('PASS: the source CSV and penguins object are unchanged')
print('Filter counts:', filter_counts)
''')
code('R', '''
verify_restored <- function(restored) {
    cat("Dimensions:", dim(restored), "\\n")
    print(vapply(restored, class, character(1)))
    print(colSums(is.na(restored)))
    stopifnot(identical(dim(restored), dim(working)),
              identical(names(restored), names(working)),
              identical(is.na(restored), is.na(working)))
    for (column in names(working)) {
        if (is.numeric(working[[column]])) {
            stopifnot(is.numeric(restored[[column]]))
            known <- !is.na(working[[column]])
            stopifnot(all(abs(working[[column]][known] - restored[[column]][known]) < 1e-12))
        } else {
            stopifnot(identical(working[[column]], restored[[column]]))
        }
    }
    stopifnot(identical(vapply(restored, class, character(1)),
                        vapply(working, class, character(1))))
    cat("PASS: dimensions, names, types, missing values and all values\\n")
}
write.csv(working, "working_r.csv", row.names = FALSE, na = "NA")
restored <- read.csv("working_r.csv", na.strings = "NA", stringsAsFactors = FALSE)
verify_restored(restored)
write.table(working, "working_r_semicolon.csv", sep = ";", dec = ",",
            row.names = FALSE, col.names = TRUE, na = "NA")
restored_semicolon <- read.table("working_r_semicolon.csv", header = TRUE,
    sep = ";", dec = ",", na.strings = "NA", stringsAsFactors = FALSE)
verify_restored(restored_semicolon)
''')
code('R', '''
tryCatch({
    wrong <- read.csv("working_r_semicolon.csv")
    cat("Incorrect import - dimensions:", dim(wrong), "\\n")
    print(names(wrong))
    print(head(wrong, 3))
    stopifnot(!identical(dim(wrong), dim(working)) || !identical(names(wrong), names(working)))
}, error = function(e) cat("Expected import error:", conditionMessage(e), "\\n"))
# Corrected import with the matching separator and decimal comma.
corrected_import <- read.table("working_r_semicolon.csv", header = TRUE,
    sep = ";", dec = ",", na.strings = "NA", stringsAsFactors = FALSE)
verify_restored(corrected_import)
stopifnot(identical(unname(tools::md5sum(source_file)), source_hash),
          identical(penguins, original))
cat("PASS: the source CSV and penguins object are unchanged\\n")
cat("Filter counts:", filter_counts, "\\n")
''')
for lang in cells:
    md(lang, '''### CSV interpretation and submission preparation
The default comma-separated parser does not recognize semicolons and mistakes decimal commas for separators. This produces an incorrect table or a parser error; expected errors are handled so execution can continue. The correction uses sep=";" and decimal="," in Python, or dec="," in R.
CSV preserves textual representations of values, column names and row/column order. It does not preserve data types, units, categories/factors, index/row labels or notebook metadata. In these exports, missing values are recognized using the agreed NA string. Other datasets may need to distinguish literal text "NA" from a missing value. Types are inferred again and must be verified or specified explicitly.
Python/R comparison: both versions have 344 x 8 in the source and 344 x 5 in working, identical filters, preserved missing values and equal values after both exports. Python uses Series/DataFrame; R uses vector/data.frame and drop=FALSE. R additionally demonstrates how indexing with an NA mask differs from subset().
The notebooks and PDFs were generated from code executed in fresh local processes. To complete the required Colab step, open each notebook, select the Python 3 / R runtime, upload penguins.csv, restart the session and run all cells. Then export the report to PDF again if needed. The ZIP contains exactly two PDF reports; CSV files remain in the working directory.
''')

def execute_python():
    import os
    os.chdir(ROOT)
    namespace = {'__name__': '__main__'}
    count = 0
    for cell in cells['Python']:
        if cell['cell_type'] == 'code':
            count += 1
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                exec(compile(cell['source'], f'<Python cell {count}>', 'exec'), namespace)
            cell['execution_count'] = count
            cell['outputs'] = [{'output_type': 'stream', 'name': 'stdout', 'text': stream.getvalue()}]
    return namespace['filter_counts']

def execute_r():
    script = []
    count = 0
    for cell in cells['R']:
        if cell['cell_type'] != 'code':
            continue
        count += 1
        target = TMP / f'r_cell_{count}.txt'
        # source(..., local=.GlobalEnv) preserves objects across consecutive cells.
        src = TMP / f'r_cell_{count}.R'
        src.write_text(cell['source'] + '\n', encoding='utf-8')
        script.append(f'capture.output(source({json.dumps(src.as_posix())}, local=.GlobalEnv), '
                      f'file={json.dumps(target.as_posix())})')
        cell['execution_count'] = count
    script.append(f'writeLines(paste(filter_counts, collapse=","), '
                  f'{json.dumps((TMP / "r_counts.txt").as_posix())})')
    driver = TMP / 'execute_r.R'
    driver.write_text('\n'.join(script), encoding='utf-8')
    run = subprocess.run([str(R_SCRIPT), '--vanilla', str(driver)], cwd=ROOT,
                         capture_output=True, text=True)
    if run.returncode:
        raise RuntimeError(run.stdout + run.stderr)
    for cell in cells['R']:
        if cell['cell_type'] == 'code':
            output = (TMP / f'r_cell_{cell["execution_count"]}.txt').read_text(encoding='utf-8')
            cell['outputs'] = [{'output_type': 'stream', 'name': 'stdout', 'text': output}]
    return [int(x) for x in (TMP / 'r_counts.txt').read_text().strip().split(',')]

def render_pdf(lang):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from xml.sax.saxutils import escape
    pdfmetrics.registerFont(TTFont('CodeFont', 'C:/Windows/Fonts/consola.ttf'))
    pdfmetrics.registerFont(TTFont('BodyFont', 'C:/Windows/Fonts/arial.ttf'))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('BodyCustom', fontName='BodyFont', fontSize=9, leading=12,
                              spaceAfter=7, alignment=TA_LEFT))
    mono = ParagraphStyle('Mono', fontName='CodeFont', fontSize=7.3, leading=9.4,
                          spaceAfter=0, textColor=colors.HexColor('#162535'))
    output_style = ParagraphStyle('Output', parent=mono, textColor=colors.HexColor('#164537'),
                                  backColor=colors.HexColor('#f1f6f3'), borderPadding=1)
    story = []
    for cell in cells[lang]:
        if cell['cell_type'] == 'markdown':
            for line in cell['source'].split('\n'):
                if not line.strip():
                    continue
                if line.startswith('# '):
                    story.append(Paragraph(escape(line[2:]), styles['Title']))
                elif line.startswith('## '):
                    story.append(Spacer(1, 10))
                    story.append(Paragraph(escape(line[3:]), styles['Heading2']))
                elif line.startswith('### '):
                    story.append(Paragraph(escape(line[4:]), styles['Heading3']))
                else:
                    story.append(Paragraph(escape(line), styles['BodyCustom']))
        else:
            story.append(Paragraph(f'Executed cell {cell["execution_count"]}', styles['Heading4']))
            # Split long lines visually only; notebook source remains unchanged.
            for line in cell['source'].splitlines():
                for wrapped in textwrap.wrap(line, width=100, replace_whitespace=False,
                                             drop_whitespace=False) or [' ']:
                    story.append(Preformatted(wrapped, mono))
            story.append(Paragraph('Output', styles['Heading4']))
            for line in cell['outputs'][0]['text'].splitlines():
                for wrapped in textwrap.wrap(line, width=100, replace_whitespace=False,
                                             drop_whitespace=False) or [' ']:
                    story.append(Preformatted(wrapped, output_style))
            story.append(Spacer(1, 8))
    target = ROOT / f'Radimsky {lang}.pdf'
    def footer(canvas, doc):
        canvas.setFont('BodyFont', 8)
        canvas.setFillColor(colors.HexColor('#536170'))
        canvas.drawString(38, 22, f'Radimsky | Lab02 | {lang} | notebook outputs')
        canvas.drawRightString(557, 22, str(doc.page))
    doc = SimpleDocTemplate(str(target), pagesize=(595.28, 841.89),
                            rightMargin=38, leftMargin=38, topMargin=36, bottomMargin=38,
                            title=f'Radimsky - Penguins - {lang}', author='Radimsky')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return target

if __name__ == '__main__':
    before = hashlib.sha256((ROOT / 'penguins.csv').read_bytes()).hexdigest()
    py_counts = execute_python()
    r_counts = execute_r()
    assert py_counts == r_counts, (py_counts, r_counts)
    import pandas as pd
    py_data = pd.read_csv(ROOT / 'working_python.csv')
    r_data = pd.read_csv(ROOT / 'working_r.csv')
    pd.testing.assert_frame_equal(py_data, r_data, rtol=0, atol=1e-12)
    for lang in cells:
        md(lang, f'### Cross-language verification\nPASS: actual filter counts in both languages: {py_counts}. Automated comparison of Python/R exports verified all 344 rows and 5 columns, order, missing values and values (atol=1e-12).')
        notebook = {'cells': cells[lang], 'nbformat': 4, 'nbformat_minor': 5,
                    'metadata': {'kernelspec': {'display_name': 'Python 3' if lang == 'Python' else 'R',
                                               'language': 'python' if lang == 'Python' else 'R',
                                               'name': 'python3' if lang == 'Python' else 'ir'},
                                 'language_info': {'name': 'python' if lang == 'Python' else 'R'},
                                 'colab': {'name': f'Radimsky {lang}.ipynb'}}}
        for i, cell in enumerate(notebook['cells']):
            cell['id'] = f'{lang.lower()}-{i:02d}'
        (ROOT / f'Radimsky {lang}.ipynb').write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding='utf-8')
        suffix = 'py' if lang == 'Python' else 'R'
        (ROOT / f'Radimsky_{lang}.{suffix}').write_text('\n\n'.join(
            c['source'] for c in cells[lang] if c['cell_type'] == 'code') + '\n', encoding='utf-8')
        render_pdf(lang)
    archive = ROOT / 'Radimsky Lab02.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for lang in cells:
            target = ROOT / f'Radimsky {lang}.pdf'
            z.write(target, target.name)
    assert hashlib.sha256((ROOT / 'penguins.csv').read_bytes()).hexdigest() == before
    (ROOT / 'README_Lab02.md').write_text(
        '# Radimsky - Lab02\n\n'
        'The ZIP contains exactly two PDF reports. The source penguins.csv was not modified.\n\n'
        'Both notebooks were executed sequentially in fresh local processes; '
        'Python and R exports were compared automatically.\n\n'
        'To complete the required Colab step, upload each ipynb to Colab, '
        'select the Python 3 / R runtime and upload penguins.csv. '
        'Restart the session, run all cells, inspect the outputs and export to PDF.\n\n'
        f'Filter counts F1/F2/F3: {py_counts}.\n'
        f'SHA256 of the unchanged source: {before}.\n', encoding='utf-8')
    print('PASS: both languages executed, cross-language values match, source unchanged')
    print('Filter counts:', py_counts)
    print('Archive:', archive)
