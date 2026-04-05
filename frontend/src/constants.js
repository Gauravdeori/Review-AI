// ── Language options ──────────────────────────────────────────────────────────
export const LANGUAGES = ["JavaScript", "Python", "C++"];

// ── Difficulty levels ─────────────────────────────────────────────────────────
export const DIFFICULTY_LEVELS = [
  { id: "easy",   label: "Easy",   desc: "Syntax only",     color: "#4ade80" },
  { id: "medium", label: "Medium", desc: "+ Logic bugs",    color: "#facc15" },
  { id: "hard",   label: "Hard",   desc: "+ Optimizations", color: "#f87171" },
];

// ── Pre-loaded sample code with intentional bugs ─────────────────────────────
export const SAMPLE_CODE = {
  JavaScript: `function calculateSum(arr) {
  let total = 0;
  for (let i = 0; i < arr.length; i++) {
    total += arr[i];
  }
  return total;
}

function findDuplicate(arr) {
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) return true
    }
  }
  return false
}

console.log(calculateSum([1, 2, 3, 4, 5]));`,

  Python: `def calculate_sum(arr):
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total

def find_max(arr):
    if not arr: return None
    max_val = arr[0]
    for x in arr:
        if x > max_val:
            max_val = x
    return max_val

def is_palindrome(s):
    for i in range(len(s) // 2):
        if s[i] != s[len(s) - 1 - i]:
            return False
    return True`,

  "C++": `#include <iostream>
using namespace std;

int calculateSum(int arr[], int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += arr[i];
    }
    return total;
}

int findMax(int arr[], int n) {
    if (n <= 0) return -1;
    int max = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > max) max = arr[i];
    }
    return max;
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    cout << calculateSum(arr, 5) << endl;
    return 0;
}`,
};

// ── Helpers ───────────────────────────────────────────────────────────────────
export const severityColor = (s) =>
  ({ critical: "#f87171", warning: "#facc15", info: "#60a5fa" }[s] || "#aaa");

export const typeIcon = (t) =>
  ({ syntax: "⚠", logic: "🔁", performance: "⚡", style: "🎨" }[t] || "•");
