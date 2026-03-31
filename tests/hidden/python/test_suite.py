# --- HIDDEN TESTS ---
import pytest

def test_calculate_sum():
    if "calculate_sum" in globals():
        assert calculate_sum([1, 2, 3, 4, 5]) == 15
        assert calculate_sum([-1, -2, -3]) == -6
        assert calculate_sum([]) == 0

def test_find_max():
    if "find_max" in globals():
        assert find_max([1, 2, 3]) == 3
        assert find_max([-1, -5, -3]) == -1

def test_is_palindrome():
    if "is_palindrome" in globals():
        assert is_palindrome("racecar") == True
        assert is_palindrome("hello") == False
