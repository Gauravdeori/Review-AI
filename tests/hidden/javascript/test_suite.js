// --- HIDDEN TESTS ---
test('calculateSum operates correctly on arrays', () => {
  if (typeof calculateSum !== 'undefined') {
    expect(calculateSum([1, 2, 3, 4, 5])).toBe(15);
    expect(calculateSum([-1, -2, -3])).toBe(-6);
    expect(calculateSum([])).toBe(0);
  }
});

test('findDuplicate correctly identifies duplicates', () => {
  if (typeof findDuplicate !== 'undefined') {
    expect(findDuplicate([1, 2, 3, 4, 1])).toBe(true);
    expect(findDuplicate([1, 2, 3, 4])).toBe(false);
  }
});
