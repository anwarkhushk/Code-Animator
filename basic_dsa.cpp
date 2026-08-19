#include <iostream>
#include <vector>

using namespace std;

// === 1. Binary Search Tree (BST) ===
struct TreeNode {
    int data;
    TreeNode* left;
    TreeNode* right;

    TreeNode(int value) : data(value), left(nullptr), right(nullptr) {}
};

class BST {
private:
    TreeNode* root;

    TreeNode* insertRecursive(TreeNode* current, int value) {
        if (current == nullptr) {
            return new TreeNode(value);
        }

        if (value < current->data) {
            current->left = insertRecursive(current->left, value);
        } else if (value > current->data) {
            current->right = insertRecursive(current->right, value);
        }

        return current;
    }

    bool searchRecursive(TreeNode* current, int value) {
        if (current == nullptr) return false;
        if (current->data == value) return true;

        if (value < current->data) {
            return searchRecursive(current->left, value);
        } else {
            return searchRecursive(current->right, value);
        }
    }

    void inorderRecursive(TreeNode* current) {
        if (current != nullptr) {
            inorderRecursive(current->left);
            cout << current->data << " ";
            inorderRecursive(current->right);
        }
    }

public:
    BST() : root(nullptr) {}

    void insert(int value) {
        root = insertRecursive(root, value);
    }

    bool search(int value) {
        return searchRecursive(root, value);
    }

    void inorderTraversal() {
        inorderRecursive(root);
        cout << endl;
    }
};

// === 2. QuickSort Algorithm ===
int partition(vector<int>& arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;

    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}

void quickSort(vector<int>& arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);

        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}

// === Main Execution ===
int main() {
    cout << "--- Basic DSA Examples ---\n\n";

    // Testing BST
    cout << "1. Binary Search Tree Test\n";
    BST tree;
    tree.insert(50);
    tree.insert(30);
    tree.insert(20);
    tree.insert(40);
    tree.insert(70);
    tree.insert(60);
    tree.insert(80);

    cout << "Inorder Traversal: ";
    tree.inorderTraversal();

    int searchValue = 60;
    cout << "Searching for " << searchValue << ": " 
         << (tree.search(searchValue) ? "Found" : "Not Found") << "\n\n";


    // Testing QuickSort
    cout << "2. QuickSort Algorithm Test\n";
    vector<int> numbers = {64, 25, 12, 22, 11, 90, 88};
    
    cout << "Original Array: ";
    for (int num : numbers) cout << num << " ";
    cout << endl;

    quickSort(numbers, 0, numbers.size() - 1);

    cout << "Sorted Array: ";
    for (int num : numbers) cout << num << " ";
    cout << endl;

    return 0;
}
