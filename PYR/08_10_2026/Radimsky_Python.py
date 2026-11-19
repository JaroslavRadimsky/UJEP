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
print('Types:\n', penguins.dtypes.to_string())
print('Missing values:\n', penguins.isna().sum().to_string())
assert penguins.shape == (344, 8)
print('PASS: 344 rows, 8 columns')

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
print('Selection by labels:\n', small.loc[['p02', 'p05']].to_string())
reverse = small.iloc[::-1]
print('Reversed table:\n', reverse.to_string())
print('First row by position:\n', reverse.iloc[[0]].to_string())
print('p01 by label:\n', reverse.loc[['p01']].to_string())
assert reverse.index[0] == 'p06'
assert reverse.loc[['p01']].equals(small.loc[['p01']])
print('PASS: dimensions, unique labels and selections')

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

def verify_restored(restored):
    print('Dimensions:', restored.shape)
    print('Types:\n', restored.dtypes.to_string())
    print('Missing values:\n', restored.isna().sum().to_string())
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
